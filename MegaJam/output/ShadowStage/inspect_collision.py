import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a});return json.loads(z.content[0].text).get('returnValue')
   sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools'
   await c(sc,'load_level',{'level_path':'/Game/Level/Stage2_ShadowBody_Prototype'})
   for n in ['Shadow_PitBackdrop','Overhead_Rig_0','Shadow_BackWall','Shadow_SafePlatform_1']:
    a=(await c(sc,'find_actors',{'name':n,'tag':'','collision_channels':[]}))[0];co={'refPath':a['refPath']+'.StaticMeshComponent0'};print(n,await c(ob,'get_properties',{'instance':co,'properties':['bodyInstance','castShadow']}),await c(ac,'get_actor_transform',{'actor':a}),flush=True)
asyncio.run(main())
