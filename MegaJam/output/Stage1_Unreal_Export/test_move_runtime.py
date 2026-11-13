import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
    async with streamable_http_client('http://127.0.0.1:8000/mcp') as (rd,wr,_):
        async with ClientSession(rd,wr) as s:
            await s.initialize()
            async def call(ts,tool,args):
                r=await s.call_tool('call_tool',{'toolset_name':ts,'tool_name':tool,'arguments':args})
                if r.isError: raise RuntimeError(str(r.content))
                return json.loads(r.content[0].text).get('returnValue')
            player={'refPath':'/Game/Level/UEDPIE_0_Stage1.Stage1:PersistentLevel.BP_Stage1Dragon_C_0'}
            get=lambda: call('editor_toolset.toolsets.actor.ActorTools','get_actor_transform',{'actor':player})
            print('BEFORE',await get())
            for i in range(30):
                await call('SlateInspectorToolset.SlateInspectorToolset','PressKey',{'key':'D'})
                await asyncio.sleep(.03)
            print('AFTER',await get())
asyncio.run(main())
