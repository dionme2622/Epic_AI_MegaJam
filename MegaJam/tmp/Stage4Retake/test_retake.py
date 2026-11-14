import asyncio, base64, json, re
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

APP="EditorToolset.EditorAppToolset"
SLATE="SlateInspectorToolset.SlateInspectorToolset"
SCENE="editor_toolset.toolsets.scene.SceneTools"
ACTOR="editor_toolset.toolsets.actor.ActorTools"
OBJECT="editor_toolset.toolsets.object.ObjectTools"
OUT=Path("tmp/Stage4Retake")

async def run():
    async with streamable_http_client("http://127.0.0.1:18765/mcp") as (r,w,_):
        async with ClientSession(r,w) as session:
            await session.initialize()
            async def c(t,n,args=None):
                p=await session.call_tool("call_tool",{"toolset_name":t,"tool_name":n,"arguments":args or {}})
                if p.isError: raise RuntimeError((n,p.content))
                return json.loads(p.content[0].text)["returnValue"]
            async def find(label):
                return (await c(SCENE,"find_actors",{"name":label,"tag":"","collision_channels":[]}))[0]
            async def props(a,*keys):
                return json.loads(await c(OBJECT,"get_properties",{"instance":a,"properties":list(keys)}))
            async def snapshot():
                return await c(SLATE,"Snapshot",{"ref":"w1","maxDepth":100})
            async def key(k):
                assert await c(SLATE,"PressKey",{"key":k})
                await asyncio.sleep(.55 if k in ("Q","R") else .35)
            async def move(x,z=58):
                assert await c(ACTOR,"set_actor_transform",{"actor":pawn,"xform":{"location":{"x":1670+x,"y":0,"z":z}}})
                await asyncio.sleep(.65)
            async def screen(name):
                art=await c(APP,"CaptureEditorImage")
                (OUT/(name+".png")).write_bytes(base64.b64decode(art["data"]))
            async def pos(index):
                owner=await find(f"Retake_Deck_{index:02}")
                return (await c(ACTOR,"get_actor_transform",{"actor":owner}))["location"]["y"]
            async def mode(low):
                ss=await snapshot()
                gear=re.search(r'button "⚙".*?\[ref=(b\d+)\]',ss)
                assert gear,"settings icon"
                for attempt in range(4):
                    await c(SLATE,"Click",{"ref":gear[1]})
                    await asyncio.sleep(.45)
                    ss=await snapshot()
                    if 'text "그림자"' in ss:
                        break
                section=ss[ss.index('text "그림자"'):]
                which="낮음" if low else "높음"
                option=re.search(rf'button "{which}".*?\[ref=(b\d+)\]',section)
                close=re.search(r'button "닫기".*?\[ref=(b\d+)\]',section)
                assert option and close, section[:2300]
                await c(SLATE,"Click",{"ref":option[1]})
                await c(SLATE,"Click",{"ref":close[1]})
                await asyncio.sleep(.4)
            assert not await c(APP,"IsPIERunning")
            await c(APP,"StartPIE",{"options":{"bSimulate":False,"playMode":"PlayMode_InViewPort","warmupSeconds":1}})
            try:
                pawn=await find("DirectorCutDragon")
                manager=await find("Shadow Rehearsal")
                door=await find("Color_ExitDoor")
                cfg=await props(manager,"WestLamp","EastLamp","DeckScenery","DeckCollision","PreviewMaterial")
                assert cfg["WestLamp"] and cfg["EastLamp"] and cfg["PreviewMaterial"]
                assert len(cfg["DeckScenery"])==len(cfg["DeckCollision"])==9
                await c(SLATE,"Observe",{"ref":"w1","maxDepth":100})
                await snapshot()
                await c(SLATE,"Click",{"ref":"sp6"})
                for k in ["E","One","One","Two","Three","Three","Three"]:
                    await key(k)
                await asyncio.sleep(2.6)
                assert (await props(door,"bOpen"))["bOpen"]
                await move(220)
                await asyncio.sleep(.7)
                assert "SHADOW RETAKE" in await snapshot()
                assert await pos(2)<-400
                await key("E")
                assert (await props(manager,"WestCut"))["WestCut"]==-1
                await key("Q")
                await screen("retake-preview")
                await key("R")
                assert (await props(manager,"WestCut"))["WestCut"]==-1 and await pos(4)<-400
                await key("E")
                await asyncio.sleep(.48)
                assert (await props(manager,"WestCut"))["WestCut"]==1
                assert await pos(2)<-400 and abs(await pos(4))<1
                await key("Q")
                assert abs(await pos(4))<1 and await pos(2)<-400
                await key("E")
                await asyncio.sleep(.55)
                assert (await props(manager,"WestCut"))["WestCut"]==0 and abs(await pos(2))<1
                await screen("retake-cut")
                await mode(True)
                await key("R")
                await key("E")
                assert (await props(manager,"WestCut"))["WestCut"]==0
                assert "Turn Shadows High" in await snapshot()
                await screen("retake-work-lights")
                await mode(False)
                await move(1370)
                assert (await props(manager,"Checkpoint"))["Checkpoint"]==1
                await key("E")
                await asyncio.sleep(.6)
                assert (await props(manager,"EastCut"))["EastCut"]==0
                assert abs(await pos(6))<1 and await pos(8)<-400
                await move(2000,78)
                await key("R")
                assert abs(await pos(6))<1 and await pos(8)<-400
                await key("E")
                await asyncio.sleep(.6)
                assert (await props(manager,"EastCut"))["EastCut"]==1
                assert await pos(6)<-400 and abs(await pos(8))<1
                await screen("retake-island-cut")
                await move(2380,-185)
                st=await props(manager,"Checkpoint","ResetCount","EastCut")
                assert st["Checkpoint"]==1 and st["ResetCount"]>=1 and st["EastCut"]==1,st
                loc=await c(ACTOR,"get_actor_transform",{"actor":pawn})
                assert abs(loc["location"]["x"]-3040)<18,loc
                await move(2878)
                await key("E")
                assert (await props(manager,"bRecovered"))["bRecovered"]
                await asyncio.sleep(2.35)
                assert "Original legs restored" in await snapshot()
                print("PASS: Gate, staged collision geometry, distinct angles, cut lock, Shadows Low, island change, retry retains cut and leg recovery",flush=True)
            finally:
                if await c(APP,"IsPIERunning"):
                    await c(APP,"StopPIE")
asyncio.run(run())

