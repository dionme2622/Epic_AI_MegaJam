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
   sc='editor_toolset.toolsets.scene.SceneTools';ac='editor_toolset.toolsets.actor.ActorTools';assets='editor_toolset.toolsets.asset.AssetTools'
   await c(sc,'load_level',{'level_path':'/Game/Level/Stage2_ShadowBody_Prototype'})
   a=(await c(sc,'find_actors',{'name':'Shadow_PitBackdrop','tag':'','collision_channels':[]}))[0];assert '/Game/Level/Stage2_ShadowBody_Prototype.' in a['refPath']
   print('MOVE',await c(ac,'set_actor_transform',{'actor':a,'xform':{'location':{'x':1100,'y':0,'z':-650}}}),flush=True)
   print('SAVE',await c(assets,'save_assets',{'asset_paths':['/Game/Level/Stage2_ShadowBody_Prototype']}),flush=True)
asyncio.run(main())
