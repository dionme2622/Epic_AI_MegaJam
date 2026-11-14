import asyncio,json,base64
from pathlib import Path
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
   sl='SlateInspectorToolset.SlateInspectorToolset';obj='editor_toolset.toolsets.object.ObjectTools';act='editor_toolset.toolsets.actor.ActorTools';app='EditorToolset.EditorAppToolset'
   await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':2}})
   await c(sl,'Snapshot',{'ref':'','maxDepth':3});await c(sl,'Observe',{'ref':'w1','maxDepth':30});await c(sl,'Snapshot',{'ref':'w1','maxDepth':30});await c(sl,'Click',{'ref':'sp5'})
   pref='/Game/Level/UEDPIE_0_Stage1.Stage1:PersistentLevel.'
   ref=lambda n:{'refPath':pref+n}
   ctrl=ref('BP_Stage1Director_C_0');pawn=ref('BP_Stage1Dragon_C_0');gate=ref('StaticMeshActor_8');gear=ref('StaticMeshActor_5');lift=ref('StaticMeshActor_9')
   async def state():return json.loads(await c(obj,'get_properties',{'instance':ctrl,'properties':['IsLow','WheelX','WheelSolved','LiftActive','LiftAlpha','LiftSolved','LiftDescending','MenuOpen']}))
   async def pos(a):return await c(act,'get_actor_transform',{'actor':a})
   async def key(k):await c(sl,'PressKey',{'key':k});await asyncio.sleep(.45)
   async def place(x,z):
    await c(act,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':x,'y':0,'z':z}}});await asyncio.sleep(1)
   async def capture(n):
    img=await c(app,'CaptureEditorImage',{});Path('output/Stage1_Unreal_Export/'+n+'.png').write_bytes(base64.b64decode(img['data']))
   print('INITIAL',await state(),flush=True)
   await place(850,200);await key('Q');await asyncio.sleep(1);s0=await state();await asyncio.sleep(1);s1=await state();print('WHEEL_MOVES',s0['WheelX'],s1['WheelX'],flush=True)
   assert s1['WheelX']>s0['WheelX'];await capture('Refined/preview_wheel_high')
   for _ in range(80):
    sw=await state()
    if 1150 < sw['WheelX'] < 1260: break
    await asyncio.sleep(.1)
   else: raise RuntimeError('Wheel did not reach the target')
   await key('Q');await asyncio.sleep(.5)
   state1=await state();print('WHEEL_RESULT',state1,await pos(gate),flush=True);assert state1['WheelSolved'];await capture('Refined/preview_wheel_low')
   await place(8700,180);await key('E');print('LIFT_LOW',await state(),flush=True);assert not (await state())['LiftActive']
   await key('Q');await key('E');await asyncio.sleep(.5);s2=await state();print('LIFT_START',s2,flush=True);assert s2['LiftActive'] and not s2['IsLow']
   await key('Q');s3=await state();print('MOVING_QUALITY_CHECK',s3,flush=True);assert not s3['IsLow']
   await asyncio.sleep(5);up=await state();print('LIFT_UP',up,'PAWN',await pos(pawn),'LIFT',await pos(lift),'GEAR',await pos(gear),flush=True)
   assert up['LiftSolved'] and not up['LiftActive'] and up['LiftAlpha']>=229
   await capture('Refined/preview_gear_high')
   await key('E');await asyncio.sleep(5);down=await state();print('LIFT_DOWN',down,'PAWN',await pos(pawn),flush=True);assert not down['LiftActive'] and down['LiftAlpha']<=1
   await c(app,'StopPIE',{})
asyncio.run(main())
