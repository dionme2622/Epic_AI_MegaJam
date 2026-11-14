import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError: return None
    return json.loads(z.content[0].text).get('returnValue')
   sc='editor_toolset.toolsets.scene.SceneTools';ac='editor_toolset.toolsets.actor.ActorTools';ob='editor_toolset.toolsets.object.ObjectTools'
   actors=await c(sc,'find_actors',{'name':'','tag':'','collision_channels':[]})
   for a in actors:
    cls=await c(ob,'get_class',{'instance':a})
    transform=await c(ac,'get_actor_transform',{'actor':a})
    bounds=await c(ac,'get_actor_bounds',{'actor':a,'only_colliding_components':False,'include_from_child_actors':False})
    x=transform['location']['x'] if transform else 0
    if (abs(x)>600 or 'PlayerStart' in a['refPath'] or 'WorldSettings' in a['refPath'] or 'Dragon' in a['refPath']):
     print(a['refPath'],cls,transform,bounds,flush=True)
asyncio.run(main())
