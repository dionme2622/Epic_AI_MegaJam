import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   for n in ['Stage2|Rendering|SetShadowsEnabled','Stage2|Shadow|MoveShadowPiece','Stage2|Sequence|EnterSymbol','Stage2|Film|SelectFilm','Stage2|Film|SubmitFilmSolution']:
    z=await s.call_tool('call_tool',{'toolset_name':'editor_toolset.toolsets.blueprint.BlueprintTools','tool_name':'get_node_type_pins','arguments':{'graph':{'refPath':'/Game/Stage2Prototype/BP_Stage2Prototype.BP_Stage2Prototype:EventGraph'},'type_id':n}})
    try:
     v=json.loads(z.content[0].text)['returnValue'];print(n,[(p['name'],p['value'],p['type_id']) for p in v['input_pins']],flush=True)
    except: print(n,z.content,flush=True)
asyncio.run(main())
