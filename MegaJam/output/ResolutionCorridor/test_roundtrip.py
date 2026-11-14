import asyncio,json,base64,re
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
   app='EditorToolset.EditorAppToolset';sl='SlateInspectorToolset.SlateInspectorToolset';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools'
   await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   p='/Game/Level/UEDPIE_0_Stage2_ResolutionCorridor_Prototype.Stage2_ResolutionCorridor_Prototype:PersistentLevel.'
   ref=lambda x:{'refPath':p+x};arrow=ref('StaticMeshActor_10');pawn=ref('DirectorCutDragon_0');ctl=ref('BP_ResolutionCorridor_C_0');trap=ref('BP_ResolutionTile_C_1')
   async def prop(a,n):return json.loads(await c(ob,'get_properties',{'instance':a,'properties':n}))
   async def snap():
    await c(sl,'Snapshot',{'ref':'','maxDepth':3});await c(sl,'Observe',{'ref':'w1','maxDepth':100});return await c(sl,'Snapshot',{'ref':'sp6','maxDepth':100})
   async def pressref(text):
    v=await snap();m=re.search(r'button "'+re.escape(text)+r'".*?\[ref=(b\d+)\]',v)
    if not m:raise RuntimeError('Missing UI button '+text)
    await c(sl,'Click',{'ref':m.group(1)});await asyncio.sleep(.2)
   async def image(name):
    z=await c(app,'CaptureEditorImage',{});Path('output/ResolutionCorridor/'+name+'.png').write_bytes(base64.b64decode(z['data']))
   async def setresolution(low):
    await pressref('⚙');v=await snap()
    if 'text "해상도"' not in v:
     await c(sl,'PressKey',{'key':'Enter'});await asyncio.sleep(.2);v=await snap()
    m=re.search(r'text "해상도".*?\n\s*button "낮음".*?\[ref=(b\d+)\]\s*\n\s*button "높음".*?\[ref=(b\d+)\]',v)
    if not m:raise RuntimeError('Resolution buttons not found: '+v)
    await c(sl,'Click',{'ref':m.group(1 if low else 2)});await asyncio.sleep(.3)
    if (await prop(arrow,['bHidden']))['bHidden']==low:
     await c(sl,'PressKey',{'key':'Enter'});await asyncio.sleep(.2)
    await pressref('닫기')
    if 'text "해상도"' in await snap():
     await c(sl,'PressKey',{'key':'Enter'});await asyncio.sleep(.2)
   print('INITIAL',await prop(arrow,['bHidden']),flush=True)
   await setresolution(True);await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':280,'y':0,'z':85}}});await asyncio.sleep(.6)
   assert not (await prop(arrow,['bHidden']))['bHidden'];print('LOW',await c(app,'SearchCVars',{'name':'r.ScreenPercentage'}),flush=True);await image('final_low')
   await setresolution(False);assert (await prop(arrow,['bHidden']))['bHidden'];print('HIGH',await c(app,'SearchCVars',{'name':'r.ScreenPercentage'}),flush=True);await image('final_high')
   await c(ob,'set_properties',{'instance':ctl,'values':json.dumps({'sinkDuration':3.0})})
   await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':560,'y':0,'z':90}}});await asyncio.sleep(1)
   state=await prop(ctl,['bFailing','progress']);pos=await c(ac,'get_actor_transform',{'actor':trap});print('SINKING',state,pos['location'],flush=True)
   assert state['bFailing'] and pos['location']['z']<-12.5
   await asyncio.sleep(3.2);state=await prop(ctl,['bFailing','progress']);pos=await c(ac,'get_actor_transform',{'actor':trap});playerpos=await c(ac,'get_actor_transform',{'actor':pawn});print('RESET',state,pos['location'],playerpos['location'],flush=True)
   assert not state['bFailing'] and state['progress']==0 and abs(pos['location']['z']+12)<1 and abs(playerpos['location']['x'])<5
   await c(app,'StopPIE',{})
asyncio.run(main())
