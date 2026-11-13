import asyncio,json
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(ts,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':ts,'tool_name':n,'arguments':a}); print(n,z.content[0].text[:1500],flush=True)
    if z.isError: raise RuntimeError(str(z.content))
   t='editor_toolset.toolsets.blueprint.BlueprintTools'; bp='/Game/Stage2Prototype/BP_Stage2Prototype.BP_Stage2Prototype'
   for v in ['TestScene','TestDirection','TestMark']:
    await c(t,'add_variable',{'blueprint':{'refPath':bp},'name':v,'type_name':'bool'})
   await c(t,'write_graph_dsl',{'graph':{'refPath':bp+':EventGraph'},'code':Path('output/stage2_prototype.dsl').read_text()})
   await c('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':['/Game/Level/Stage2','/Game/Stage2Prototype/BP_Stage2Prototype']})
asyncio.run(main())
