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
   sl='SlateInspectorToolset.SlateInspectorToolset';ob='editor_toolset.toolsets.object.ObjectTools';act='editor_toolset.toolsets.actor.ActorTools';app='EditorToolset.EditorAppToolset'
   if not await c(app,'IsPIERunning',{}):
    await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   snap=await c(sl,'Snapshot',{'ref':'','maxDepth':3});win=re.search(r'\[ref=(w\d+)\]',snap).group(1)
   await c(sl,'Observe',{'ref':win,'maxDepth':30});await c(sl,'Snapshot',{'ref':win,'maxDepth':30});await c(sl,'Click',{'ref':'sp5'})
   p='/Game/Level/UEDPIE_0_Stage2_BloomSign_Prototype.Stage2_BloomSign_Prototype:PersistentLevel.'
   ref=lambda n:{'refPath':p+n};ctl=ref('BP_BloomController_C_0');pawn=ref('DirectorCutDragon_0');door=ref('BP_S2_Door_C_0')
   async def props(a,n):return json.loads(await c(ob,'get_properties',{'instance':a,'properties':n}))
   async def key(k):await c(sl,'PressKey',{'key':k});await asyncio.sleep(.3)
   async def image(name):
    z=await c(app,'CaptureEditorImage',{});Path('output/BloomPuzzle/DetailRefined/'+name+'.png').write_bytes(base64.b64decode(z['data']))
   async def move(x):
    await c(act,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':x,'y':0,'z':92}}});await asyncio.sleep(.6)
   await move(350);await image('star_on');await key('B');await image('star_off')
   assert not (await props(ctl,['bBloomOn']))['bBloomOn']
   await move(900);await image('moon_off');await move(1450);await image('sun_off')
   await move(2000);await key('E');assert (await props(ctl,['bConsoleOpen']))['bConsoleOpen']
   await key('One');await key('Three');wrong=await props(ctl,['sequenceProgress','bSolved']);print('WRONG',wrong,flush=True);assert wrong['sequenceProgress']==0 and not wrong['bSolved']
   for k in ['One','Two','Three']:await key(k)
   await asyncio.sleep(2);result=await props(ctl,['sequenceProgress','bSolved']);d=await props(door,['bOpen']);print('SUCCESS',result,d,flush=True);assert result['bSolved'] and d['bOpen']
   await c(app,'StopPIE',{})
asyncio.run(main())
