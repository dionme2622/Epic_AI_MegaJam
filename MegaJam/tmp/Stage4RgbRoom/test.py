import asyncio,base64,json,re
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
out=Path("tmp/Stage4RgbRoom")

async def run():
    async with streamable_http_client("http://127.0.0.1:18765/mcp") as (r,w,_):
        async with ClientSession(r,w) as session:
            await session.initialize()
            async def c(t,n,a=None):
                z=await session.call_tool("call_tool",{"toolset_name":t,"tool_name":n,"arguments":a or {}})
                if z.isError: raise RuntimeError((n,z.content))
                return json.loads(z.content[0].text)["returnValue"]
            app="EditorToolset.EditorAppToolset"
            sl="SlateInspectorToolset.SlateInspectorToolset"
            sc="editor_toolset.toolsets.scene.SceneTools"
            ac="editor_toolset.toolsets.actor.ActorTools"
            ob="editor_toolset.toolsets.object.ObjectTools"
            async def find(name):
                rows=await c(sc,"find_actors",{"name":name,"tag":"","collision_channels":[]})
                assert len(rows)==1,(name,rows)
                return rows[0]
            async def props(a,*names):
                return json.loads(await c(ob,"get_properties",{"instance":a,"properties":names}))
            async def screen(name):
                im=await c(app,"CaptureEditorImage")
                (out/(name+".png")).write_bytes(base64.b64decode(im["data"]))
            async def pos(a):
                return (await c(ac,"get_actor_transform",{"actor":a}))["location"]
            async def move(x):
                assert await c(ac,"set_actor_transform",{"actor":pawn,"xform":{"location":{"x":x,"y":0,"z":58}}})
                await asyncio.sleep(.85)
            async def key(k):
                await c(sl,"PressKey",{"key":k})
                await asyncio.sleep(.18)
            async def snapshot():
                return await c(sl,"Snapshot",{"ref":"w1","maxDepth":100})
            async def trace():
                s=await snapshot()
                f=re.search(r'text "Cmd".*\n.*\n\s*textbox .*\[ref=(tb\d+)\]',s)
                assert f
                assert await c(sl,"Type",{"ref":f[1],"text":"py C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4RgbRoom/trace.py","submit":True})
                await asyncio.sleep(.5)
                assert await c(sl,"Click",{"ref":"sp6"})
                return (out/"collision.txt").read_text()
            assert not await c(app,"IsPIERunning")
            await c(app,"StartPIE",{"options":{"bSimulate":False,"playMode":"PlayMode_InViewPort","warmupSeconds":1}})
            try:
                controller=await find("Color_Controller")
                door=await find("Color_ExitDoor")
                gate=await find("Vault Gallery Moving Gate")
                pawn=await find("DirectorCutDragon")
                await c(sl,"Observe",{"ref":"w1","maxDepth":100})
                await snapshot()
                assert await c(sl,"Click",{"ref":"sp6"})
                await asyncio.sleep(.6)
                await screen("lighting-gallery")
                assert not (await props(door,"bOpen"))["bOpen"]
                pre=await trace()
                print("Closed passage trace",pre,flush=True)
                assert pre.startswith("(True, False"),pre
                await key("E")
                assert (await props(controller,"bActive"))["bActive"]
                assert "Step Red" in (await snapshot())
                await screen("gallery-console")
                for k in ["One","One","Two","Three","Three","Three"]: await key(k)
                await asyncio.sleep(4.3)
                closed=(await pos(gate))["z"]
                assert (await props(door,"bOpen"))["bOpen"] and closed>355,closed
                await move(947)
                await screen("gallery-exit")
                post=await trace()
                print("Open passage trace",post,flush=True)
                assert post.startswith("(False, True"),post
                await move(1750)
                await asyncio.sleep(.9)
                assert "SHADOW RETAKE" in (await snapshot())
                print("PASS: RGB console, automatic solution, attached grate, traversable connection",flush=True)
            finally:
                if await c(app,"IsPIERunning"):
                    await c(app,"StopPIE")
asyncio.run(run())

