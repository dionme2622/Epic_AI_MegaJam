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
    return json.loads(z.content[0].text).get('returnValue')
   assets='editor_toolset.toolsets.asset.AssetTools';sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools'
   print('DUP',await c(assets,'duplicate',{'path':'/Game/Level/Stage2_FocusProp_Prototype','new_path':'/Game/Level/Stage2_ShadowBody_Prototype'}),flush=True)
   await c(assets,'save_assets',{'asset_paths':['/Game/Level/Stage2_ShadowBody_Prototype']})
   await c(sc,'load_level',{'level_path':'/Game/Level/Stage2_ShadowBody_Prototype'})
   for a in await c(sc,'find_actors',{'name':'','tag':'','collision_channels':[]}):
    print('ACTOR',a,await c(ob,'get_class',{'instance':a}),flush=True)
asyncio.run(main())
