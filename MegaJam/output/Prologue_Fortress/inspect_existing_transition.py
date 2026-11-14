import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(n,a):
    z=await s.call_tool('call_tool',{'toolset_name':'editor_toolset.toolsets.blueprint.BlueprintTools','tool_name':n,'arguments':a})
    if z.isError:raise RuntimeError(str(z.content))
    v=json.loads(z.content[0].text).get('returnValue');print(n,v,flush=True);return v
   g={'refPath':'/Game/DirectorCut/Prologue/BP_PrologueStageTransition.BP_PrologueStageTransition:EventGraph'}
   for name in ['OnPrologueFinished','Open Level','Bind Event']:
    nodes=await c('find_nodes',{'graph':g,'title':name})
    if nodes:await c('get_node_infos',{'nodes':nodes})
asyncio.run(main())
