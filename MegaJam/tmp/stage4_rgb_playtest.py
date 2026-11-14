import asyncio
import base64
import json
import re
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


LEVEL = "/Game/DirectorCut/Stage/Stage4"
SCENE = "editor_toolset.toolsets.scene.SceneTools"
OBJECT = "editor_toolset.toolsets.object.ObjectTools"
ACTOR = "editor_toolset.toolsets.actor.ActorTools"
ASSETS = "editor_toolset.toolsets.asset.AssetTools"
SLATE = "SlateInspectorToolset.SlateInspectorToolset"
APP = "EditorToolset.EditorAppToolset"


async def run():
    async with streamable_http_client("http://127.0.0.1:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            async def call(toolset, name, args=None):
                reply = await session.call_tool("call_tool", {
                    "toolset_name": toolset, "tool_name": name, "arguments": args or {},
                })
                if reply.isError:
                    raise RuntimeError(f"{name}: {reply.content}")
                return json.loads(reply.content[0].text)["returnValue"]

            async def find(name):
                actors = await call(SCENE, "find_actors", {"name": name, "tag": "", "collision_channels": []})
                assert len(actors) == 1, (name, actors)
                return actors[0]

            async def props(actor, *names):
                return json.loads(await call(OBJECT, "get_properties", {"instance": actor, "properties": names}))

            async def key(value):
                await call(SLATE, "PressKey", {"key": value})
                await asyncio.sleep(0.19)

            async def capture(name):
                image = await call(APP, "CaptureEditorImage")
                path = Path("tmp/stage4_rgb_qa")
                path.mkdir(exist_ok=True, parents=True)
                (path / f"{name}.png").write_bytes(base64.b64decode(image["data"]))

            assert not await call(APP, "IsPIERunning")
            if not (await find("WorldSettings"))["refPath"].startswith(LEVEL + ".Stage4:"):
                await call(SCENE, "load_level", {"level_path": LEVEL})
            controller = await find("Color_Controller")
            assert controller["refPath"].startswith(LEVEL + ".Stage4:")
            if not (await props(controller, "bUseRgbCalibration"))["bUseRgbCalibration"]:
                assert await call(OBJECT, "set_properties", {
                    "instance": controller, "values": json.dumps({"bUseRgbCalibration": True}),
                })
            sign = {"refPath": LEVEL + ".Stage4:PersistentLevel.TextRenderActor_0"}
            components = await call(ACTOR, "get_components", {"actor": sign})
            text = next(a for a in components if "TextRender" in a["refPath"])
            if (await props(text, "text"))["text"] != "E : RGB LIGHT PANEL":
                assert await call(OBJECT, "set_properties", {
                    "instance": text, "values": json.dumps({"text": "E : RGB LIGHT PANEL"}),
                })
                assert await call(ASSETS, "save_assets", {"asset_paths": [LEVEL]})
            print("Stage4 RGB saved", await props(controller, "bUseRgbCalibration", "exitDoor"), flush=True)

            await call(APP, "StartPIE", {"options": {
                "bSimulate": False, "playMode": "PlayMode_InViewPort", "warmupSeconds": 1,
            }})
            try:
                color = await find("Color_Controller")
                door = await find("Color_ExitDoor")
                await call(SLATE, "Observe", {"ref": "w1", "maxDepth": 40})
                await call(SLATE, "Snapshot", {"ref": "w1", "maxDepth": 40})
                await call(SLATE, "Click", {"ref": "sp6"})
                await key("E")
                assert (await props(color, "bActive", "dialValues")) == {"bActive": True, "dialValues": [0, 0, 0]}
                await capture("rgb-start")
                snapshot = await call(SLATE, "Snapshot", {"ref": "w1", "maxDepth": 100})
                assert "Vault Light Console" in snapshot and "VAULT LOCKED" in snapshot
                assert "Blue leads. Red is one step above green. No channel is dark." in snapshot
                assert all(word not in snapshot for word in ('"TARGET"', "TARGET MIX", "MATCHED"))
                assert not any(word in snapshot for word in ("조명 맞추기", "혼합색", "나가기"))
                steps = re.findall(r'button "STEP".*?\[ref=(b\d+)\]', snapshot)
                assert len(steps) == 3, [line for line in snapshot.splitlines() if "STEP" in line]
                assert await call(SLATE, "Click", {"ref": steps[0]})
                await asyncio.sleep(.25)
                assert (await props(color, "dialValues"))["dialValues"] == [1, 0, 0]
                await key("R")
                for _ in range(4):
                    await key("One")
                assert (await props(color, "dialValues"))["dialValues"] == [0, 0, 0]
                await key("One")
                await key("Two")
                await key("E")
                assert not (await props(color, "bActive"))["bActive"]
                await key("E")
                assert (await props(color, "dialValues"))["dialValues"] == [1, 1, 0]
                await key("R")
                assert (await props(color, "dialValues"))["dialValues"] == [0, 0, 0]
                for button in ["One", "One", "Two", "Three", "Three"]:
                    await key(button)
                assert (await props(color, "bSolved", "dialValues")) == {"bSolved": False, "dialValues": [2, 1, 2]}
                assert not (await props(door, "bOpen"))["bOpen"]
                await capture("rgb-progress")
                await key("Three")
                assert (await props(color, "bSolved", "dialValues")) == {"bSolved": True, "dialValues": [2, 1, 3]}
                await capture("rgb-solved")
                await asyncio.sleep(2.8)
                assert (await props(door, "bOpen"))["bOpen"]
                assert not (await props(color, "bActive"))["bActive"]
                print("PASSED: independent RGB channels, wrap, leave, reset, automatic completion, door", flush=True)
            finally:
                await call(APP, "StopPIE")


asyncio.run(run())
