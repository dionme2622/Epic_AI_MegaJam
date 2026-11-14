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
   sc='editor_toolset.toolsets.scene.SceneTools';ac='editor_toolset.toolsets.actor.ActorTools';assets='editor_toolset.toolsets.asset.AssetTools';path='/Game/Stage4Integrated/L_ShadowStage'
   await c(sc,'load_level',{'level_path':path});a=(await c(sc,'find_actors',{'name':'Shadow_BackWall','tag':'','collision_channels':[]}))[0];assert path+'.' in a['refPath']
   print('BEFORE',await c(ac,'get_actor_transform',{'actor':a}),flush=True)
   await c(ac,'set_actor_transform',{'actor':a,'xform':{'location':{'x':1100,'y':-260,'z':-185},'rotation':{'pitch':0,'yaw':0,'roll':0},'scale':{'x':30,'y':.25,'z':16.3}}})
   await c(assets,'save_assets',{'asset_paths':[path]});print('SAVED',flush=True)
asyncio.run(main())
