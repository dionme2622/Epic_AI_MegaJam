import argparse
import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


ROUTES = (
    ('/Game/DirectorCut/Transitions/BP_StageRightExit', '/Game/DirectorCut/Stage/Stage2.Stage2'),
    ('/Game/Stage3Integrated/BP_Stage2ToStage3', '/Game/DirectorCut/Stage/Stage3_.Stage3_'),
)


async def run(apply):
    async with streamable_http_client('http://127.0.0.1:18765/mcp') as (read, write, _):
        async with ClientSession(read, write) as client:
            await client.initialize()

            async def call(toolset, name, arguments):
                response = await client.call_tool('call_tool', {
                    'toolset_name': toolset, 'tool_name': name, 'arguments': arguments,
                })
                if response.isError:
                    raise RuntimeError((name, response.content))
                return json.loads(response.content[0].text)['returnValue']

            blueprint = 'editor_toolset.toolsets.blueprint.BlueprintTools'
            assets = 'editor_toolset.toolsets.asset.AssetTools'
            app = 'EditorToolset.EditorAppToolset'
            assert not await call(app, 'IsPIERunning', {})

            for package, target in ROUTES:
                ref_path = package + '.' + package.rsplit('/', 1)[1]
                asset = {'refPath': ref_path}
                graph = {'refPath': ref_path + ':EventGraph'}
                candidates = await call(blueprint, 'find_nodes', {'graph': graph, 'title': 'Open Level'})
                assert len(candidates) == 1, (ref_path, candidates)
                node = candidates[0]
                nodes = await call(blueprint, 'get_node_infos', {'nodes': candidates})
                print(package, json.dumps(nodes, ensure_ascii=False), flush=True)
                if not apply:
                    continue

                pin = {'node': node, 'direction': 'EGPD_Input', 'index_id': 1}
                await call(blueprint, 'set_pin_value', {'pin': pin, 'value': target})
                updated = await call(blueprint, 'get_node_infos', {'nodes': candidates})
                assert target in json.dumps(updated), updated
                await call(blueprint, 'compile_blueprint', {'blueprint': asset})
                await call(assets, 'save_assets', {'asset_paths': [package]})
                print('Saved transition:', package, '->', target, flush=True)


parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true')
asyncio.run(run(parser.parse_args().apply))
