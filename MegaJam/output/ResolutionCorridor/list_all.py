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
   for a in await c('editor_toolset.toolsets.scene.SceneTools','find_actors',{'name':'','tag':'','collision_channels':[]}):
    print(a['refPath'],await c('editor_toolset.toolsets.object.ObjectTools','get_class',{'instance':a}),flush=True)
asyncio.run(main())
