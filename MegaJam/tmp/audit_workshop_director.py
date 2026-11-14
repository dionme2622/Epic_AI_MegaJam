import asyncio,json
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
    async with streamable_http_client('http://127.0.0.1:18765/mcp') as (r,w,_):
        async with ClientSession(r,w) as s:
            await s.initialize()
            name='editor_toolset.toolsets.blueprint.BlueprintTools'
            response=await s.call_tool('describe_toolset',{'toolset_name':name})
            tools=json.loads(response.content[0].text)['tools']
            for tool in tools:
                if any(word in tool['name'] for word in ('dsl','variable','parent')):
                    print(tool['name'], tool['inputSchema'])
            async def call(name,tool,arguments):
                out=await s.call_tool('call_tool',{'toolset_name':name,'tool_name':tool,'arguments':arguments})
                assert not out.isError,out.content
                return json.loads(out.content[0].text)['returnValue']
            for tool in tools:
                if tool['name'].endswith('.read_graph_dsl'):
                    p='/Game/Stage1Generated/BP_Stage1Director.BP_Stage1Director:EventGraph'
                    d=await call(name,'read_graph_dsl',{'graph':{'refPath':p}})
                    Path('tmp/stage2_live_original.dsl').write_text(d,encoding='utf-8')

asyncio.run(main())
