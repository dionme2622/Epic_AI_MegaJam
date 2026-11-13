import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
    async with streamable_http_client('http://127.0.0.1:8000/mcp') as (rd,wr,_):
        async with ClientSession(rd,wr) as s:
            await s.initialize()
            async def call(toolset,tool,args):
                response=await s.call_tool('call_tool',{'toolset_name':toolset,'tool_name':tool,'arguments':args})
                if response.isError: raise RuntimeError(str(response.content))
                return json.loads(response.content[0].text).get('returnValue')
            instance={'refPath':'/Game/Level/UEDPIE_0_Stage1.Stage1:PersistentLevel.BP_Stage1Director_C_0'}
            for i in range(200):
                state=json.loads(await call('editor_toolset.toolsets.object.ObjectTools','get_properties',{'instance':instance,'properties':['IsLow','WheelX','WheelDirection','WheelSolved']}))
                if state['IsLow']:
                    print('STATE_ALREADY_LOW',state); break
                if 1150<=state['WheelX']<=1210:
                    await call('SlateInspectorToolset.SlateInspectorToolset','PressKey',{'key':'Q'})
                    await asyncio.sleep(.3)
                    state=json.loads(await call('editor_toolset.toolsets.object.ObjectTools','get_properties',{'instance':instance,'properties':['IsLow','WheelX','WheelSolved']}))
                    hidden=json.loads(await call('editor_toolset.toolsets.object.ObjectTools','get_properties',{'instance':{'refPath':'/Game/Level/UEDPIE_0_Stage1.Stage1:PersistentLevel.StaticMeshActor_8'},'properties':['bHidden']}))
                    print('WHEEL_TEST',state,'GATE',hidden); break
                await asyncio.sleep(.1)
            else: print('WHEEL_TEST_TIMEOUT',state)
asyncio.run(main())
