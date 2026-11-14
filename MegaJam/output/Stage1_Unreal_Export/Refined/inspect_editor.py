import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   for n,a in [('Observe',{'ref':'w1','maxDepth':30}),('Snapshot',{'ref':'w1','maxDepth':30})]:
    z=await s.call_tool('call_tool',{'toolset_name':'SlateInspectorToolset.SlateInspectorToolset','tool_name':n,'arguments':a})
    if n=='Snapshot':
     val=json.loads(z.content[0].text)['returnValue']
     print('\n'.join(x for x in val.splitlines() if any(v in x for v in ['Saved','Unsaved','tab "'])))
asyncio.run(main())
