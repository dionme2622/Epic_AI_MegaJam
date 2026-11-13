import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError: raise RuntimeError(str(z.content))
    return json.loads(z.content[0].text).get('returnValue')
   slate='SlateInspectorToolset.SlateInspectorToolset'; obj='editor_toolset.toolsets.object.ObjectTools'
   await c(slate,'Snapshot',{'ref':'','maxDepth':3}); print('OBS',await c(slate,'Observe',{'ref':'w3'}),flush=True); snap=await c(slate,'Snapshot',{'ref':'w3','maxDepth':12}); print('SNAP',str(snap)[-9000:],flush=True); print('CLICK',await c(slate,'Click',{'ref':'sp5'}),flush=True)
   actor={'refPath':'/Game/Level/UEDPIE_0_Stage2.Stage2:PersistentLevel.BP_Stage2Prototype_C_0'}
   async def st(): return json.loads(await c(obj,'get_properties',{'instance':actor,'properties':['bShadowsOn','bBloomOn','bExposureDark','bShadowSolved','sequenceProgress','bSequenceSolved','currentFilm','bFilmSolved','shadowPieceA','shadowPieceB']}))
   async def key(k): await c(slate,'PressKey',{'key':k}); await asyncio.sleep(.15)
   print('INITIAL',await st(),flush=True)
   for k in ['Q','B','N','Four','One','Two','Three','Seven','Eight','Nine','Enter']:
    await key(k)
   print('AFTER_KEYS',await st(),flush=True)
   await key('Q')
   for i in range(4): await key('G')
   for i in range(4): await key('J')
   print('AFTER_SHADOW',await st(),flush=True)
asyncio.run(main())
