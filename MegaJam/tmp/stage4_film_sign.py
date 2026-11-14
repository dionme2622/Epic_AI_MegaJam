import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():
    async with streamable_http_client("http://127.0.0.1:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            async def call(toolset, name, args=None):
                reply = await session.call_tool("call_tool", {
                    "toolset_name": toolset, "tool_name": name, "arguments": args or {},
                })
                if reply.isError:
                    raise RuntimeError(reply.content)
                return json.loads(reply.content[0].text)["returnValue"]

            scene = "editor_toolset.toolsets.scene.SceneTools"
            obj = "editor_toolset.toolsets.object.ObjectTools"
            actor = "editor_toolset.toolsets.actor.ActorTools"
            app = "EditorToolset.EditorAppToolset"
            level = "/Game/DirectorCut/Stage/Stage4"
            assert not await call(app, "IsPIERunning")
            worlds = await call(scene, "find_actors", {"name": "WorldSettings", "tag": "", "collision_channels": []})
            assert any(a["refPath"].startswith(level + ".Stage4:") for a in worlds)
            sign = {"refPath": level + ".Stage4:PersistentLevel.TextRenderActor_0"}
            components = await call(actor, "get_components", {"actor": sign})
            text = next(a for a in components if "TextRender" in a["refPath"])
            before = json.loads(await call(obj, "get_properties", {"instance": text, "properties": ["text"]}))
            assert "COLOR SIGNAL" in str(before).upper(), before
            assert await call(obj, "set_properties", {
                "instance": text, "values": json.dumps({"text": "E : RESTORE FILM"}),
            })
            after = await call(obj, "get_properties", {"instance": text, "properties": ["text"]})
            assert "RESTORE FILM" in after, after
            assert await call("editor_toolset.toolsets.asset.AssetTools", "save_assets", {"asset_paths": [level]})
            print("Stage4 sign saved:", after)


asyncio.run(main())
