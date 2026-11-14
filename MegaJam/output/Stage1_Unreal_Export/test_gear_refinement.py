import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError:raise RuntimeError(str(z.content))
    return json.loads(z.content[0].text).get('returnValue')
   sl='SlateInspectorToolset.SlateInspectorToolset';ob='editor_toolset.toolsets.object.ObjectTools';act='editor_toolset.toolsets.actor.ActorTools';app='EditorToolset.EditorAppToolset'
   await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   await c(sl,'Snapshot',{'ref':'','maxDepth':3});await c(sl,'Observe',{'ref':'w1','maxDepth':30});await c(sl,'Snapshot',{'ref':'w1','maxDepth':30});await c(sl,'Click',{'ref':'sp5'})
   pref='/Game/Level/UEDPIE_0_Stage1.Stage1:PersistentLevel.'
   ref=lambda n:{'refPath':pref+n}
   ctrl=ref('BP_Stage1Director_C_0');pawn=ref('BP_Stage1Dragon_C_0');gear=ref('StaticMeshActor_5')
   async def state():return json.loads(await c(ob,'get_properties',{'instance':ctrl,'properties':['IsLow','LiftActive','LiftAlpha','LiftSolved','MenuOpen']}))
   async def key(k):await c(sl,'PressKey',{'key':k});await asyncio.sleep(.4)
   await c(act,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':8700,'y':0,'z':180}}});await asyncio.sleep(1)
   await key('Q');await key('E');await asyncio.sleep(1)
   rot=await c(act,'get_actor_transform',{'actor':gear});before=await state();print('ROTATING',before,rot,flush=True)
   assert abs(rot['rotation']['pitch'])>1
   await key('M');paused=await state();print('MENU_OPEN',paused,flush=True);assert paused['MenuOpen']
   await key('One');after=await state();print('MENU_LOW_ATTEMPT',after,flush=True);assert not after['IsLow'] and after['LiftActive']
   await key('M');await asyncio.sleep(5);done=await state();print('ARRIVED',done,flush=True);assert done['LiftSolved'] and not done['LiftActive']
   await key('Q');end=await state();print('SWITCH_AFTER_ARRIVAL',end,flush=True);assert end['IsLow']
   await c(app,'StopPIE',{})
asyncio.run(main())
