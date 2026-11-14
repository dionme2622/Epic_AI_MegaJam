import asyncio,base64
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
import json
async def main():
    async with streamable_http_client("http://127.0.0.1:8000/mcp") as (r,w,_):
        async with ClientSession(r,w) as s:
            await s.initialize()
            reply = await s.call_tool("call_tool",{"toolset_name":"EditorToolset.EditorAppToolset","tool_name":"CaptureEditorImage","arguments":{}})
            if reply.isError: raise RuntimeError(reply.content)
            art=json.loads(reply.content[0].text)["returnValue"]
            Path("tmp/Stage4Theatre/stage4-overview.png").write_bytes(base64.b64decode(art["data"]))
asyncio.run(main())
