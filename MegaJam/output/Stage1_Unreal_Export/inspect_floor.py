import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (rd,wr,_):
  async with ClientSession(rd,wr) as s:
   await s.initialize()
   async def call(ts,n,a):
    r=await s.call_tool('call_tool',{'toolset_name':ts,'tool_name':n,'arguments':a})
    print(n, a, r.content[0].text[:6500],flush=True)
   pref='/Game/Level/UEDPIE_0_Stage1.Stage1:PersistentLevel.'
   pawn={'refPath':pref+'BP_Stage1Dragon_C_0'}
   await call('editor_toolset.toolsets.actor.ActorTools','get_components',{'actor':pawn})
   for path in [pref+'StaticMeshActor_7',pref+'StaticMeshActor_9',pref+'BP_Stage1Dragon_C_0.CharacterMovement',pref+'BP_Stage1Dragon_C_0.CharMoveComp']:
    await call('editor_toolset.toolsets.object.ObjectTools','get_properties',{'instance':{'refPath':path},'properties':['bActorEnableCollision','currentFloor','movementBase']})
asyncio.run(main())
