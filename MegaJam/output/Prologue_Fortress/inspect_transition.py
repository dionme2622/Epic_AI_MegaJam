import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    print(n,z.content,flush=True)
    if z.isError: return None
    return json.loads(z.content[0].text).get('returnValue')
   ref=lambda p:{'refPath':p}
   sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools'
   actors=await c(sc,'find_actors',{'name':'Sequence','tag':'','collision_channels':[]})
   for a in actors:
    await c(ob,'list_properties',{'instance':a})
   await c('editor_toolset.toolsets.blueprint.BlueprintTools','find_node_types',{'graph':ref('/Game/Stage1Generated/BP_Stage1Director.BP_Stage1Director:EventGraph'),'type_id_filter':'OnFinished','context_pins':[]})
asyncio.run(main())
