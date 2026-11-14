import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   for name,args in [('load_level',{'level_path':'/Game/Level/Stage2_Integrated'}),('find_actors',{'name':'TemporaryWalkQA','tag':'','collision_channels':[]})]:
    z=await s.call_tool('call_tool',{'toolset_name':'editor_toolset.toolsets.scene.SceneTools','tool_name':name,'arguments':args});print(name,z.content,flush=True)
asyncio.run(main())
