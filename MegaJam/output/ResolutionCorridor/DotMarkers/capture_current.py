import asyncio,json,base64
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   z=await s.call_tool('call_tool',{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'CaptureEditorImage','arguments':{}})
   if z.isError:raise RuntimeError(str(z.content))
   Path('output/ResolutionCorridor/DotMarkers/current.png').write_bytes(base64.b64decode(json.loads(z.content[0].text)['returnValue']['data']))
asyncio.run(main())
