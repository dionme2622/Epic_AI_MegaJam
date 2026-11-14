import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError:return None
    return json.loads(z.content[0].text).get('returnValue')
   sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools'
   for a in await c(sc,'find_actors',{'name':'','tag':'','collision_channels':[]}):
    if 'StaticMeshActor' not in a['refPath']:continue
    m=await c(ob,'get_properties',{'instance':{'refPath':a['refPath']+'.StaticMeshComponent0'},'properties':['staticMesh']})
    if m and ('Exit' in m or 'Door' in m or 'Film_Set' in m):
     print(a,m,await c(ac,'get_actor_transform',{'actor':a}),await c(ac,'get_actor_bounds',{'actor':a,'only_colliding_components':False,'include_from_child_actors':False}),flush=True)
asyncio.run(main())
