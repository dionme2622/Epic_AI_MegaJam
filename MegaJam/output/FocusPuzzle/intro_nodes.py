import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   g={'refPath':'/Game/FocusPropPrototype/BP_FocusIntro.BP_FocusIntro:EventGraph'}
   for n in ['Pawn|GetViewTarget','Game|Player|SetViewTargetwithBlend','Delay|Delay','Actor|Tick|SetActorTickEnabled','Input|SetIgnoreMoveInput']:
    z=await s.call_tool('call_tool',{'toolset_name':'editor_toolset.toolsets.blueprint.BlueprintTools','tool_name':'get_node_type_pins','arguments':{'graph':g,'type_id':n}});print(n,z.content,flush=True)
asyncio.run(main())
