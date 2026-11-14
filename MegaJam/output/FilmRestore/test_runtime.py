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
   sl='SlateInspectorToolset.SlateInspectorToolset';obj='editor_toolset.toolsets.object.ObjectTools'
   snap=await c(sl,'Snapshot',{'ref':'','maxDepth':3});win=re.search(r'\[ref=(w\d+)\]',snap).group(1);await c(sl,'Observe',{'ref':win,'maxDepth':30});await asyncio.sleep(1);await c(sl,'Snapshot',{'ref':win,'maxDepth':30});print('CLICK',await c(sl,'Click',{'ref':'sp5'}),flush=True)
   p='/Game/Level/UEDPIE_0_Stage2_FilmRestore_Prototype.Stage2_FilmRestore_Prototype:PersistentLevel.';ctl={'refPath':p+'BP_FilmRestorePuzzle_C_0'};door={'refPath':p+'BP_S2_Door_C_0'}
   async def props(a,n):return json.loads(await c(obj,'get_properties',{'instance':a,'properties':n}))
   async def key(k):await c(sl,'PressKey',{'key':k});await asyncio.sleep(.3)
   async def image(name):
    z=await c('EditorToolset.EditorAppToolset','CaptureEditorImage',{});Path('output/FilmRestore/'+name+'.png').write_bytes(base64.b64decode(z['data']))
   print('INIT',await props(ctl,['bActive','bSolved','currentFilm','bBloomOn','bShadowOn','bDarkExposure']),flush=True)
   await key('E');print('ENTER',await props(ctl,['bActive']),flush=True);await image('film_A_on')
   await key('B');await image('film_A_off')
   await key('Two');await image('film_B_shadow_on');await key('Q');await image('film_B_shadow_off')
   await key('Three');await image('film_C_bright');await key('N');await image('film_C_dark')
   await key('Enter');print('WRONG',await props(ctl,['bSolved','sceneChoice','directionChoice','markChoice']),flush=True)
   for k in ['Four','Four','Five','Six','Six','Enter']:await key(k)
   print('RECORD',await props({'refPath':p+'BP_FilmRestorePuzzle_C_0.RestoredRecord'},['bVisible','text']),flush=True);await image('film_restored')
   await asyncio.sleep(2.5);print('COMPLETE',await props(ctl,['bActive','bSolved','sceneChoice','directionChoice','markChoice']),await props(door,['bOpen']),flush=True)
asyncio.run(main())
