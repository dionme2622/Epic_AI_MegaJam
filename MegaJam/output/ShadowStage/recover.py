import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a});print(n,z.content,flush=True)
   await c('editor_toolset.toolsets.asset.AssetTools','duplicate',{'path':'/Game/DirectorCut/Stage/Stage2_','new_path':'/Game/ShadowBodyStage/Backups/Stage2_UnsavedRecovery'})
   await c('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':['/Game/ShadowBodyStage/Backups/Stage2_UnsavedRecovery']})
   await c('editor_toolset.toolsets.scene.SceneTools','load_level',{'level_path':'/Game/Level/Stage2_ShadowBody_Prototype'})
   await c('editor_toolset.toolsets.scene.SceneTools','find_actors',{'name':'WorldSettings','tag':'','collision_channels':[]})
asyncio.run(main())
