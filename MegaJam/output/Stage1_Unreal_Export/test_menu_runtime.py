import asyncio,json,re
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
            slate='SlateInspectorToolset.SlateInspectorToolset'
            ctrl={'refPath':'/Game/Level/UEDPIE_0_Stage1.Stage1:PersistentLevel.BP_Stage1Director_C_0'}
            async def state():
                return json.loads(await call('editor_toolset.toolsets.object.ObjectTools','get_properties',{'instance':ctrl,'properties':['MenuOpen','IsLow','ShadowOff']}))
            await call(slate,'Observe',{'ref':'w1'})
            snap=await call(slate,'Snapshot',{'ref':'w1','maxDepth':6})
            print('SNAP',str(snap)[:1600])
            await call(slate,'Click',{'ref':'sp5'})
            print('INITIAL',await state())
            for key in ('M','2','1','3','M'):
                await call(slate,'PressKey',{'key':key})
                await asyncio.sleep(.3)
                print('AFTER',key,await state())
asyncio.run(main())
