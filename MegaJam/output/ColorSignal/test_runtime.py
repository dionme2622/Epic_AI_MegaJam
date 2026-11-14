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
   snap=await c(sl,'Snapshot',{'ref':'','maxDepth':3});win=re.search(r'\[ref=(w\d+)\]',snap).group(1)
   await c(sl,'Observe',{'ref':win,'maxDepth':30});await asyncio.sleep(1);snap=await c(sl,'Snapshot',{'ref':win,'maxDepth':30})
   print('Editor ready',flush=True)
   print('PLAY',await c(sl,'Click',{'ref':'b9'}),flush=True);await asyncio.sleep(3)
   await c(sl,'Snapshot',{'ref':win,'maxDepth':30});await c(sl,'Click',{'ref':'sp5'})
   p='/Game/Level/UEDPIE_0_Stage2_ColorSignal_Prototype.Stage2_ColorSignal_Prototype:PersistentLevel.'
   ctl={'refPath':p+'BP_ColorSignalPuzzle_C_0'};door={'refPath':p+'BP_S2_Door_C_0'}
   async def props(a,n):return json.loads(await c(obj,'get_properties',{'instance':a,'properties':n}))
   async def key(k):await c(sl,'PressKey',{'key':k});await asyncio.sleep(.4)
   async def image(name):
    z=await c('EditorToolset.EditorAppToolset','CaptureEditorImage',{});Path('output/ColorSignal/'+name+'.png').write_bytes(base64.b64decode(z['data']))
   print('INIT',await props(ctl,['bActive','bSolved','filterMode','dialValues']),flush=True)
   await key('E');print('ENTER',await props(ctl,['bActive']),flush=True);await image('full')
   for name in ['red','green','blue']:
    await key('Q');await image(name);print(name,await props(ctl,['filterMode']),flush=True)
   await key('SpaceBar');print('WRONG',await props(ctl,['bSolved']),flush=True)
   await key('One');print('INDEPENDENT',await props(ctl,['dialValues']),flush=True)
   for k in ['One','Two','Two','Three']:await key(k)
   print('ALIGNED',await props(ctl,['dialValues']),flush=True)
   await key('SpaceBar');print('SOLVED',await props(ctl,['bSolved']),flush=True);await image('solved')
   await asyncio.sleep(2.5);print('DONE',await props(ctl,['bActive','bSolved']),await props(door,['bOpen']),flush=True)
asyncio.run(main())
