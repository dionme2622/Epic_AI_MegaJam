import asyncio
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def run():
    async with streamable_http_client('http://127.0.0.1:18765/mcp') as (r,w,_):
        async with ClientSession(r,w) as s:
            await s.initialize()
            async def c(t,n,args=None):
                result=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':args or {}})
                assert not result.isError, (n,result.content)
                return json.loads(result.content[0].text)['returnValue']
            app='EditorToolset.EditorAppToolset'; sc='editor_toolset.toolsets.scene.SceneTools'
            sl='SlateInspectorToolset.SlateInspectorToolset'; ob='editor_toolset.toolsets.object.ObjectTools'
            ac='editor_toolset.toolsets.actor.ActorTools'
            async def find(n):
                found=await c(sc,'find_actors',{'name':n,'tag':'','collision_channels':[]})
                assert len(found)==1,(n,found)
                return found[0]
            async def props(a,*keys):
                return json.loads(await c(ob,'get_properties',{'instance':a,'properties':keys}))
            async def key(k):
                await c(sl,'PressKey',{'key':k})
                await asyncio.sleep(.55)
            async def move(x,z=110):
                await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':x,'y':0,'z':z}}})
                await asyncio.sleep(.5)
            async def snapshot():
                return await c(sl,'Snapshot',{'ref':'w1','maxDepth':100})
            async def state():
                return await props(director,'IsLow','WheelX','WheelPushTarget','WheelSolved')
            assert not await c(app,'IsPIERunning')
            await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
            try:
                pawn=await find('Stage1_Player'); director=await find('Stage1_PuzzleDirector'); gate=await find('Stage1_GateBarrier')
                assert 'BP_Stage2WorkshopDirector' in director['refPath'], director
                await c(sl,'Observe',{'ref':'w1','maxDepth':100});await snapshot();await c(sl,'Click',{'ref':'sp6'})
                await key('E'); assert (await state())['WheelX']==440
                await move(345); assert 'Push the wheel' in await snapshot()
                await key('Q'); assert (await state())['IsLow']
                await key('E'); expected=await state(); print('FIRST PUSH',expected,flush=True); assert expected['WheelX']==620 and expected['IsLow']
                await asyncio.sleep(.7); assert (await state())['WheelX']==620
                await move(715); await key('E'); assert (await state())['WheelX']==440
                for x in (345,525,705,885):
                    await move(x); await key('E')
                solved=await state(); print('SOLVED',solved,flush=True)
                assert solved['WheelSolved'] and 1110 < solved['WheelX'] < 1320
                assert (await props(gate,'bHidden'))['bHidden']
                await move(8700,120); await key('M')
                assert (await props(director,'MenuOpen'))['MenuOpen']
                await key('Two'); assert not (await state())['IsLow']
                await key('M'); await key('E'); await asyncio.sleep(5.1)
                lift=await props(director,'LiftSolved','LiftAlpha'); print('LIFT',lift,flush=True)
                assert lift['LiftSolved'] and lift['LiftAlpha']>=229
            finally:
                if await c(app,'IsPIERunning'): await c(app,'StopPIE')

asyncio.run(run())
