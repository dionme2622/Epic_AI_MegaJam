import asyncio
import base64
import json
import re
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def run():
    output = Path("tmp/stage3_resolution_check")
    output.mkdir(parents=True, exist_ok=True)
    async with streamable_http_client("http://127.0.0.1:18765/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            async def call(toolset, name, arguments=None):
                result = await session.call_tool("call_tool", {
                    "toolset_name": toolset, "tool_name": name, "arguments": arguments or {},
                })
                if result.isError:
                    raise RuntimeError((name, result.content))
                return json.loads(result.content[0].text)["returnValue"]

            app = "EditorToolset.EditorAppToolset"
            slate = "SlateInspectorToolset.SlateInspectorToolset"
            scene = "editor_toolset.toolsets.scene.SceneTools"
            obj = "editor_toolset.toolsets.object.ObjectTools"
            actor = "editor_toolset.toolsets.actor.ActorTools"

            async def find(name):
                matches = await call(scene, "find_actors", {"name": name, "tag": "", "collision_channels": []})
                if len(matches) != 1:
                    raise RuntimeError((name, matches))
                return matches[0]

            async def props(target, *names):
                return json.loads(await call(obj, "get_properties", {"instance": target, "properties": list(names)}))

            async def key(k):
                await call(slate, "PressKey", {"key": k})
                await asyncio.sleep(.35)

            async def snapshot():
                return await call(slate, "Snapshot", {"ref": "w1", "maxDepth": 100})

            async def picture(name):
                data = await call(app, "CaptureEditorImage")
                (output / f"{name}.png").write_bytes(base64.b64decode(data["data"]))

            async def change_resolution(low):
                ss = await snapshot()
                gear = re.search(r'button "⚙".*?\[ref=(b\d+)\]', ss)
                assert gear, "Settings button missing"
                for _ in range(4):
                    await call(slate, "Click", {"ref": gear[1]})
                    await asyncio.sleep(.35)
                    ss = await snapshot()
                    if 'text "해상도"' in ss:
                        break
                section = ss[ss.index('text "해상도"'):]
                button = re.search(r'button "' + ("낮음" if low else "높음") + r'".*?\[ref=(b\d+)\]', section)
                close = re.search(r'button "닫기".*?\[ref=(b\d+)\]', section)
                assert button and close
                await call(slate, "Click", {"ref": button[1]})
                await asyncio.sleep(.4)
                await call(slate, "Click", {"ref": close[1]})
                await asyncio.sleep(.5)

            async def move(x, z=58):
                await call(actor, "set_actor_transform", {
                    "actor": pawn, "xform": {"location": {"x": x, "y": 0, "z": z}},
                })
                await asyncio.sleep(.75)

            assert not await call(app, "IsPIERunning")
            world = await find("WorldSettings")
            assert "/Game/DirectorCut/Stage/Stage3_.Stage3_:" in world["refPath"], world
            await call(app, "StartPIE", {"options": {
                "bSimulate": False, "playMode": "PlayMode_InViewPort", "warmupSeconds": 1,
            }})
            try:
                pawn = await find("DirectorCutDragon")
                focus = await find("Focus_Controller")
                controller = await find("Resolution_Controller")
                setup = await props(controller, "bUseStationChoices", "stationAnswers", "stationCheckpointOffsets", "guidanceArrows")
                print("SETUP", setup, flush=True)
                origin = (await call(actor, "get_actor_transform", {"actor": controller}))["location"]["x"]
                guides = setup["guidanceArrows"]
                await call(slate, "Observe", {"ref": "w1", "maxDepth": 100})
                await snapshot()
                await call(slate, "Click", {"ref": "sp6"})
                await move(origin + 210)
                await change_resolution(False)
                print("HIGH", [await props(g, "bHidden") for g in guides], flush=True)
                await picture("high")
                await change_resolution(True)
                print("LOW", [await props(g, "bHidden") for g in guides], flush=True)
                await picture("low")
                await key("Two")
                await key("E")
                await asyncio.sleep(1.5)
                assert (await props(controller, "progress"))["progress"] == 0
                for index, (choice, tile) in enumerate(zip(["One", "Two", "Three"], [400, 720, 1040])):
                    await picture(f"station_{index + 1}")
                    await key(choice)
                    assert (await props(controller, "selectedChoice"))["selectedChoice"] == index + 1
                    await key("E")
                    assert (await props(controller, "bChoiceConfirmed"))["bChoiceConfirmed"]
                    await move(origin + tile)
                    state = await props(controller, "progress", "bCompleted")
                    print("STEP", index + 1, state, flush=True)
                    assert state["progress"] == index + 1
                    if index == 0:
                        await key("One")
                        await key("E")
                        await asyncio.sleep(1.5)
                        assert (await props(controller, "progress"))["progress"] == 1
                assert (await props(controller, "bCompleted"))["bCompleted"]
                print("PASS: high/low marker state, incorrect answer retry, preserved progress, 3 successful tiles", flush=True)
            finally:
                if await call(app, "IsPIERunning"):
                    await call(app, "StopPIE")


asyncio.run(run())
