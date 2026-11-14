import asyncio, base64, json
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
    async with streamable_http_client("http://127.0.0.1:18765/mcp") as (r,w,_):
        async with ClientSession(r,w) as session:
            await session.initialize()
            async def c(toolset,name,args=None):
                p=await session.call_tool("call_tool",{"toolset_name":toolset,"tool_name":name,"arguments":args or {}})
                if p.isError: raise RuntimeError(p.content)
                return json.loads(p.content[0].text)["returnValue"]
            scene="editor_toolset.toolsets.scene.SceneTools"
            obj="editor_toolset.toolsets.object.ObjectTools"
            actor="editor_toolset.toolsets.actor.ActorTools"
            async def find(label):
                return await c(scene,"find_actors",{"name":label,"tag":"","collision_channels":[]})
            theatre,=await find("Shadow Rehearsal")
            assert theatre["refPath"].startswith("/Game/DirectorCut/Stage/Stage4.Stage4:")
            assert not await find("Stage4_ShadowStage")
            q=await c(obj,"get_properties",{"instance":theatre,"properties":["EntranceDoor","SilhouetteMaterial","WestRig","EastRig","Glass","Exhibit"]})
            p=json.loads(q)
            assert all(p.get(k) for k in ["EntranceDoor","SilhouetteMaterial","WestRig","EastRig","Glass","Exhibit"]), p
            color,=await find("Color_Controller")
            comp=await c(obj,"get_properties",{"instance":color,"properties":["bUseRgbCalibration"]})
            assert json.loads(comp)["bUseRgbCalibration"]
            print("Fresh Stage4 verified",p,flush=True)
asyncio.run(main())

