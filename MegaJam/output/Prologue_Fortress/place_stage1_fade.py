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
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:300],flush=True);return v
   sc='editor_toolset.toolsets.scene.SceneTools';asset='editor_toolset.toolsets.asset.AssetTools'
   await c(sc,'load_level',{'level_path':'/Game/Level/Stage1'})
   found=await c(sc,'find_actors',{'name':'Stage1_EntryFade','tag':'','collision_channels':[]})
   if not found:
    await c(sc,'add_to_scene_from_asset',{'asset_path':'/Game/DirectorCut/Transitions/BP_StageFadeIn.BP_StageFadeIn','name':'Stage1_EntryFade','xform':{'location':{'x':0,'y':0,'z':0}}})
   await c(asset,'save_assets',{'asset_paths':['/Game/Level/Stage1']})
asyncio.run(main())
