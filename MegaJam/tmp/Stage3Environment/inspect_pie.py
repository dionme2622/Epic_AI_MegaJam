import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client("http://127.0.0.1:18765/mcp") as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a={}):
    z=await s.call_tool("call_tool",{"toolset_name":t,"tool_name":n,"arguments":a})
    if z.isError:raise RuntimeError(str(z.content))
    return json.loads(z.content[0].text).get("returnValue")
   sc="editor_toolset.toolsets.scene.SceneTools";ac="editor_toolset.toolsets.actor.ActorTools";app="EditorToolset.EditorAppToolset"
   await c(app,"StartPIE",{"options":{"bSimulate":False,"playMode":"PlayMode_InViewPort","warmupSeconds":1}})
   try:
    for n in ["Bloom_Sign","Bloom_Controller","Resolution_Controller","Resolution","Focus_Controller","Door","PostProcess"]:
     for a in await c(sc,"find_actors",{"name":n,"tag":"","collision_channels":[]}):
      print(n,a["refPath"],await c(ac,"get_actor_transform",{"actor":a}),flush=True)
   finally:await c(app,"StopPIE")
asyncio.run(main())
