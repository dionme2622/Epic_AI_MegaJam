import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (rd,wr,_):
  async with ClientSession(rd,wr) as s:
   await s.initialize()
   async def call(ts,n,a):
    r=await s.call_tool('call_tool',{'toolset_name':ts,'tool_name':n,'arguments':a})
    if r.isError: raise RuntimeError(str(r.content))
    return json.loads(r.content[0].text).get('returnValue')
   slate='SlateInspectorToolset.SlateInspectorToolset'; obj='editor_toolset.toolsets.object.ObjectTools'; act='editor_toolset.toolsets.actor.ActorTools'
   pref='/Game/Level/UEDPIE_0_Stage1.Stage1:PersistentLevel.'
   ctrl={'refPath':pref+'BP_Stage1Director_C_0'}; pawn={'refPath':pref+'BP_Stage1Dragon_C_0'}; lift={'refPath':pref+'StaticMeshActor_9'}
   async def state(): return json.loads(await call(obj,'get_properties',{'instance':ctrl,'properties':['IsLow','LiftActive','LiftAlpha','LiftSolved','LiftDescending']}))
   async def pos(a): return (await call(act,'get_actor_transform',{'actor':a}))['location']
   async def key(k):
    await call(slate,'PressKey',{'key':k}); await asyncio.sleep(.4)
   async def place(x,z):
    await call(act,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':x,'y':0,'z':z}}}); await asyncio.sleep(1)
   await call(slate,'Observe',{'ref':'w1'}); await call(slate,'Snapshot',{'ref':'w1','maxDepth':6}); await call(slate,'Click',{'ref':'sp5'})
   await place(8430,200); await key('Q'); await key('E'); print('OFF_PLATFORM',await state(),'PLAYER',await pos(pawn))
   await place(8700,180); print('ON_PLATFORM',await state(),'PLAYER',await pos(pawn),'LIFT',await pos(lift))
   await key('Q'); await key('E'); print('LOW_ATTEMPT',await state())
   await key('Q'); await key('E'); await asyncio.sleep(5.5); print('UP',await state(),'PLAYER',await pos(pawn),'LIFT',await pos(lift))
   await key('E'); await asyncio.sleep(5.5); print('DOWN',await state(),'PLAYER',await pos(pawn),'LIFT',await pos(lift))
   await key('E'); await asyncio.sleep(5.5)
   await place(8950,440); print('UPPER_FLOOR',await state(),'PLAYER',await pos(pawn))
asyncio.run(main())
