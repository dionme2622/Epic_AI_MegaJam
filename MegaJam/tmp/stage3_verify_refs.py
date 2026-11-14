import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client("http://127.0.0.1:18765/mcp") as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a={}):
    z=await s.call_tool("call_tool",{"toolset_name":t,"tool_name":n,"arguments":a})
    if z.isError:raise RuntimeError((n,z.content))
    return json.loads(z.content[0].text)["returnValue"]
   for name,fields in [("Bloom_Controller",["bUseFilmEditing","FilmSources","FilmScenes"]),("Resolution_Controller",["bUseStationChoices","stationAnswers","stationCheckpointOffsets","guidanceArrows"]),("Archive Empty Crate",["bOpened"])]:
    a=await c("editor_toolset.toolsets.scene.SceneTools","find_actors",{"name":name,"tag":"","collision_channels":[]})
    print(name,a,flush=True)
    for x in a:print(await c("editor_toolset.toolsets.object.ObjectTools","get_properties",{"instance":x,"properties":fields}),flush=True)
asyncio.run(main())
