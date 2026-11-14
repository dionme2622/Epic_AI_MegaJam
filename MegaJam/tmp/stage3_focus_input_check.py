import asyncio
import json
import re

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def run():
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
                found = await call(scene, "find_actors", {"name": name, "tag": "", "collision_channels": []})
                assert len(found) == 1, (name, found)
                return found[0]

            async def props(target, *names):
                value = await call(obj, "get_properties", {"instance": target, "properties": list(names)})
                return json.loads(value)

            async def snapshot():
                return await call(slate, "Snapshot", {"ref": "w1", "maxDepth": 100})

            async def key(name):
                await call(slate, "PressKey", {"key": name})
                await asyncio.sleep(.35)

            assert not await call(app, "IsPIERunning")
            world = await find("WorldSettings")
            assert "/Game/DirectorCut/Stage/Stage3_.Stage3_:" in world["refPath"]
            await call(app, "StartPIE", {"options": {
                "bSimulate": False, "playMode": "PlayMode_InViewPort", "warmupSeconds": 1,
            }})
            try:
                focus = await find("Focus_Controller")
                pawn = await find("DirectorCutDragon")
                await call(slate, "Observe", {"ref": "w1", "maxDepth": 100})
                await snapshot()
                await call(slate, "Click", {"ref": "sp6"})
                await asyncio.sleep(7)
                x = (await call(actor, "get_actor_transform", {"actor": focus}))["location"]["x"]
                await call(actor, "set_actor_transform", {
                    "actor": pawn, "xform": {"location": {"x": x, "y": 0, "z": 58}},
                })
                await asyncio.sleep(.75)
                await key("E")
                initial = await props(focus, "bActive", "bNearSelected")
                assert initial == {"bActive": True, "bNearSelected": True}, initial
                ss = await snapshot()
                gear = re.search(r'button "⚙".*?\[ref=(b\d+)\]', ss)
                assert gear
                await call(slate, "Click", {"ref": gear[1]})
                await asyncio.sleep(.5)
                ss = await snapshot()
                assert 'text "해상도"' in ss
                await key("Two")
                state = await props(focus, "bActive", "bNearSelected")
                assert state == initial, (initial, state)
                close = re.search(r'button "닫기".*?\[ref=(b\d+)\]', ss)
                assert close
                await call(slate, "Click", {"ref": close[1]})
                await asyncio.sleep(.45)
                await call(slate, "Click", {"ref": "sp6"})
                await key("Two")
                assert not (await props(focus, "bNearSelected"))["bNearSelected"]
                await key("One")
                assert (await props(focus, "bNearSelected"))["bNearSelected"]
                for name, piece_x, piece_y in [("NearPiece", 450, 200), ("FarPiece", 500, -200)]:
                    await call(obj, "set_properties", {
                        "instance": {"refPath": focus["refPath"] + "." + name},
                        "values": json.dumps({"relativeLocation": {"x": piece_x, "y": piece_y, "z": 300}}),
                    })
                await key("Enter")
                await asyncio.sleep(2)
                solved = await props(focus, "bSolved", "exitDoor")
                assert solved["bSolved"]
                assert (await props(solved["exitDoor"], "bOpen"))["bOpen"]
                print("PASS: settings block puzzle input; closed settings accept 1/2; aligned key opens door", flush=True)
            finally:
                if await call(app, "IsPIERunning"):
                    await call(app, "StopPIE")


asyncio.run(run())
