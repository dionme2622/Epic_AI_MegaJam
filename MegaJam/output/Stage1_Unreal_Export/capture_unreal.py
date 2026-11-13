import asyncio, base64, json
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
    async with streamable_http_client('http://127.0.0.1:8000/mcp') as (rd,wr,_):
        async with ClientSession(rd,wr) as s:
            await s.initialize()
            r=await s.call_tool('call_tool',{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'CaptureEditorImage','arguments':{}})
            for item in r.content:
                if item.type=='text':
                    image=json.loads(item.text)['returnValue']
                    Path(r'C:\LHH\Epic_AI_MegaJam\MegaJam\output\Stage1_Unreal_Export\playtest.png').write_bytes(base64.b64decode(image['data']))
                    print('CAPTURE_OK')
asyncio.run(main())
