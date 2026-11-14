import argparse
import asyncio
import base64
import json
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


LEVEL = "/Game/DirectorCut/Stage/Stage4"
SCENE = "editor_toolset.toolsets.scene.SceneTools"
OBJECT = "editor_toolset.toolsets.object.ObjectTools"
ASSETS = "editor_toolset.toolsets.asset.AssetTools"
SLATE = "SlateInspectorToolset.SlateInspectorToolset"
APP = "EditorToolset.EditorAppToolset"
ARTIFACTS = Path("tmp/stage4_film_qa")


async def run(install):
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
                return json.loads(await call(OBJECT, "get_properties", {
                    "instance": actor, "properties": names,
                }))

            started = await call(APP, "IsPIERunning")
            assert not started, "A play session is already running"
            world = await find("WorldSettings")
            if LEVEL not in world["refPath"]:
                await call(SCENE, "load_level", {"level_path": LEVEL})
            controller = await find("Color_Controller")
            assert controller["refPath"].startswith(LEVEL + ".Stage4:"), controller
            if install:
                result = await call(OBJECT, "set_properties", {
                    "instance": controller, "values": json.dumps({"bUseFilmSynchronization": True}),
                })
                assert result
                print("Stage4 film mode saved:",
                      await props(controller, "bUseFilmSynchronization", "exitDoor"),
                      await call(ASSETS, "save_assets", {"asset_paths": [LEVEL]}),
                      flush=True)
            assert (await props(controller, "bUseFilmSynchronization"))["bUseFilmSynchronization"]

            async def key(value, wait=0.2):
                await call(SLATE, "PressKey", {"key": value})
                await asyncio.sleep(wait)

            async def capture(name):
                image = await call(APP, "CaptureEditorImage")
                ARTIFACTS.mkdir(exist_ok=True, parents=True)
                (ARTIFACTS / (name + ".png")).write_bytes(base64.b64decode(image["data"]))

            await call(APP, "StartPIE", {"options": {
                "bSimulate": False, "playMode": "PlayMode_InViewPort", "warmupSeconds": 1,
            }})
            try:
                color = await find("Color_Controller")
                door = await find("Color_ExitDoor")
                await call(SLATE, "Observe", {"ref": "w1", "maxDepth": 40})
                snap = await call(SLATE, "Snapshot", {"ref": "w1", "maxDepth": 40})
                viewport = "/ SLevelViewport"
                matches = [line for line in snap.splitlines() if viewport in line]
                print("Viewport:", matches[:3], flush=True)
                await call(SLATE, "Click", {"ref": "sp6"})
                await key("E", 0.5)
                entry = await props(color, "bActive", "dialValues", "filterMode")
                print("ENTER", entry, flush=True)
                assert entry["bActive"] and entry["dialValues"] == [0, 0, 0, 2]
                await capture("film-overview")
                await key("SpaceBar")
                assert not (await props(color, "bSolved"))["bSolved"]
                assert (await props(color, "dialValues"))["dialValues"] == entry["dialValues"]
                assert not (await props(door, "bOpen"))["bOpen"]
                await capture("film-mismatch")

                for index, filter_name in enumerate(("red", "green", "blue"), 1):
                    await key("Q")
                    assert (await props(color, "filterMode"))["filterMode"] == index
                    await capture("film-" + filter_name)

                await key("One")
                assert (await props(color, "dialValues"))["dialValues"] == [1, 0, 0, 2]
                await key("E")
                assert not (await props(color, "bActive"))["bActive"]
                await key("E", 0.5)
                assert (await props(color, "dialValues"))["dialValues"] == [1, 0, 0, 2]
                await key("R")
                assert (await props(color, "dialValues"))["dialValues"] == entry["dialValues"]
                for value in ["One", "One", "Two", "Three", "Three", "Three", "Four", "Four"]:
                    await key(value)
                aligned = await props(color, "dialValues", "bSolved")
                print("ALIGNED", aligned, flush=True)
                assert aligned["dialValues"] == [2, 1, 3, 0] and not aligned["bSolved"]
                await key("SpaceBar")
                assert (await props(color, "bSolved"))["bSolved"]
                await asyncio.sleep(2.8)
                await capture("film-restored")
                await asyncio.sleep(2.3)
                assert (await props(door, "bOpen"))["bOpen"]
                assert not (await props(color, "bActive"))["bActive"]
                print("PASSED: filters, independent reels, retry, replay, exit door", flush=True)
            finally:
                await call(APP, "StopPIE")


parser = argparse.ArgumentParser()
parser.add_argument("--install", action="store_true")
asyncio.run(run(parser.parse_args().install))
