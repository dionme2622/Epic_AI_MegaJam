import asyncio, json, re
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def run():
    path=Path("tmp/Stage4Retake/jumps.json")
    if path.exists(): path.unlink()
    phase=path.parent/"jump_phase.txt"
    if phase.exists(): phase.unlink()
    async with streamable_http_client("http://127.0.0.1:18765/mcp") as (read,write,_):
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
                await asyncio.sleep(.6)
                await call(sl,"PressKey",{"key":"Q"})
                await asyncio.sleep(.7)
                await call(sl,"PressKey",{"key":"E"})
                await asyncio.sleep(.7)
                # Use the in-game console to stage the timed input from Unreal Python.
                snapshot=await call(sl,"Snapshot",{"ref":"w1","maxDepth":100})
                Path("tmp/Stage4Retake/jump_slate.txt").write_text(snapshot, encoding="utf-8")
                ui_ref=re.search(r'button "Stop.*?\[ref=(b\d+)\]',snapshot)
                print("Stop button ref",ui_ref[1] if ui_ref else "none",flush=True)
                field=re.search(r'text "Cmd".*\n.*\n\s*textbox .*\[ref=(tb\d+)\]',snapshot)
                assert field, snapshot[-5000:]
                print("Console field",field[0],flush=True)
                assert await call(sl,"Type",{"ref":field[1],"text":"py C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4Retake/jump_live.py","submit":True})
                await call(sl,"Click",{"ref":"sp6"})
                async def press(value):
                    await call(sl,"PressKey",{"key":value})
                for expected,aim in [("await_cut 4","Q"),("await_cut 6","R"),("await_recovery 8",None)]:
                    for _ in range(95):
                        if path.exists() or (phase.exists() and phase.read_text()==expected): break
                        await asyncio.sleep(.14)
                    if path.exists(): break
                    assert phase.exists() and phase.read_text()==expected,(expected,phase.read_text() if phase.exists() else None)
                    if aim:
                        await press(aim)
                        await asyncio.sleep(.55)
                    await press("E")
                for _ in range(65):
                    if path.exists(): break
                    await asyncio.sleep(.6)
                assert path.exists(),"No jump report"
                report=json.loads(path.read_text())
                print(report,flush=True)
                assert not report["error"] and len(report["landings"])==8 and report["checkpoint"]==2 and report["recovered"] and report["reset_count"]==0,report
            finally:
                await call(app,"StopPIE")
asyncio.run(run())

