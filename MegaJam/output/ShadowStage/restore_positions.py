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
   l=(await c(sc,'find_actors',{'name':'DirectionalLight','tag':'','collision_channels':[]}))[0];assert '/Game/Level/Stage2_ShadowBody_Prototype.' in l['refPath']
   await c(ac,'set_actor_transform',{'actor':l,'xform':{'location':{'x':0,'y':0,'z':400},'rotation':{'pitch':-80.4803901821914,'yaw':-88.7885003939543,'roll':-69.06887165998292},'scale':{'x':1,'y':1,'z':1}}})
   for i,x in enumerate([400,670,940,1210,1480,1750]):
    a=(await c(sc,'find_actors',{'name':f'Overhead_Rig_{i}','tag':'','collision_channels':[]}))[0];await c(ac,'set_actor_transform',{'actor':a,'xform':{'location':{'x':x,'y':0,'z':365},'rotation':{'pitch':0,'yaw':0,'roll':0},'scale':{'x':2.5,'y':5.2,'z':.65}}})
   await c(assets,'save_assets',{'asset_paths':['/Game/Level/Stage2_ShadowBody_Prototype']});print('PLACEMENT_RESTORED',flush=True)
asyncio.run(main())
