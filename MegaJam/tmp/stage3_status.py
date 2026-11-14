import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:18765/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError:raise RuntimeError(f'{n}: {z.content}')
    return json.loads(z.content[0].text).get('returnValue')
   sc='editor_toolset.toolsets.scene.SceneTools';sl='SlateInspectorToolset.SlateInspectorToolset';app='EditorToolset.EditorAppToolset'
   print('PIE',await c(app,'IsPIERunning',{}),flush=True)
   print('WORLD',await c(sc,'find_actors',{'name':'WorldSettings','tag':'','collision_channels':[]}),flush=True)
   print('WINDOWS',await c(sl,'Snapshot',{'ref':'','maxDepth':3}),flush=True)
   await c(sl,'Observe',{'ref':'w1','maxDepth':40});snap=await c(sl,'Snapshot',{'ref':'w1','maxDepth':40});print('SAVE', '\n'.join(x for x in snap.splitlines() if 'Saved' in x or 'Unsaved' in x or 'tab "Stage' in x),flush=True)
asyncio.run(main())


