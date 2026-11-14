import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a});return json.loads(z.content[0].text).get('returnValue')
   sc='editor_toolset.toolsets.scene.SceneTools';ac='editor_toolset.toolsets.actor.ActorTools';ob='editor_toolset.toolsets.object.ObjectTools'
   await c(sc,'load_level',{'level_path':'/Game/Level/Stage2_ShadowBody_Prototype'})
   for name in ['DirectionalLight','Overhead_Rig_0','ShadowStage_ColorGrade']:
    a=(await c(sc,'find_actors',{'name':name,'tag':'','collision_channels':[]}))[0];print(name,a,await c(ac,'get_actor_transform',{'actor':a}),flush=True)
    if name=='Overhead_Rig_0':print('RIG',await c(ob,'get_properties',{'instance':{'refPath':a['refPath']+'.StaticMeshComponent0'},'properties':['castShadow','bHiddenInGame','mobility']}),flush=True)
asyncio.run(main())
