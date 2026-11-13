import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   for n in [4,5,6,7]:
    z=await s.call_tool('call_tool',{'toolset_name':'editor_toolset.toolsets.object.ObjectTools','tool_name':'set_properties','arguments':{'instance':{'refPath':f'/Game/Level/Stage2.Stage2:PersistentLevel.StaticMeshActor_{n}.StaticMeshComponent0'},'values':json.dumps({'bodyInstance':{'collisionEnabled':'NoCollision','collisionProfileName':'NoCollision'}})}})
    print(n,z.content[0].text,flush=True)
    if z.isError: raise RuntimeError(str(z.content))
   z=await s.call_tool('call_tool',{'toolset_name':'editor_toolset.toolsets.asset.AssetTools','tool_name':'save_assets','arguments':{'asset_paths':['/Game/Level/Stage2']}});print(z.content[0].text)
asyncio.run(main())
