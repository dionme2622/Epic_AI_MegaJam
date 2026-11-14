import asyncio,base64,json,re
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def run():
    async with streamable_http_client("http://127.0.0.1:18765/mcp") as (r,w,_):
        async with ClientSession(r,w) as s:
            await s.initialize()
            async def c(t,n,args=None):
                p=await s.call_tool("call_tool",{"toolset_name":t,"tool_name":n,"arguments":args or {}})
                if p.isError: raise RuntimeError((n,p.content))
                return json.loads(p.content[0].text)["returnValue"]
            app="EditorToolset.EditorAppToolset"
            sl="SlateInspectorToolset.SlateInspectorToolset"
            obj="editor_toolset.toolsets.object.ObjectTools"
            sc="editor_toolset.toolsets.scene.SceneTools"
            act="editor_toolset.toolsets.actor.ActorTools"
            async def find(label):
                items=await c(sc,"find_actors",{"name":label,"tag":"","collision_channels":[]})
                assert items,label
                return items[0]
            async def p(a,*keys):
                return json.loads(await c(obj,"get_properties",{"instance":a,"properties":list(keys)}))
            async def move(x,z=58,wait=.7):
                await c(act,"set_actor_transform",{"actor":pawn,"xform":{"location":{"x":4930+x,"y":0,"z":z}}})
                await asyncio.sleep(wait)
            async def position(actor):
                return (await c(act,"get_actor_transform",{"actor":actor}))["location"]
            async def key(k):
                await c(sl,"PressKey",{"key":k})
                await asyncio.sleep(.25)
            async def snap():
                return await c(sl,"Snapshot",{"ref":"w1","maxDepth":100})
            async def image(n):
                data=await c(app,"CaptureEditorImage")
                Path("tmp/Stage4Lighting",n+".png").write_bytes(base64.b64decode(data["data"]))
            async def shadows(on):
                ss=await snap()
                gear=re.search(r'button "⚙".*?\[ref=(b\d+)\]',ss)
                assert gear
                for _ in range(4):
                    await c(sl,"Click",{"ref":gear[1]})
                    await asyncio.sleep(.30)
                    ss=await snap()
                    if 'text "그림자"' in ss: break
                part=ss[ss.index('text "그림자"'):]
                target=re.search(r'button "'+("높음" if on else "낮음")+r'".*?\[ref=(b\d+)\]',part)
                close=re.search(r'button "닫기".*?\[ref=(b\d+)\]',part)
                await c(sl,"Click",{"ref":target[1]})
                await asyncio.sleep(.33)
                await c(sl,"Click",{"ref":close[1]})
                await asyncio.sleep(.45)
            assert not await c(app,"IsPIERunning")
            await c(app,"StartPIE",{"options":{"bSimulate":False,"playMode":"PlayMode_InViewPort","warmupSeconds":1}})
            try:
                pawn=await find("DirectorCutDragon")
                puzzle=await find("Shadow Stand-In")
                theatre=await find("Shadow Rehearsal")
                door=await find("Color_ExitDoor")
                ferry=await find("Shadow Ferry Collision")
                bridge=await find("Switch Bridge Collision")
                assert (await p(theatre,"StandInPuzzle"))["StandInPuzzle"]
                await c(sl,"Observe",{"ref":"w1","maxDepth":100})
                await snap()
                await c(sl,"Click",{"ref":"sp6"})
                await asyncio.sleep(.6)
                await image("rgb-gallery")
                for k in ["E","One","One","Two","Three","Three","Three"]: await key(k)
                await asyncio.sleep(2.6)
                assert (await p(door,"bOpen"))["bOpen"]
                await move(-3180)
                await key("Q")
                await asyncio.sleep(.65)
                await image("shadow-retake")
                await key("E")
                await asyncio.sleep(.7)
                assert (await p(theatre,"WestCut"))["WestCut"]==0
                await move(-375)
                await key("E")
                assert not (await p(theatre,"bRecovered"))["bRecovered"]
                await move(155,wait=2.65)
                assert (await p(puzzle,"bCallSwitch"))["bCallSwitch"]
                assert abs((await position(ferry))["x"]-5263)<3
                await image("stand-in-call")
                await move(330)
                await shadows(False)
                for _ in range(6):
                    await asyncio.sleep(.55)
                    if (await position(pawn))["x"]>5650: break
                loc=await position(pawn)
                print("Ferry carried",loc,flush=True)
                assert loc["x"]>5650 and abs(loc["z"]-55)<12,loc
                await image("stand-in-ferry")
                await move(1090)
                assert (await p(puzzle,"Checkpoint"))["Checkpoint"]==1
                await move(1195,-195)
                assert abs((await position(pawn))["x"]-6030)<18
                await move(1198)
                await shadows(True)
                st=await p(puzzle,"bLowSwitch","bHighSwitch","bRaisedBridge")
                print("Low mechanism",st,await position(bridge),flush=True)
                assert st=={"bLowSwitch":True,"bHighSwitch":False,"bRaisedBridge":False},st
                await asyncio.sleep(.6)
                assert abs((await position(bridge))["z"]+10)<4
                await move(1294,132)
                st=await p(puzzle,"bHighSwitch","bRaisedBridge")
                print("High contact before retake",st,flush=True)
                assert st["bHighSwitch"] and not st["bRaisedBridge"],st
                await shadows(False)
                await shadows(True)
                assert (await p(puzzle,"bRaisedBridge"))["bRaisedBridge"]
                await asyncio.sleep(1)
                assert abs((await position(bridge))["z"]-71)<4
                await image("stand-in-bridge")
                await move(1535,144)
                assert (await p(puzzle,"bRaisedBridge"))["bRaisedBridge"]
                await move(1980,175)
                assert (await p(puzzle,"bReachedExhibit"))["bReachedExhibit"]
                await image("stand-in-exhibit")
                await key("E")
                assert (await p(theatre,"bRecovered"))["bRecovered"]
                print("PASS: calls ferry, ferries rider, lower/upper contacts, restart, raise bridge, moved exhibit",flush=True)
            finally:
                if await c(app,"IsPIERunning"): await c(app,"StopPIE")
asyncio.run(run())

