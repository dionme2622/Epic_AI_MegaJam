import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def run():
    async with streamable_http_client('http://127.0.0.1:18765/mcp') as (read, write, _):
        async with ClientSession(read, write) as client:
            await client.initialize()

            async def call(toolset, name, arguments=None):
                reply = await client.call_tool('call_tool', {'toolset_name': toolset, 'tool_name': name, 'arguments': arguments or {}})
                if reply.isError:
                    raise RuntimeError((name, reply.content))
                return json.loads(reply.content[0].text)['returnValue']

            scene = 'editor_toolset.toolsets.scene.SceneTools'
            app = 'EditorToolset.EditorAppToolset'
            actor = 'editor_toolset.toolsets.actor.ActorTools'
            obj = 'editor_toolset.toolsets.object.ObjectTools'

            async def find(name):
                return await call(scene, 'find_actors', {'name': name, 'tag': '', 'collision_channels': []})

            async def wait_for(name, map_name, attempts=65):
                for _ in range(attempts):
                    for item in await find(name):
                        if f'UEDPIE_0_{map_name}.{map_name}' in item['refPath']:
                            print('Reached', map_name, item['refPath'], flush=True)
                            return item
                    await asyncio.sleep(.35)
                raise RuntimeError(f'Did not reach {map_name} ({name})')

            async def approach_exit(pawn, exit_ref, z):
                result = json.loads(await call(obj, 'get_properties', {'instance': exit_ref, 'properties': ['ExitX', 'TransitionStarted']}))
                assert not result['TransitionStarted'], result
                x = result['ExitX']
                print('Approaching exit at X', x, flush=True)
                await call(actor, 'set_actor_transform', {'actor': pawn, 'xform': {'location': {'x': x + 10, 'y': 0, 'z': z}}})
                await asyncio.sleep(.3)
                assert json.loads(await call(obj, 'get_properties', {'instance': exit_ref, 'properties': ['TransitionStarted']}))['TransitionStarted']

            assert not await call(app, 'IsPIERunning')
            await call(scene, 'load_level', {'level_path': '/Game/DirectorCut/Prologue/L_BossPrologue'})
            await call(app, 'StartPIE', {'options': {'bSimulate': False, 'playMode': 'PlayMode_InViewPort', 'warmupSeconds': 1}})
            try:
                print('Playing the prologue sequence to its end', flush=True)
                castle_exit = await wait_for('Stage1_RightExit_Fade', 'L_Stage1')
                dragon = next(a for a in await find('Dragon') if 'UEDPIE_0_L_Stage1' in a['refPath'])
                await approach_exit(dragon, castle_exit, 55)

                workshop_exit = await wait_for('Stage2_To_Stage3_FadeExit', 'Stage2')
                dragon = next(a for a in await find('Stage1_Player') if 'UEDPIE_0_Stage2' in a['refPath'])
                await approach_exit(dragon, workshop_exit, 380)

                await wait_for('Stage3_EntryFade', 'Stage3_')
                for _ in range(12):
                    if await find('Two Takes Controller'):
                        break
                    await asyncio.sleep(.25)
                else:
                    raise AssertionError('The streamed Two Takes puzzle did not load')
                print('Prologue through Stage3 joined correctly', flush=True)
            finally:
                if await call(app, 'IsPIERunning'):
                    await call(app, 'StopPIE')


asyncio.run(run())
