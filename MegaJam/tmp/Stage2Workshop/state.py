import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client("http://127.0.0.1:18765/mcp") as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a={}):
    z=await s.call_tool("call_tool",{"toolset_name":t,"tool_name":n,"arguments":a})
    if z.isError: raise RuntimeError(z.content)
    return json.loads(z.content[0].text)["returnValue"]
   app="EditorToolset.EditorAppToolset"
   sc="editor_toolset.toolsets.scene.SceneTools"
   sl="SlateInspectorToolset.SlateInspectorToolset"
   print("PIE",await c(app,"IsPIERunning"))
   print("worldsettings",await c(sc,"find_actors",{"name":"WorldSettings","tag":"","collision_channels":[]}))
   await c(sl,"Observe",{"ref":"w1","maxDepth":80})
   snap=await c(sl,"Snapshot",{"ref":"w1","maxDepth":80})
   print("\n".join(x for x in snap.splitlines() if "Unsaved" in x or "Saved" in x or 'text "Cmd"' in x))
asyncio.run(main())
