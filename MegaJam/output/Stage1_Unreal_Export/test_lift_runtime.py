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
            pref='/Game/Level/UEDPIE_0_Stage1.Stage1:PersistentLevel.'
            player={'refPath':pref+'BP_Stage1Dragon_C_0'}
            ctrl={'refPath':pref+'BP_Stage1Director_C_0'}
            await call('editor_toolset.toolsets.actor.ActorTools','set_actor_transform',{'actor':player,'xform':{'location':{'x':8700,'y':0,'z':112},'rotation':{'pitch':0,'yaw':0,'roll':0},'scale':{'x':1,'y':1,'z':1}}})
            await asyncio.sleep(.5)
            await call('SlateInspectorToolset.SlateInspectorToolset','PressKey',{'key':'E'})
            await asyncio.sleep(.3)
            before=json.loads(await call('editor_toolset.toolsets.object.ObjectTools','get_properties',{'instance':ctrl,'properties':['IsLow','LiftActive','LiftAlpha']}))
            await call('SlateInspectorToolset.SlateInspectorToolset','PressKey',{'key':'Q'})
            await asyncio.sleep(.2)
            await call('SlateInspectorToolset.SlateInspectorToolset','PressKey',{'key':'E'})
            await asyncio.sleep(7.5)
            after=json.loads(await call('editor_toolset.toolsets.object.ObjectTools','get_properties',{'instance':ctrl,'properties':['IsLow','LiftActive','LiftAlpha','LiftSolved']}))
            player_transform=await call('editor_toolset.toolsets.actor.ActorTools','get_actor_transform',{'actor':player})
            lift_transform=await call('editor_toolset.toolsets.actor.ActorTools','get_actor_transform',{'actor':{'refPath':pref+'StaticMeshActor_9'}})
            print('LOW_TEST',before,'HIGH_TEST',after,'PLAYER',player_transform,'LIFT',lift_transform)
asyncio.run(main())
