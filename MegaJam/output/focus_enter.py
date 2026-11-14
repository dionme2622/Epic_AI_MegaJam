import asyncio,json,re
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(n,a):
    z=await s.call_tool('call_tool',{'toolset_name':'SlateInspectorToolset.SlateInspectorToolset','tool_name':n,'arguments':a});return json.loads(z.content[0].text).get('returnValue')
   snap=await c('Snapshot',{'ref':'','maxDepth':3});ref=re.search(r'\[ref=(w\d+)\]',snap).group(1)
   await c('Observe',{'ref':ref,'maxDepth':30});await asyncio.sleep(1);await c('Snapshot',{'ref':ref,'maxDepth':30});print(await c('Click',{'ref':'sp5'}));print(await c('PressKey',{'key':'E'}));await asyncio.sleep(1)
asyncio.run(main())
