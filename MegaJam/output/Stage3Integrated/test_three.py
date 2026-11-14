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
    if z.isError:raise RuntimeError(f'{n}: {z.content}')
    return json.loads(z.content[0].text).get('returnValue')
   sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools';sl='SlateInspectorToolset.SlateInspectorToolset';app='EditorToolset.EditorAppToolset'
   async def find(n):
    a=await c(sc,'find_actors',{'name':n,'tag':'','collision_channels':[]});assert a,n;return a[0]
   async def props(a,n):return json.loads(await c(ob,'get_properties',{'instance':a,'properties':n}))
   async def key(k):await c(sl,'PressKey',{'key':k});await asyncio.sleep(.4)
   await c(sc,'load_level',{'level_path':'/Game/Level/Stage3_Integrated'});await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   pawn=next(x for x in await c(sc,'find_actors',{'name':'Dragon','tag':'','collision_channels':[]}) if 'DirectorCutDragon' in x['refPath']);focus=await find('Focus_Controller');bloom=await find('Bloom_Controller');res=await find('Resolution_Controller');pp=await find('PostProcess')
   async def move(x,z=85):await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':x,'y':0,'z':z}}});await asyncio.sleep(.85)
   print('RESOLUTION_CONFIG',await props(res,['bRestrictOverlayStart','showOverlayFromOffsetX','bUseLocalCheckpoint']),flush=True)
   print('BLOOM_INITIAL_WEIGHT',await props(pp,['blendWeight']),flush=True)
   await asyncio.sleep(7);await c(sl,'Observe',{'ref':'w1','maxDepth':80});snap=await c(sl,'Snapshot',{'ref':'w1','maxDepth':80})
   # The editor viewport is the large splitter containing the in-game settings button.
   await c(sl,'Click',{'ref':'sp6'});await move(0);await key('E');print('FOCUS_ACTIVE',await props(focus,['bActive']),flush=True)
   if not (await props(focus,['bActive']))['bActive']:raise RuntimeError('Focus puzzle did not start')
   for name,x,y in [('NearPiece',450,200),('FarPiece',500,-200)]:await c(ob,'set_properties',{'instance':{'refPath':focus['refPath']+'.'+name},'values':json.dumps({'relativeLocation':{'x':x,'y':y,'z':300}})})
   await key('Enter');await asyncio.sleep(2);print('FOCUS_SOLVED',await props(focus,['bSolved']),flush=True);assert (await props(focus,['bSolved']))['bSolved']
   await move(2200);print('BLOOM_WEIGHT_IN',await props(pp,['blendWeight']),flush=True);await key('B');await move(3900);await key('E');print('BLOOM_ACTIVE',await props(bloom,['bConsoleOpen','bBloomOn']),flush=True)
   for k in ['One','Two','Three']:await key(k)
   await asyncio.sleep(2);print('BLOOM_SOLVED',await props(bloom,['bSolved']),flush=True);assert (await props(bloom,['bSolved']))['bSolved']
   await move(4750);print('BLOOM_WEIGHT_OUT',await props(pp,['blendWeight']),flush=True)
   await move(5550);print('RES_SAFE',await props(res,['progress','bFailing']),flush=True);assert (await props(res,['progress']))['progress']==1
   await move(5710);await asyncio.sleep(2);pos=await c(ac,'get_actor_transform',{'actor':pawn});state=await props(res,['progress','bFailing']);print('RES_RETRY',pos,state,flush=True);assert 4650<pos['location']['x']<4900 and state['progress']==0
   for x in [5550,5870,6190]:await move(x)
   print('RES_SOLVED',await props(res,['progress','bCompleted']),flush=True);assert (await props(res,['bCompleted']))['bCompleted']
   await c(app,'StopPIE',{});print('THREE_OK',flush=True)
asyncio.run(main())
