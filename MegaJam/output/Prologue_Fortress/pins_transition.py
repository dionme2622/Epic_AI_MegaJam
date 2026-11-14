import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   g={'refPath':'/Game/DirectorCut/Prologue/BP_PrologueStageTransition.BP_PrologueStageTransition:EventGraph'}
   for name in ['Class|LevelSequenceActor|GetSequencePlayer','Sequencer|Player|BindEventtoOnFinished','EventDispatchers|CreateEvent','Game|OpenLevel(byObjectReference)','Variables|Default|GetPrologueSequence']:
    z=await s.call_tool('call_tool',{'toolset_name':'editor_toolset.toolsets.blueprint.BlueprintTools','tool_name':'get_node_type_pins','arguments':{'graph':g,'type_id':name}})
    print(name,z.content,flush=True)
asyncio.run(main())
