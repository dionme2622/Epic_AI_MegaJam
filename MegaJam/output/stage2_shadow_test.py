import asyncio,json,re
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError: raise RuntimeError(str(z.content))
    return json.loads(z.content[0].text).get('returnValue')
   sl='SlateInspectorToolset.SlateInspectorToolset';obj='editor_toolset.toolsets.object.ObjectTools';act='editor_toolset.toolsets.actor.ActorTools'
   snap=await c(sl,'Snapshot',{'ref':'','maxDepth':3}); ref=re.search(r'\[ref=(w\d+)\]',snap).group(1)
   await c(sl,'Observe',{'ref':ref,'maxDepth':30}); await asyncio.sleep(1); snap=await c(sl,'Snapshot',{'ref':ref,'maxDepth':30})
   print('VIEWPORT', '\n'.join([l for l in snap.splitlines() if 'splitter' in l][:10]),flush=True)
   print('CLICK',await c(sl,'Click',{'ref':'sp5'}),flush=True)
   p='/Game/Level/UEDPIE_0_Stage2_ShadowStealth_Prototype.Stage2_ShadowStealth_Prototype:PersistentLevel.'
   pawn={'refPath':p+'BP_Dragon_C_0'};manager={'refPath':p+'BP_S2_SectionManager_C_0'};spot={'refPath':p+'BP_S2_Spotlight_C_0'};door={'refPath':p+'BP_S2_Door_C_0'}
   async def props(a,n):return json.loads(await c(obj,'get_properties',{'instance':a,'properties':n}))
   async def move(x,z=92):
    await c(act,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':x,'y':0,'z':z},'rotation':{'pitch':0,'yaw':0,'roll':0},'scale':{'x':1,'y':1,'z':1}}});await asyncio.sleep(.3)
   async def key(k):await c(sl,'PressKey',{'key':k});await asyncio.sleep(.4)
   await move(200);await key('E');print('GRAB',await props(manager,['bHoldingCrate']),flush=True)
   await key('E');print('RELEASE',await props(manager,['bHoldingCrate']),flush=True)
   await move(800);await asyncio.sleep(7.5);print('DETECTION',await c(act,'get_actor_transform',{'actor':pawn}),await props(spot,['bPlayerInBeam','bPlayerCovered','ExposureTime']),flush=True)
   await move(1400);await key('Q');await key('E');await asyncio.sleep(2.5);print('LEVER',await props(manager,['bSectionCompleted']),await props(door,['bOpen']),await c(act,'get_actor_transform',{'actor':door}),flush=True)
asyncio.run(main())
