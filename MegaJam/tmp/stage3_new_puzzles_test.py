import asyncio,json,base64,re
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:18765/mcp') as (rd,wr,_):
  async with ClientSession(rd,wr) as s:
   await s.initialize()
   async def c(t,n,a=None):
    q=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a or {}})
    if q.isError:raise RuntimeError((n,q.content))
    return json.loads(q.content[0].text)['returnValue']
   scene='editor_toolset.toolsets.scene.SceneTools';obj='editor_toolset.toolsets.object.ObjectTools';actor='editor_toolset.toolsets.actor.ActorTools';sl='SlateInspectorToolset.SlateInspectorToolset';app='EditorToolset.EditorAppToolset'
   async def find(n):
    a=await c(scene,'find_actors',{'name':n,'tag':'','collision_channels':[]});assert len(a)==1,(n,a);return a[0]
   async def props(a,*names):return json.loads(await c(obj,'get_properties',{'instance':a,'properties':list(names)}))
   async def key(k):await c(sl,'PressKey',{'key':k});await asyncio.sleep(.4)
   async def move(x,z=85):
    await c(actor,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':x,'y':0,'z':z}}});await asyncio.sleep(.9)
   async def shot(n):
    d=await c(app,'CaptureEditorImage');Path('tmp/stage3_new_'+n+'.png').write_bytes(base64.b64decode(d['data']))
   async def res(low):
    ss=await c(sl,'Snapshot',{'ref':'w1','maxDepth':100});gear=re.search(r'button "⚙".*?\[ref=(b\d+)\]',ss);assert gear
    await c(sl,'Click',{'ref':gear[1]});await asyncio.sleep(.4)
    ss=await c(sl,'Snapshot',{'ref':'w1','maxDepth':100});section=ss[ss.index('text "해상도"'):]
    button=re.search(r'button "'+('낮음' if low else '높음')+r'".*?\[ref=(b\d+)\]',section);close=re.search(r'button "닫기".*?\[ref=(b\d+)\]',section);assert button and close
    await c(sl,'Click',{'ref':button[1]});await asyncio.sleep(.3);await c(sl,'Click',{'ref':close[1]});await asyncio.sleep(.6)
   assert not await c(app,'IsPIERunning')
   await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':2}})
   try:
    pawn=await find('DirectorCutDragon');bloom=await find('Bloom_Controller');resctrl=await find('Resolution_Controller');crate=await find('Archive Empty Crate')
    clues=[await find('Bloom Shutter Clue '+n) for n in ('STAR','MOON','SUN')];decoder=await find('Film Decoder Low Resolution Clue')
    await c(sl,'Observe',{'ref':'w1','maxDepth':100});await c(sl,'Snapshot',{'ref':'w1','maxDepth':4});await c(sl,'Click',{'ref':'sp6'})
    await move(2250);print('BLOOM ON',await props(bloom,'bUseShutterPuzzle','bBloomOn'),[await props(x,'bHidden') for x in clues],flush=True);assert all([(await props(x,'bHidden'))['bHidden'] for x in clues])
    await shot('bloom_on');await key('B');assert all([not (await props(x,'bHidden'))['bHidden'] for x in clues]);await shot('bloom_off')
    await move(3900);await key('E');assert (await props(bloom,'bConsoleOpen'))['bConsoleOpen']
    await key('Two');await key('Enter');assert not (await props(bloom,'bSolved'))['bSolved'];await key('R');await key('One');await key('Three');await shot('bloom_console');await key('Enter');await asyncio.sleep(1.8);assert (await props(bloom,'bSolved'))['bSolved'];print('SHUTTERS PASS',flush=True)
    await move(5550);await res(False);assert (await props(decoder,'bHidden'))['bHidden'];await shot('resolution_high');await res(True);assert not (await props(decoder,'bHidden'))['bHidden'];await shot('resolution_low')
    await key('E');assert (await props(resctrl,'progress'))['progress']==0
    for x,p in ((5870,1),(5550,2),(6190,3)):
     await move(x);await key('E');v=await props(resctrl,'progress','bCompleted');print('REEL',x,v,flush=True);assert v['progress']==p
    assert (await props(resctrl,'bCompleted'))['bCompleted'];await move(6790);await key('E');assert (await props(crate,'bOpened'))['bOpened'];await shot('crate');print('REELS AND CRATE PASS',flush=True)
   finally:
    if await c(app,'IsPIERunning'):await c(app,'StopPIE')
asyncio.run(main())
