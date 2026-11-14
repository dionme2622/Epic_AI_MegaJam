import asyncio, json, re, base64
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def run():
 async with streamable_http_client("http://127.0.0.1:18765/mcp") as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,args=None):
    x=await s.call_tool("call_tool",{"toolset_name":t,"tool_name":n,"arguments":args or {}})
    if x.isError:raise RuntimeError((n,x.content))
    return json.loads(x.content[0].text)["returnValue"]
   sc="editor_toolset.toolsets.scene.SceneTools";ob="editor_toolset.toolsets.object.ObjectTools";ac="editor_toolset.toolsets.actor.ActorTools";sl="SlateInspectorToolset.SlateInspectorToolset";app="EditorToolset.EditorAppToolset"
   async def find(n):
    a=await c(sc,"find_actors",{"name":n,"tag":"","collision_channels":[]});assert len(a)==1,(n,a);return a[0]
   async def props(a,*keys):return json.loads(await c(ob,"get_properties",{"instance":a,"properties":keys}))
   async def key(k):
    await c(sl,"PressKey",{"key":k})
    await asyncio.sleep(.42)
   async def move(x,z=58):
    await c(ac,"set_actor_transform",{"actor":pawn,"xform":{"location":{"x":x,"y":0,"z":z}}})
    await asyncio.sleep(.8)
   async def screen(name):
    data=await c(app,"CaptureEditorImage")
    Path("tmp",name+".png").write_bytes(base64.b64decode(data["data"]))
   assert not await c(app,"IsPIERunning")
   await c(app,"StartPIE",{"options":{"bSimulate":False,"playMode":"PlayMode_InViewPort","warmupSeconds":2}})
   try:
    pawn=await find("DirectorCutDragon");bloom=await find("Bloom_Controller");res=await find("Resolution_Controller");crate=await find("Archive Empty Crate")
    await c(sl,"Observe",{"ref":"w1","maxDepth":100})
    await c(sl,"Snapshot",{"ref":"w1","maxDepth":4})
    await c(sl,"Click",{"ref":"sp6"})
    await move(2250)
    await screen("stage3-focus-bloom")
    await key("B")
    for x in (2250,2800,3350):
     await move(x);await key("E")
    print("FILM",await props(bloom,"bUseFilmEditing","bBloomOn","collectedFilms"),flush=True)
    assert (await props(bloom,"collectedFilms"))["collectedFilms"]==[1,2,3]
    await move(3900);await key("E")
    assert (await props(bloom,"bConsoleOpen"))["bConsoleOpen"]
    for k in ("One","Two","Three"):await key(k)
    await key("B");await asyncio.sleep(3.2)
    assert (await props(bloom,"bSolved"))["bSolved"]
    print("BLOOM OK",flush=True)
    await move(5360)
    await key("One");await key("E")
    print("CHOICE",await props(res,"selectedChoice","bChoiceConfirmed","progress"),flush=True)
    assert (await props(res,"bChoiceConfirmed"))["bChoiceConfirmed"]
    await move(5550,85)
    assert (await props(res,"progress"))["progress"]==1
    await key("One");await key("E")
    await asyncio.sleep(1.8)
    assert (await props(res,"progress"))["progress"]==1
    print("RETRY",await c(ac,"get_actor_transform",{"actor":pawn}),flush=True)
    await key("Two");await key("E");await move(5870,85)
    assert (await props(res,"progress"))["progress"]==2
    await key("Three");await key("E");await move(6190,85)
    assert (await props(res,"bCompleted"))["bCompleted"]
    await move(6790);await key("E")
    print("CRATE",await props(crate,"bOpened","Corridor"),flush=True)
    assert (await props(crate,"bOpened"))["bOpened"]
    await screen("stage3-crate")
    print("STAGE3 COMPLETE",flush=True)
   finally:
    if await c(app,"IsPIERunning"):await c(app,"StopPIE")
asyncio.run(run())

