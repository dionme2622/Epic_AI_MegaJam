import asyncio,json,base64
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client("http://127.0.0.1:18765/mcp") as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a={}):
    z=await s.call_tool("call_tool",{"toolset_name":t,"tool_name":n,"arguments":a})
    if z.isError:raise RuntimeError(str(z.content))
    return json.loads(z.content[0].text)["returnValue"]
   sc="editor_toolset.toolsets.scene.SceneTools"; act="editor_toolset.toolsets.actor.ActorTools"; sl="SlateInspectorToolset.SlateInspectorToolset"; app="EditorToolset.EditorAppToolset"
   assert not await c(app,"IsPIERunning")
   await c(app,"StartPIE",{"options":{"bSimulate":False,"playMode":"PlayMode_InViewPort","warmupSeconds":1}})
   try:
    await c(sl,"Observe",{"ref":"w1","maxDepth":80});await c(sl,"Snapshot",{"ref":"w1","maxDepth":80});await c(sl,"Click",{"ref":"sp6"})
    a=await c(sc,"find_actors",{"name":"Stage1_Player","tag":"","collision_channels":[]});pawn=a[0]
    director=(await c(sc,"find_actors",{"name":"PuzzleDirector","tag":"","collision_channels":[]}))[0]
    print("pawn",pawn,"director",director,flush=True)
    for n,x,z in [("entry",-600,110),("wheel",500,110),("middle",4400,110),("lift",8500,110),("exit",9100,430)]:
     await c(act,"set_actor_transform",{"actor":pawn,"xform":{"location":{"x":x,"y":0,"z":z}}})
     await asyncio.sleep(1.3)
     a=await c(app,"CaptureEditorImage");Path("tmp/Stage2Workshop/"+n+"_before.png").write_bytes(base64.b64decode(a["data"]))
   finally:
    await c(app,"StopPIE")
asyncio.run(main())
