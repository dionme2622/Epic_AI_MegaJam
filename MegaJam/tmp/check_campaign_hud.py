import asyncio
import base64
import json
import re
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def run():
    output = Path('tmp/campaign_hud_qa')
    output.mkdir(exist_ok=True)
    async with streamable_http_client('http://127.0.0.1:18765/mcp') as (reader, writer, _):
        async with ClientSession(reader, writer) as session:
            await session.initialize()

            async def call(toolset, name, arguments=None):
                response = await session.call_tool('call_tool', {'toolset_name': toolset, 'tool_name': name, 'arguments': arguments or {}})
                if response.isError:
                    raise RuntimeError((name, response.content))
                return json.loads(response.content[0].text)['returnValue']

            app = 'EditorToolset.EditorAppToolset'
            scene = 'editor_toolset.toolsets.scene.SceneTools'
            actor = 'editor_toolset.toolsets.actor.ActorTools'
            slate = 'SlateInspectorToolset.SlateInspectorToolset'

            async def find(name):
                values = await call(scene, 'find_actors', {'name': name, 'tag': '', 'collision_channels': []})
                assert len(values) == 1, (name, values)
                return values[0]

            async def move(name, x, z):
                await call(actor, 'set_actor_transform', {'actor': await find(name), 'xform': {'location': {'x': x, 'y': 0, 'z': z}}})
                await asyncio.sleep(.9)

            async def snap():
                return await call(slate, 'Snapshot', {'ref': 'w1', 'maxDepth': 100})

            async def expect(condition, label):
                for _ in range(18):
                    state = await snap()
                    if condition(state):
                        print('PASS', label, flush=True)
                        return state
                    await asyncio.sleep(.22)
                (output / f'{label}.txt').write_text(state, encoding='utf8')
                raise AssertionError(label)

            async def capture(label):
                shot = await call(app, 'CaptureEditorImage')
                (output / f'{label}.png').write_bytes(base64.b64decode(shot['data']))

            async def begin(path):
                await call(scene, 'load_level', {'level_path': path})
                await call(app, 'StartPIE', {'options': {'bSimulate': False, 'playMode': 'PlayMode_InViewPort', 'warmupSeconds': 1}})
                await call(slate, 'Observe', {'ref': 'w1', 'maxDepth': 100})

            async def end():
                if await call(app, 'IsPIERunning'):
                    await call(app, 'StopPIE')

            try:
                await begin('/Game/DirectorCut/Stage1/L_Stage1')
                await expect(lambda s: '그럼 내가 직접 찾으러 가지' in s and "I'll go find them myself" in s, 'Stage1_Subtitle')
                await capture('Stage1_Subtitle')
                await expect(lambda s: 'Move with A / D' in s, 'Stage1_Hint')
                await end()

                await begin('/Game/DirectorCut/Stage/Stage2')
                await expect(lambda s: '작업용 휠체어' in s and 'A workshop wheelchair' in s, 'Stage2_Subtitle')
                await move('Stage1_Player', 500, 110)
                await expect(lambda s: 'Set High to roll the wheel' in s and '높음으로 바꿔 바퀴 굴리기' in s, 'Stage2_Wheel_Key')
                await capture('Stage2_Wheel_Key')
                await move('Stage1_Player', 8700, 120)
                await expect(lambda s: 'Set model detail to High' in s, 'Stage2_Lift_Key')
                await end()

                await begin('/Game/DirectorCut/Stage/Stage3_')
                await expect(lambda s: 'Adjust focus' in s and '초점 조절' in s, 'Stage3_Focus_Key')
                await capture('Stage3_Focus_Key')
                await move('DirectorCutDragon', 2950, 58)
                await expect(lambda s: 'Record the first take' in s, 'Stage3_Record_Key')
                await move('DirectorCutDragon', 5360, 58)
                await expect(lambda s: 'Operate the film desk' in s, 'Stage3_Film_Key')
                await capture('Stage3_Film_Key')
                await end()

                await begin('/Game/DirectorCut/Stage/Stage4')
                state = await expect(lambda s: 'Calibrate the lights' in s and '색 조명 조절' in s, 'Stage4_RGB_Key')
                await capture('Stage4_RGB_Key')
                gear = re.search(r'button "⚙".*?\[ref=(b\d+)\]', state)
                assert gear
                await call(slate, 'Click', {'ref': gear[1]})
                await expect(lambda s: 'Calibrate the lights' not in s and '그래픽 설정' in s, 'Settings_Hides_Prompt')
                await end()
            finally:
                await end()
                await call(scene, 'load_level', {'level_path': '/Game/DirectorCut/Prologue/L_BossPrologue'})


asyncio.run(run())
