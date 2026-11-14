import asyncio
import json
import re
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

SOURCE = '/Game/Stage1Generated/BP_Stage1Director'
TARGET = '/Game/Stage2Workshop/BP_Stage2WorkshopDirector'


def remove_top_level_blocks(text, predicate):
    lines = text.splitlines()
    result = []
    index = 0
    while index < len(lines):
        if lines[index].startswith('  (') and predicate(lines[index]):
            index += 1
            while index < len(lines) and lines[index].startswith('    '):
                index += 1
        else:
            result.append(lines[index])
            index += 1
    return '\n'.join(result)


def make_graph(original):
    graph = remove_top_level_blocks(original, lambda line: '"Q"' in line and '(if ' in line)
    graph = graph.replace('(Variables|Default|SetWheelDirection 1.0)', '(Variables|Default|SetWheelPushTarget 440.0)', 1)
    graph = re.sub(r'\n  \(Development\|PrintString "A/D:[^\n]+\)\)', ')', graph, count=1)
    graph = re.sub(r'\n    \(if _islow\n      \(Development\|PrintString[^\n]+\n      \(else\n        \(Development\|PrintString[^\n]+', ')', graph, count=1)
    auto_roll = graph.index('  (if (and (and (not (Variables|Default|GetIsLow)) (not (Variables|Default|GetWheelSolved)))')
    wheel_models = graph.index('  (bind _outactors (Actor|GetAllActorsWithTag "WheelPiece"))', auto_roll)
    graph = graph[:auto_roll] + '''  (bind playerX (.x _returnvalue_2))
  (bind target (Variables|Default|GetWheelPushTarget))
  (if (and (and (not (Variables|Default|GetMenuOpen)) (not (Variables|Default|GetWheelSolved))) (Game|Player|WasInputKeyJustPressed _returnvalue "E"))
    (if (and (and (> playerX (- _wheelx 220.0)) (< playerX (+ _wheelx 220.0))) (and (> (.z _returnvalue_2) 0.0) (< (.z _returnvalue_2) 310.0)))
      (if (and (< (- target _wheelx) 4.0) (> (- target _wheelx) -4.0))
        (if (<= playerX _wheelx)
          (Variables|Default|SetWheelPushTarget (select (> (+ _wheelx 180.0) 1420.0) 1420.0 (+ _wheelx 180.0)))
          (else
            (Variables|Default|SetWheelPushTarget (select (< (- _wheelx 180.0) 440.0) 440.0 (- _wheelx 180.0))))))))
  (if (and (not (Variables|Default|GetMenuOpen)) (not (Variables|Default|GetWheelSolved)))
    (bind step (* DeltaSeconds 540.0))
    (Variables|Default|SetWheelX
      (select (< _wheelx target)
        (select (< (+ _wheelx step) target) (+ _wheelx step) target)
        (select (> (- _wheelx step) target) (- _wheelx step) target))))
''' + graph[wheel_models:]
    graph = re.sub(r'\n    \(Development\|PrintString "WHEEL PUZZLE COMPLETE[^\n]+\)\)', ')', graph, count=1)
    lift_begin = graph.index('  (if (and (not (Variables|Default|GetMenuOpen)) (Game|Player|WasInputKeyJustPressed _returnvalue "E"))')
    lift_gears = graph.index('  (bind _outactors_1 (Actor|GetAllActorsWithTag "GearHigh"))', lift_begin)
    graph = graph[:lift_begin] + '''  (if (and (and (not (Variables|Default|GetMenuOpen)) (not (Variables|Default|GetLiftActive))) (Game|Player|WasInputKeyJustPressed _returnvalue "E"))
    (if (and (> playerX 8585.0) (< playerX 8800.0))
      (if (and (and (> (.z _returnvalue_2) (+ (Variables|Default|GetLiftAlpha) 90.0)) (< (.z _returnvalue_2) (+ (Variables|Default|GetLiftAlpha) 150.0))) (not _islow_1))
        (Variables|Default|SetLiftDescending (> (Variables|Default|GetLiftAlpha) 115.0))
        (Variables|Default|SetLiftActive true)
        (Input|SetIgnoreMoveInput _returnvalue true))))
''' + graph[lift_gears:]
    assert graph.count('(') == graph.count(')') and 'PrintString' not in graph and '"Q"' not in graph
    return graph


async def run():
    async with streamable_http_client('http://127.0.0.1:18765/mcp') as (r,w,_):
        async with ClientSession(r,w) as s:
            await s.initialize()
            async def call(toolset, name, args=None):
                reply = await s.call_tool('call_tool', {'toolset_name':toolset, 'tool_name':name, 'arguments':args or {}})
                if reply.isError:
                    raise RuntimeError((name, reply.content))
                return json.loads(reply.content[0].text)['returnValue']

            bp = 'editor_toolset.toolsets.blueprint.BlueprintTools'
            asset = 'editor_toolset.toolsets.asset.AssetTools'
            app = 'EditorToolset.EditorAppToolset'
            slate = 'SlateInspectorToolset.SlateInspectorToolset'
            if await call(app, 'IsPIERunning'):
                await call(app, 'StopPIE')

            def ref(path):
                return {'refPath': path}

            await call(slate, 'Observe', {'ref':'w1','maxDepth':100})
            state = await call(slate, 'Snapshot', {'ref':'w1','maxDepth':100})
            field = re.search(r'text "Cmd".*\n.*\n\s*textbox .*\[ref=(tb\d+)\]', state)
            assert field
            command = 'py C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/prepare_stage2_director.py'
            await call(slate, 'Type', {'ref': field[1], 'text':command, 'submit':True})

            source = SOURCE + '.BP_Stage1Director'
            target = TARGET + '.BP_Stage2WorkshopDirector'
            original = await call(bp, 'read_graph_dsl', {'graph':ref(source + ':EventGraph')})
            updated = make_graph(original)
            Path('tmp/stage2_workshop_controls.dsl').write_text(updated, encoding='utf-8')
            variables = await call(bp, 'list_variables', {'blueprint':ref(target)})
            if 'WheelPushTarget' not in json.dumps(variables):
                await call(bp, 'add_variable', {'blueprint':ref(target), 'name':'WheelPushTarget', 'type_name':'float'})
            graph = ref(target + ':EventGraph')
            print('WRITE', await call(bp, 'write_graph_dsl', {'graph':graph, 'code':updated}), flush=True)
            print('COMPILE', await call(bp, 'compile_blueprint', {'blueprint':ref(target)}), flush=True)
            verified = await call(bp, 'read_graph_dsl', {'graph':graph})
            assert 'SetWheelPushTarget' in verified and 'PrintString' not in verified and '"Q"' not in verified
            print('SAVE', await call(asset, 'save_assets', {'asset_paths':[TARGET]}), flush=True)


if __name__ == '__main__':
    asyncio.run(run())
