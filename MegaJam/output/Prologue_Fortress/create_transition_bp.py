import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(n,a):
    z=await s.call_tool('call_tool',{'toolset_name':'editor_toolset.toolsets.blueprint.BlueprintTools','tool_name':n,'arguments':a})
    print(n,z.content,flush=True)
    if z.isError:raise RuntimeError(str(z.content))
    return json.loads(z.content[0].text).get('returnValue')
   ref=lambda p:{'refPath':p}
   bp=ref('/Game/DirectorCut/Prologue/BP_PrologueStageTransition.BP_PrologueStageTransition')
   graph=ref('/Game/DirectorCut/Prologue/BP_PrologueStageTransition.BP_PrologueStageTransition:EventGraph')
   await c('set_variable_instance_editable',{'blueprint':bp,'variable_name':'PrologueSequence','instance_editable':True})
   for f in ['GetSequencePlayer','BindEventtoOnFinished','OpenLevel','CreateEvent']:
    await c('find_node_types',{'graph':graph,'type_id_filter':f,'context_pins':[]})
asyncio.run(main())
