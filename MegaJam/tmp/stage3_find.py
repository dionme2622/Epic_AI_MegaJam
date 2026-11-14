import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client("http://127.0.0.1:18765/mcp") as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   for name in ("Bloom_Controller","Bloom_Sign","Resolution_Controller","Tile","Stage3 Film Scene"):
    z=await s.call_tool("call_tool",{"toolset_name":"editor_toolset.toolsets.scene.SceneTools","tool_name":"find_actors","arguments":{"name":name,"tag":"","collision_channels":[]}})
    print(name,z.content[0].text,flush=True)
asyncio.run(main())
