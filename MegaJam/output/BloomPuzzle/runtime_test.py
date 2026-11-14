import asyncio,json,re,base64
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
   sl='SlateInspectorToolset.SlateInspectorToolset';ob='editor_toolset.toolsets.object.ObjectTools';act='editor_toolset.toolsets.actor.ActorTools'
   snap=await c(sl,'Snapshot',{'ref':'','maxDepth':3});window=re.search(r'\[ref=(w\d+)\]',snap).group(1)
   await c(sl,'Observe',{'ref':window,'maxDepth':30});await asyncio.sleep(1);await c(sl,'Snapshot',{'ref':window,'maxDepth':30});print('FOCUS',await c(sl,'Click',{'ref':'sp5'}),flush=True)
   p='/Game/Level/UEDPIE_0_Stage2_BloomSign_Prototype.Stage2_BloomSign_Prototype:PersistentLevel.'
   ctl={'refPath':p+'BP_BloomController_C_0'};pawn={'refPath':p+'BP_Dragon_C_0'};door={'refPath':p+'BP_S2_Door_C_0'};pp={'refPath':p+'PostProcessVolume_0'}
   async def props(a,n):return json.loads(await c(ob,'get_properties',{'instance':a,'properties':n}))
   async def key(k):await c(sl,'PressKey',{'key':k});await asyncio.sleep(.3)
   async def snap(name):
    img=await c('EditorToolset.EditorAppToolset','CaptureEditorImage',{});Path('output/BloomPuzzle/'+name+'.png').write_bytes(base64.b64decode(img['data']))
   async def move(x):
    await c(act,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':x,'y':0,'z':92},'rotation':{'pitch':0,'yaw':0,'roll':0},'scale':{'x':1,'y':1,'z':1}}});await asyncio.sleep(.6)
   print('INIT',await props(ctl,['bBloomOn','bConsoleOpen','sequenceProgress','bSolved']),flush=True)
   print('EXPOSURE',[(k,v) for k,v in (await props(pp,['settings']))['settings'].items() if k in ['autoExposureBias','autoExposureApplyPhysicalCameraExposure','bOverride_AutoExposureApplyPhysicalCameraExposure','bloomIntensity']],flush=True)
   await move(350);await snap('bloom_on');await key('B');await snap('bloom_off');print('BLOOM_OFF',await props(ctl,['bBloomOn']),flush=True)
   await move(900);await snap('moon');await move(1450);await snap('sun');await move(2000);await key('E');print('CONSOLE',await props(ctl,['bConsoleOpen']),flush=True)
   await key('One');await key('Three');print('WRONG',await props(ctl,['sequenceProgress','bSolved']),flush=True)
   for k in ['One','Two','Three']:await key(k)
   await asyncio.sleep(2);print('SUCCESS',await props(ctl,['sequenceProgress','bSolved','bConsoleOpen']),await props(door,['bOpen']),flush=True)
asyncio.run(main())
