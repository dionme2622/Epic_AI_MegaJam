import asyncio, json, re, sys
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def run(command):
    async with streamable_http_client("http://127.0.0.1:18765/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            async def call(toolset, name, arguments=None):
                reply=await session.call_tool("call_tool", {"toolset_name":toolset,"tool_name":name,"arguments":arguments or {}})
                if reply.isError: raise RuntimeError(reply.content)
                return json.loads(reply.content[0].text)["returnValue"]
            app="EditorToolset.EditorAppToolset"
            slate="SlateInspectorToolset.SlateInspectorToolset"
            assert not await call(app,"IsPIERunning")
            await call(slate,"Observe",{"ref":"w1","maxDepth":100})
            ss=await call(slate,"Snapshot",{"ref":"w1","maxDepth":100})
            m=re.search(r'text "Cmd".*\n.*\n\s*textbox .*\[ref=(tb\d+)\]',ss)
            assert m
            await call(slate,"Click",{"ref":m[1]})
            print(await call(slate,"Type",{"ref":m[1],"text":command,"submit":True}))
asyncio.run(run(" ".join(sys.argv[1:])))

