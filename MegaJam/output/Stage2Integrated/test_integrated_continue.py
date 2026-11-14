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
   sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools';sl='SlateInspectorToolset.SlateInspectorToolset';app='EditorToolset.EditorAppToolset'
   async def find(n):
    a=await c(sc,'find_actors',{'name':n,'tag':'','collision_channels':[]});return a[0]
   async def props(a,n):return json.loads(await c(ob,'get_properties',{'instance':a,'properties':n}))
   pawn=await find('Dragon');res=await find('Resolution_Controller');focus=await find('Focus_Controller');bloom=await find('Bloom_Controller');color=await find('Color_Controller');intro=(await c(sc,'find_actors',{'name':'Intro','tag':'','collision_channels':[]}))[-1];pp=await find('PostProcess')
   async def move(x,z=85):
    await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':x,'y':0,'z':z}}});await asyncio.sleep(.8)
   async def key(k):
    await c(sl,'PressKey',{'key':k});await asyncio.sleep(.35)
   await c(sl,'Observe',{'ref':'w1','maxDepth':25});await c(sl,'Snapshot',{'ref':'w1','maxDepth':25});await c(sl,'Click',{'ref':'sp6'})
   await move(2500);await key('E');print('FOCUS_ACTIVE',await props(focus,['bActive']),flush=True)
   assert (await props(focus,['bActive']))['bActive']
   for name,x,y in [('NearPiece',450,200),('FarPiece',500,-200)]:
    await c(ob,'set_properties',{'instance':{'refPath':focus['refPath']+'.'+name},'values':json.dumps({'relativeLocation':{'x':x,'y':y,'z':300}})})
   await key('Enter');await asyncio.sleep(2);print('FOCUS_DONE',await props(focus,['bSolved','exitDoor']),flush=True);assert (await props(focus,['bSolved']))['bSolved']
   await move(4800);print('BLOOM_WEIGHT',await props(pp,['blendWeight']),flush=True);await key('B');await move(6450);await key('E');print('BLOOM_ACTIVE',await props(bloom,['bConsoleOpen','bBloomOn']),flush=True)
   for k in ['One','Two','Three']:await key(k)
   await asyncio.sleep(2);print('BLOOM_DONE',await props(bloom,['bSolved']),flush=True);assert (await props(bloom,['bSolved']))['bSolved']
   await move(7550);print('POSTPROCESS_AFTER',await props(pp,['blendWeight']),flush=True);await key('E');print('COLOR_ACTIVE',await props(color,['bActive','dialValues']),flush=True);await key('Q')
   for k in ['One','One','Two','Two','Three']:await key(k)
   print('COLOR_DIALS',await props(color,['dialValues']),flush=True);await key('SpaceBar');await asyncio.sleep(2);print('COLOR_DONE',await props(color,['bSolved']),flush=True);assert (await props(color,['bSolved']))['bSolved']
   await c(app,'StopPIE',{});print('ALL_OK',flush=True)
asyncio.run(main())

