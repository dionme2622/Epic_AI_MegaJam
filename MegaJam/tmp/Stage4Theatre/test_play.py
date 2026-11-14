import asyncio, base64, json, re
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

OUT=Path("tmp/Stage4Theatre")
APP="EditorToolset.EditorAppToolset"
SLATE="SlateInspectorToolset.SlateInspectorToolset"
SCENE="editor_toolset.toolsets.scene.SceneTools"
OBJECT="editor_toolset.toolsets.object.ObjectTools"
ACTOR="editor_toolset.toolsets.actor.ActorTools"

async def run():
    async with streamable_http_client("http://127.0.0.1:18765/mcp") as (read,write,_):
        async with ClientSession(read,write) as session:
            await session.initialize()
            async def call(toolset,name,args=None):
                reply=await session.call_tool("call_tool",{"toolset_name":toolset,"tool_name":name,"arguments":args or {}})
                if reply.isError: raise RuntimeError((name, reply.content))
                return json.loads(reply.content[0].text)["returnValue"]

            async def find(name):
                actors=await call(SCENE,"find_actors",{"name":name,"tag":"","collision_channels":[]})
                assert len(actors)==1, (name,actors)
                return actors[0]

            async def props(actor,*names):
                result=await call(OBJECT,"get_properties",{"instance":actor,"properties":names})
                return json.loads(result)

            async def key(value):
                await call(SLATE,"PressKey",{"key":value})
                await asyncio.sleep(.12)

            async def snap():
                return await call(SLATE,"Snapshot",{"ref":"w1","maxDepth":100})

            async def click(pattern):
                s=await snap()
                match=re.search(pattern,s)
                assert match, s[-8000:]
                assert await call(SLATE,"Click",{"ref":match[1]})
                await asyncio.sleep(.25)

            async def capture(name):
                artwork=await call(APP,"CaptureEditorImage")
                (OUT/(name+".png")).write_bytes(base64.b64decode(artwork["data"]))

            async def move(x,z=58):
                assert await call(ACTOR,"set_actor_transform",{"actor":pawn,"xform":{"location":{"x":x+1670,"y":0,"z":z}}})
                await asyncio.sleep(.65)

            assert not await call(APP,"IsPIERunning")
            await call(APP,"StartPIE",{"options":{"bSimulate":False,"playMode":"PlayMode_InViewPort","warmupSeconds":1}})
            try:
                pawn=await find("DirectorCutDragon")
                theatre=await find("Shadow Rehearsal")
                controller=await find("Color_Controller")
                door=await find("Color_ExitDoor")
                print("actors",pawn,theatre,flush=True)
                print("theatre props",await props(theatre,"Checkpoint","bRecovered","WestRig","EntranceDoor","ResetCount"),flush=True)
                await call(SLATE,"Observe",{"ref":"w1","maxDepth":100})
                await snap()
                assert await call(SLATE,"Click",{"ref":"sp6"})
                await key("E")
                assert (await props(controller,"bActive"))["bActive"]
                for k in ["One","One","Two","Three","Three","Three"]:
                    await key(k)
                await asyncio.sleep(2.7)
                assert (await props(door,"bOpen"))["bOpen"]
                await move(225)
                await asyncio.sleep(1)
                assert "THE SHADOW REHEARSAL" in (await snap())
                await capture("play-west-shadow-on")
                await capture("play-west-shadow-on-b")
                await click(r'button "⚙".*?\[ref=(b\d+)\]')
                s=await snap()
                section=s[s.index('text "그림자"'):]
                low=re.search(r'button "낮음".*?\[ref=(b\d+)\]',section)
                close=re.search(r'button "닫기".*?\[ref=(b\d+)\]',section)
                assert low and close, section[:2200]
                await call(SLATE,"Click",{"ref":low[1]})
                await call(SLATE,"Click",{"ref":close[1]})
                await asyncio.sleep(.8)
                assert "Lit edges mark the landing platforms" in (await snap())
                await capture("play-west-shadow-off")
                await move(613,-190)
                state=await props(theatre,"Checkpoint","ResetCount")
                assert state["Checkpoint"]==0 and state["ResetCount"]>=1, state
                loc=(await call(ACTOR,"get_actor_transform",{"actor":pawn}))["location"]
                assert abs(loc["x"]-1890)<20 and loc["z"]>45,loc
                await move(1370)
                assert (await props(theatre,"Checkpoint"))["Checkpoint"]==1
                await capture("play-center")
                await move(1830,-190)
                loc=(await call(ACTOR,"get_actor_transform",{"actor":pawn}))["location"]
                assert abs(loc["x"]-3040)<20 and loc["z"]>45,loc
                await move(2875)
                assert (await props(theatre,"Checkpoint"))["Checkpoint"]==2
                await capture("play-exhibit")
                await key("E")
                assert (await props(theatre,"bRecovered"))["bRecovered"]
                await asyncio.sleep(2.5)
                assert "Original legs restored" in (await snap())
                await capture("play-recovered")
                print("PASSED: RGB linkage, shadow setting, both fall checkpoints, exhibition, retrieval",flush=True)
            finally:
                if await call(APP,"IsPIERunning"):
                    await call(APP,"StopPIE")

asyncio.run(run())

