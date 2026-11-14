import asyncio, json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def run():
    async with streamable_http_client('http://127.0.0.1:18765/mcp') as (r,w,_):
        async with ClientSession(r,w) as s:
            await s.initialize()
            async def call(t,n,a=None):
                reply=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a or {}})
                assert not reply.isError, reply.content
                return json.loads(reply.content[0].text)['returnValue']
            scene='editor_toolset.toolsets.scene.SceneTools'
            actor='editor_toolset.toolsets.actor.ActorTools'
            app='EditorToolset.EditorAppToolset'
            obj='editor_toolset.toolsets.object.ObjectTools'
            slate='SlateInspectorToolset.SlateInspectorToolset'
            await call(scene,'load_level',{'level_path':'/Game/DirectorCut/Stage/Stage4'})
            await call(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
            try:
                await call(slate,'Observe',{'ref':'w1','maxDepth':100})
                await asyncio.sleep(1.5)
                for n in ('Color_Controller','DirectorCutDragon','RGB Light Panel','Vault RGB'):
                    for a in await call(scene,'find_actors',{'name':n,'tag':'','collision_channels':[]}):
                        print(n,a,await call(actor,'get_actor_transform',{'actor':a}),flush=True)
                        if n=='Color_Controller':
                            print(await call(obj,'get_properties',{'instance':a,'properties':['bSolved','bActive','InteractDistance']}),flush=True)
            finally:
                await call(app,'StopPIE')
asyncio.run(run())
