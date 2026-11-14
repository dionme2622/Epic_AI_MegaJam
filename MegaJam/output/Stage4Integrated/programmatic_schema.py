import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize();z=await s.call_tool('describe_toolset',{'toolset_name':'editor_toolset.toolsets.programmatic.ProgrammaticToolset'});print(z.content[0].text)
asyncio.run(main())
