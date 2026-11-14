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
   ref=lambda p:{'refPath':p}; bp=ref('/Game/DirectorCut/Prologue/BP_PrologueStageTransition.BP_PrologueStageTransition');graph=ref(bp['refPath']+':EventGraph')
   code='(event EventBeginPlay (Sequencer|Player|BindEventtoOnFinished :self (Class|LevelSequenceActor|GetSequencePlayer :self (Variables|Default|GetPrologueSequence))))'
   # The initial graph is present even though its incomplete delegate does not compile yet.
   ev=await c('add_event',{'blueprint':bp,'event_name':'OnPrologueFinished','position':{'x':0,'y':350}})
   bind=await c('find_nodes',{'graph':graph,'title':'Bind Event to On Finished'})
   eventnode=await c('create_node',{'graph':graph,'type_id':'EventDispatchers|CreateEvent','pos':{'x':350,'y':180}})
   openlevel=await c('create_node',{'graph':graph,'type_id':'Game|OpenLevel(byObjectReference)','pos':{'x':350,'y':350}})
   print('REFS',ev,bind,eventnode,openlevel,flush=True)
   await c('get_node_infos',{'nodes':[ev,eventnode,openlevel]+bind})
asyncio.run(main())
