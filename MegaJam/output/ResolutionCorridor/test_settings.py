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
   sl='SlateInspectorToolset.SlateInspectorToolset'
   await c(sl,'Observe',{'ref':'w1','maxDepth':100});snap=await c(sl,'Snapshot',{'ref':'sp6','maxDepth':100})
   print('VIEW',snap,flush=True)
   await c(sl,'Click',{'ref':'b58'});await asyncio.sleep(.3)
   snap=await c(sl,'Snapshot',{'ref':'sp6','maxDepth':100});print('MENU',snap,flush=True);Path('output/ResolutionCorridor/menu.txt').write_text(snap,encoding='utf8')
asyncio.run(main())
