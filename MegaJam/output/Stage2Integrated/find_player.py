import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   for name in ['Pawn','Character','Player','Director','Stage1']:
    z=await s.call_tool('call_tool',{'toolset_name':'editor_toolset.toolsets.scene.SceneTools','tool_name':'find_actors','arguments':{'name':name,'tag':'','collision_channels':[]}});print(name,str(z.content)[:7000],flush=True)
asyncio.run(main())
