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
   sc='editor_toolset.toolsets.scene.SceneTools';app='EditorToolset.EditorAppToolset';ac='editor_toolset.toolsets.actor.ActorTools';assets='editor_toolset.toolsets.asset.AssetTools'
   if await c(app,'IsPIERunning',{}):await c(app,'StopPIE',{})
   await c(sc,'load_level',{'level_path':'/Game/Level/Stage2_ShadowBody_Prototype'})
   l=(await c(sc,'find_actors',{'name':'DirectionalLight','tag':'','collision_channels':[]}))[0];assert '/Game/Level/Stage2_ShadowBody_Prototype.' in l['refPath']
   await c(ac,'set_actor_transform',{'actor':l,'xform':{'rotation':{'pitch':-80.4803901821914,'yaw':-88.7885003939543,'roll':-69.06887165998292}}})
   for a in await c(sc,'find_actors',{'name':'Overhead_Rig_','tag':'','collision_channels':[]}):await c(ac,'set_actor_transform',{'actor':a,'xform':{'scale':{'x':2.5,'y':5.2,'z':.65}}})
   await c(assets,'save_assets',{'asset_paths':['/Game/Level/Stage2_ShadowBody_Prototype']});print('RESTORED',flush=True)
asyncio.run(main())
