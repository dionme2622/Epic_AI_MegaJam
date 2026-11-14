import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
    async with streamable_http_client("http://127.0.0.1:8000/mcp") as (r,w,_):
        async with ClientSession(r,w) as s:
            await s.initialize()
            async def c(t,n,a): 
                p=await s.call_tool("call_tool",{"toolset_name":t,"tool_name":n,"arguments":a})
                if p.isError: raise RuntimeError(p.content)
                return json.loads(p.content[0].text)["returnValue"]
            slate="SlateInspectorToolset.SlateInspectorToolset"
            await c(slate,"Observe",{"ref":"w1","maxDepth":100})
            import re
            snap=await c(slate,"Snapshot",{"ref":"w1","maxDepth":100})
            field=re.search(r'text "Cmd".*\n.*\n\s*textbox .*\[ref=(tb\d+)\]',snap)
            print(await c(slate,"Type",{"ref":field[1],"text":"py C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4Theatre/test_jumps_live.py","submit":True}))
            print(await c(slate,"Click",{"ref":"sp6"}))
asyncio.run(main())
