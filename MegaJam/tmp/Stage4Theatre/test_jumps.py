import asyncio, json, re
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def run():
    path=Path("tmp/Stage4Theatre/jump_report.json")
    if path.exists(): path.unlink()
    async with streamable_http_client("http://127.0.0.1:8000/mcp") as (read,write,_):
        async with ClientSession(read,write) as session:
            await session.initialize()
            async def call(toolset,name,arguments=None):
                reply=await session.call_tool("call_tool",{"toolset_name":toolset,"tool_name":name,"arguments":arguments or {}})
                if reply.isError: raise RuntimeError((name,reply.content))
                return json.loads(reply.content[0].text)["returnValue"]
            app="EditorToolset.EditorAppToolset"
            sl="SlateInspectorToolset.SlateInspectorToolset"
            sc="editor_toolset.toolsets.scene.SceneTools"
            ac="editor_toolset.toolsets.actor.ActorTools"

            assert not await call(app,"IsPIERunning")
            await call(app,"StartPIE",{"options":{"bSimulate":False,"playMode":"PlayMode_InViewPort","warmupSeconds":1}})
            try:
                await call(sl,"Observe",{"ref":"w1","maxDepth":100})
                await call(sl,"Snapshot",{"ref":"w1","maxDepth":100})
                await call(sl,"Click",{"ref":"sp6"})
                for key in ["E","One","One","Two","Three","Three","Three"]:
                    await call(sl,"PressKey",{"key":key})
                    await asyncio.sleep(.12)
                await asyncio.sleep(2.75)
                pawn,=await call(sc,"find_actors",{"name":"DirectorCutDragon","tag":"","collision_channels":[]})
                await call(ac,"set_actor_transform",{"actor":pawn,"xform":{"location":{"x":1890,"y":0,"z":58}}})
                # Use the in-game console to stage the timed input from Unreal Python.
                snapshot=await call(sl,"Snapshot",{"ref":"w1","maxDepth":100})
                Path("tmp/Stage4Theatre/jump_slate.txt").write_text(snapshot, encoding="utf-8")
                field=re.search(r'text "Cmd".*\n.*\n\s*textbox .*\[ref=(tb\d+)\]',snapshot)
                assert field, snapshot[-5000:]
                print("Console field",field[0],flush=True)
                assert await call(sl,"Type",{"ref":field[1],"text":"py C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4Theatre/test_jumps_live.py","submit":True})
                await call(sl,"Click",{"ref":"sp6"})
                for _ in range(65):
                    if path.exists(): break
                    await asyncio.sleep(.6)
                assert path.exists(),"No jump report"
                report=json.loads(path.read_text())
                print(report,flush=True)
                assert not report["error"] and len(report["landings"])==8 and report["checkpoint"]==2,report
            finally:
                await call(app,"StopPIE")
asyncio.run(run())
