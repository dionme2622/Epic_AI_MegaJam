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
   scene='editor_toolset.toolsets.scene.SceneTools';obj='editor_toolset.toolsets.object.ObjectTools';act='editor_toolset.toolsets.actor.ActorTools'
   actors=await c(scene,'find_actors',{'name':'','tag':'','collision_channels':[]})
   for a in actors:
    try:
     p=json.loads(await c(obj,'get_properties',{'instance':a,'properties':['tags']}))
     tr=await c(act,'get_actor_transform',{'actor':a})
     if p.get('tags') or 'Stage1' in a['refPath']: print(a['refPath'],p,tr,flush=True)
    except Exception as e: print('ERR',str(e)[:150])
asyncio.run(main())
