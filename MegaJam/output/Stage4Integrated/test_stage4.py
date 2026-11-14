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
   async def key(k):await c(sl,'PressKey',{'key':k});await asyncio.sleep(.35)
   assert not await c(app,'IsPIERunning',{})
   await c(sc,'load_level',{'level_path':'/Game/DirectorCut/Stage/Stage4'});await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   pawn=next(x for x in await c(sc,'find_actors',{'name':'Dragon','tag':'','collision_channels':[]}) if 'DirectorCutDragon' in x['refPath']);color=await find('Color_Controller');body=await find('Dragon_LowerBody_Collectible');checkpoint=await find('ShadowStage_FallCheckpoint');pp=await find('FinalShadow_ColorGrade')
   print('LOCATIONS',await c(ac,'get_actor_transform',{'actor':body}),await c(ac,'get_actor_transform',{'actor':checkpoint}),flush=True)
   async def move(x,z=85):await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':x,'y':0,'z':z}}});await asyncio.sleep(.8)
   async def image(n):
    z=await c(app,'CaptureEditorImage',{});Path('output/Stage4Integrated/'+n+'.png').write_bytes(base64.b64decode(z['data']))
   await c(sl,'Observe',{'ref':'w1','maxDepth':80});await c(sl,'Snapshot',{'ref':'w1','maxDepth':80});await c(sl,'Click',{'ref':'sp6'})
   await move(0);await key('E');print('COLOR_ACTIVE',await props(color,['bActive','dialValues']),flush=True);assert (await props(color,['bActive']))['bActive']
   await key('Q')
   for k in ['One','One','Two','Two','Three']:await key(k)
   print('COLOR_DIALS',await props(color,['dialValues']),flush=True);await key('SpaceBar');await asyncio.sleep(2);print('COLOR_DONE',await props(color,['bSolved']),flush=True);assert (await props(color,['bSolved']))['bSolved']
   await move(2620);await asyncio.sleep(1);await image('shadow_on')
   snap=await c(sl,'Snapshot',{'ref':'w1','maxDepth':100});gear=re.search(r'button "⚙".*?\[ref=(b\d+)\]',snap).group(1);await c(sl,'Click',{'ref':gear});await asyncio.sleep(.5);snap=await c(sl,'Snapshot',{'ref':'w1','maxDepth':100})
   if 'text "그림자"' not in snap:await key('Enter');snap=await c(sl,'Snapshot',{'ref':'w1','maxDepth':100})
   after=snap[snap.index('text "그림자"'):];low=re.search(r'button "낮음".*?\[ref=(b\d+)\]',after).group(1);close=re.search(r'button "닫기".*?\[ref=(b\d+)\]',after).group(1)
   await c(sl,'Click',{'ref':low});await key('Enter');await c(sl,'Click',{'ref':close});await key('Enter');await asyncio.sleep(1);await image('shadow_off')
   await move(2200,-150);await asyncio.sleep(1.5);p=await c(ac,'get_actor_transform',{'actor':pawn});print('CHECKPOINT',p,flush=True);assert 1350<p['location']['x']<1600
   await move(3940,150);await asyncio.sleep(1);st=await props(body,['Collected','bHidden']);print('GOAL',st,flush=True);assert st['Collected'] and st['bHidden']
   await c(app,'StopPIE',{});print('STAGE4_OK',flush=True)
asyncio.run(main())
