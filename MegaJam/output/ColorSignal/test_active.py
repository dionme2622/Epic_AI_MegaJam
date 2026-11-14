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
   sl='SlateInspectorToolset.SlateInspectorToolset';obj='editor_toolset.toolsets.object.ObjectTools'
   await c(sl,'Snapshot',{'ref':'','maxDepth':3});await c(sl,'Observe',{'ref':'w1','maxDepth':30});await c(sl,'Snapshot',{'ref':'w1','maxDepth':30});await c(sl,'Click',{'ref':'sp5'})
   p='/Game/Level/UEDPIE_0_Stage2_ColorSignal_Prototype.Stage2_ColorSignal_Prototype:PersistentLevel.'
   ctl={'refPath':p+'BP_ColorSignalPuzzle_C_0'};door={'refPath':p+'BP_S2_Door_C_0'}
   async def props(a,n):return json.loads(await c(obj,'get_properties',{'instance':a,'properties':n}))
   async def key(k):
    print(k,await c(sl,'PressKey',{'key':k}),flush=True);await asyncio.sleep(.5)
   await key('E');print('ACTIVE',await props(ctl,['bActive']),flush=True)
   await key('SpaceBar');print('WRONG',await props(ctl,['bSolved']),flush=True)
   for k in ['One','One','Three','Four','Four','Four']:await key(k)
   print('ALIGNED',await props(ctl,['dialValues']),flush=True)
   await key('SpaceBar');print('SOLVED',await props(ctl,['bSolved']),flush=True)
   z=await c('EditorToolset.EditorAppToolset','CaptureEditorImage',{});Path('output/ColorSignal/solved.png').write_bytes(base64.b64decode(z['data']))
   await asyncio.sleep(2.5);print('DONE',await props(ctl,['bActive','bSolved']),await props(door,['bOpen']),flush=True)
asyncio.run(main())
