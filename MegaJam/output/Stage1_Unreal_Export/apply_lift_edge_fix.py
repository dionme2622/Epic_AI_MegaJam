import asyncio,json
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (rd,wr,_):
  async with ClientSession(rd,wr) as s:
   await s.initialize()
   for ts,n,args in [('editor_toolset.toolsets.blueprint.BlueprintTools','write_graph_dsl',{'graph':{'refPath':'/Game/Stage1Generated/BP_Stage1Director.BP_Stage1Director:EventGraph'},'code':Path('output/Stage1_Unreal_Export/director_v3.dsl').read_text(encoding='utf8')}),('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':['/Game/Stage1Generated/BP_Stage1Director']})]:
    r=await s.call_tool('call_tool',{'toolset_name':ts,'tool_name':n,'arguments':args}); print(n,r.content[0].text[:1200],flush=True)
    if r.isError: raise RuntimeError(str(r.content))
asyncio.run(main())
