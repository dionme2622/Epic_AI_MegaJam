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
            st='SlateInspectorToolset.SlateInspectorToolset'
            await call(st,'Observe',{'ref':'w1'})
            await call(st,'Snapshot',{'ref':'w1','maxDepth':6})
            await call(st,'Click',{'ref':'sp5'})
            await call(st,'PressKey',{'key':'Q'})
            pref='/Game/Level/UEDPIE_0_Stage1.Stage1:PersistentLevel.'
            ctrl={'refPath':pref+'BP_Stage1Director_C_0'}
            for i in range(200):
                state=json.loads(await call('editor_toolset.toolsets.object.ObjectTools','get_properties',{'instance':ctrl,'properties':['IsLow','WheelX','WheelSolved']}))
                if not state['IsLow'] and 1150<state['WheelX']<1210:
                    await call(st,'PressKey',{'key':'Q'})
                    await asyncio.sleep(.3)
                    state=json.loads(await call('editor_toolset.toolsets.object.ObjectTools','get_properties',{'instance':ctrl,'properties':['IsLow','WheelX','WheelSolved']}))
                    gate=json.loads(await call('editor_toolset.toolsets.object.ObjectTools','get_properties',{'instance':{'refPath':pref+'StaticMeshActor_8'},'properties':['bHidden']}))
                    visual=await call('editor_toolset.toolsets.actor.ActorTools','get_actor_transform',{'actor':{'refPath':pref+'StaticMeshActor_10'}})
                    print('FINAL_WHEEL',state,'GATE',gate,'VISUAL',visual)
                    break
                await asyncio.sleep(.1)
            else: print('TIMEOUT',state)
asyncio.run(main())
