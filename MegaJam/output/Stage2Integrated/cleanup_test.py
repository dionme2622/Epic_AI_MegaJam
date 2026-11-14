import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError:raise RuntimeError(str(z.content))
    v=json.loads(z.content[0].text).get('returnValue');print(n,v,flush=True);return v
   sc='editor_toolset.toolsets.scene.SceneTools';asset='editor_toolset.toolsets.asset.AssetTools'
   for a in await c(sc,'find_actors',{'name':'TemporaryWalkQA','tag':'','collision_channels':[]}):
    await c(sc,'remove_from_scene',{'actor':a})
   await c(asset,'save_assets',{'asset_paths':['/Game/Level/Stage1']})
   await c(asset,'delete',{'path':'/Game/Stage2Integrated/BP_TempStage1WalkQA'})
asyncio.run(main())

