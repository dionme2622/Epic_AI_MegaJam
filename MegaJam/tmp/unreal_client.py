import asyncio
import json
import sys
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
    async with streamable_http_client('http://127.0.0.1:18765/mcp') as (read,write,_):
        async with ClientSession(read,write) as session:
            await session.initialize()
            if len(sys.argv)==1:
                result=await session.list_tools()
                print(json.dumps([{'name':t.name,'description':t.description,'inputSchema':t.inputSchema} for t in result.tools],ensure_ascii=False))
            elif sys.argv[1].startswith('@'):
                batch=json.loads(Path(sys.argv[1][1:]).read_text(encoding='utf8'))
                for entry in batch:
                    result=await session.call_tool(entry['name'],entry.get('arguments',{}))
                    print(json.dumps({'request':entry,'result':result.model_dump(mode='json')},ensure_ascii=False))
                    if result.isError: raise RuntimeError('MCP tool call failed: '+entry['name'])
            else:
                name=sys.argv[1]
                args=json.loads(sys.argv[2]) if len(sys.argv)>2 else {}
                result=await session.call_tool(name,args)
                print(result.model_dump_json())
                if result.isError: raise RuntimeError('MCP tool call failed')

asyncio.run(main())

