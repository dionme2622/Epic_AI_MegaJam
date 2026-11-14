import asyncio
import base64
import json
import re
import time
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def run():
    output = Path('tmp/stage3_take_bridge_qa')
    output.mkdir(exist_ok=True)
    command = Path('tmp/stage3_drive_command.json')
    result = Path('tmp/stage3_drive_result.json')
    command.unlink(missing_ok=True)
    result.unlink(missing_ok=True)
    async with streamable_http_client('http://127.0.0.1:18765/mcp') as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()

            async def call(toolset, name, arguments=None):
                response = await session.call_tool('call_tool', {'toolset_name': toolset, 'tool_name': name, 'arguments': arguments or {}})
                if response.isError:
                    raise RuntimeError((name, response.content))
                return json.loads(response.content[0].text)['returnValue']

            scene = 'editor_toolset.toolsets.scene.SceneTools'
            obj = 'editor_toolset.toolsets.object.ObjectTools'
            actor = 'editor_toolset.toolsets.actor.ActorTools'
            slate = 'SlateInspectorToolset.SlateInspectorToolset'
            app = 'EditorToolset.EditorAppToolset'

            async def find(name):
                targets = await call(scene, 'find_actors', {'name': name, 'tag': '', 'collision_channels': []})
                assert len(targets) == 1, (name, targets)
                return targets[0]

            async def props(target, *names):
                data = json.loads(await call(obj, 'get_properties', {'instance': target, 'properties': list(names)}))
                return {key if key.startswith('b') else key[0].lower() + key[1:]: value for key, value in data.items()}

            async def key(name):
                await call(slate, 'PressKey', {'key': name})
                await asyncio.sleep(.27)

            async def snapshot(depth=100):
                return await call(slate, 'Snapshot', {'ref': 'w1', 'maxDepth': depth})

            async def screenshot(name):
                data = await call(app, 'CaptureEditorImage')
                (output / f'{name}.png').write_bytes(base64.b64decode(data['data']))

            async def walk(x, fall=False):
                key_id = time.time_ns()
                command.write_text(json.dumps({'id': key_id, 'x': x, 'attempt_fall': fall}))
                for _ in range(250):
                    await asyncio.sleep(.12)
                    if result.exists():
                        try:
                            info = json.loads(result.read_text())
                        except ValueError:
                            continue
                        if info['id'] == key_id:
                            assert info['ok'], info
                            print('WALK', x, info['at'], flush=True)
                            return
                raise RuntimeError(f'Timed out walking to {x}')

            async def change_resolution(low):
                gear = re.search(r'button "⚙".*?\[ref=(b\d+)\]', await snapshot())
                assert gear
                await call(slate, 'Click', {'ref': gear[1]})
                await asyncio.sleep(.35)
                ui = await snapshot()
                section = ui[ui.index('text "해상도"'):]
                button = re.search(r'button "' + ('낮음' if low else '높음') + r'".*?\[ref=(b\d+)\]', section)
                close = re.search(r'button "닫기".*?\[ref=(b\d+)\]', section)
                assert button and close
                await call(slate, 'Click', {'ref': button[1]})
                await asyncio.sleep(.3)
                await call(slate, 'Click', {'ref': close[1]})
                await asyncio.sleep(.5)

            assert not await call(app, 'IsPIERunning')
            await call(scene, 'load_level', {'level_path': '/Game/DirectorCut/Stage/Stage3_'})
            await call(app, 'StartPIE', {'options': {'bSimulate': False, 'playMode': 'PlayMode_InViewPort', 'warmupSeconds': 2}})
            try:
                pawn = await find('DirectorCutDragon')
                take = await find('Two Takes Controller')
                bridge = await find('Resolution_Controller')
                crate = await find('Archive Empty Crate')
                left_platform = await find('Bridge Platform 1 Collision')
                right_platform = await find('Bridge Platform 2 Collision')
                await call(slate, 'Observe', {'ref': 'w1', 'maxDepth': 100})
                field = re.search(r'text "Cmd".*\n.*\n\s*textbox .*\[ref=(tb\d+)\]', await snapshot())
                assert field
                await call(slate, 'Type', {'ref': field[1], 'text': 'py C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/stage3_take_bridge_drive.py', 'submit': True})
                await snapshot(4)
                await call(slate, 'Click', {'ref': 'sp6'})
                await asyncio.sleep(3)
                # Start at the second puzzle. All subsequent routes use character movement and collision.
                await call(actor, 'set_actor_transform', {'actor': pawn, 'xform': {'location': {'x': 2950, 'y': 0, 'z': 58}}})
                await asyncio.sleep(.9)
                await key('E')
                state = await props(take, 'Phase', 'RecordedSeconds')
                print('RECORDING', state, flush=True)
                assert 'Recording' in str(state['phase'])
                await walk(2590)
                await asyncio.sleep(5.0)
                assert (await props(take, 'bLeftPressed'))['bLeftPressed']
                await key('E')
                state = await props(take, 'Phase', 'RecordedSeconds')
                print('REPLAY', state, flush=True)
                assert 'Playing' in str(state['phase'])
                await walk(3320)
                await screenshot('Take_Replay')
                await asyncio.sleep(1.3)
                assert (await props(take, 'bCompleted'))['bCompleted']
                print('TWO TAKES PASSED', flush=True)

                await walk(5360)
                await walk(5710, fall=True)
                assert not (await props(bridge, 'bCompleted'))['bCompleted']
                await key('E')
                assert (await props(bridge, 'bBridgeConsoleOpen'))['bBridgeConsoleOpen']
                await asyncio.sleep(1.0)
                await change_resolution(False)
                assert not (await props(bridge, 'bProjectionReadable'))['bProjectionReadable']
                await screenshot('Bridge_High')
                await change_resolution(True)
                assert (await props(bridge, 'bProjectionReadable'))['bProjectionReadable']
                await screenshot('Bridge_Low')
                await key('One')
                await key('Down')
                await asyncio.sleep(.5)
                assert (await props(bridge, 'BridgeNotches'))['bridgeNotches'] == [0, -2]
                local = await call(actor, 'get_actor_transform', {'actor': left_platform})
                assert abs(local['location']['z'] + 15) < 1, local
                await key('Two')
                await key('Up')
                await key('Up')
                await asyncio.sleep(1.3)
                assert (await props(bridge, 'bCompleted'))['bCompleted']
                local = await call(actor, 'get_actor_transform', {'actor': right_platform})
                assert abs(local['location']['z'] + 15) < 1, local
                await screenshot('Bridge_Aligned')
                await walk(6795)
                await asyncio.sleep(.2)
                assert 'Open the storage crate' in await snapshot()
                await key('E')
                assert (await props(crate, 'bOpened'))['bOpened']
                await asyncio.sleep(.85)
                subtitle = await snapshot()
                assert '원래 다리는 최종 보관소로 옮겼습니다.' in subtitle
                assert 'The real legs were moved to the final vault.' in subtitle
                await screenshot('Crate_Notice')
                await asyncio.sleep(2.15)
                await screenshot('Stage3_FadeOut')
                for _ in range(15):
                    await asyncio.sleep(.4)
                    destination = await call(scene, 'find_actors', {'name': 'Stage4_EntryFade', 'tag': '', 'collision_channels': []})
                    if destination:
                        assert '/Stage4.Stage4:' in destination[0]['refPath'] or 'UEDPIE_0_Stage4' in destination[0]['refPath'], destination
                        print('STAGE4 LOADED', destination, flush=True)
                        await screenshot('Stage4_Entry')
                        break
                else:
                    raise AssertionError('Opening the crate did not load Stage4')
            finally:
                command.unlink(missing_ok=True)
                if await call(app, 'IsPIERunning'):
                    await call(app, 'StopPIE')
                await call(scene, 'load_level', {'level_path': '/Game/DirectorCut/Prologue/L_BossPrologue'})


asyncio.run(run())
