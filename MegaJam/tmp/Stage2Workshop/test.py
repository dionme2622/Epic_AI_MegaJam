import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
 async with streamable_http_client("http://127.0.0.1:18765/mcp") as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a={}):
    q=await s.call_tool("call_tool",{"toolset_name":t,"tool_name":n,"arguments":a})
    if q.isError:raise RuntimeError((n,q.content))
    return json.loads(q.content[0].text)["returnValue"]
   sc="editor_toolset.toolsets.scene.SceneTools";ac="editor_toolset.toolsets.actor.ActorTools"
   ob="editor_toolset.toolsets.object.ObjectTools";sl="SlateInspectorToolset.SlateInspectorToolset";app="EditorToolset.EditorAppToolset"
   async def find(n):
    a=await c(sc,"find_actors",{"name":n,"tag":"","collision_channels":[]})
    assert len(a)==1,(n,a)
    return a[0]
   async def props(a,*keys):return json.loads(await c(ob,"get_properties",{"instance":a,"properties":keys}))
   async def key(k):
    await c(sl,"PressKey",{"key":k});await asyncio.sleep(.38)
   async def setpos(a,x,z):
    assert await c(ac,"set_actor_transform",{"actor":a,"xform":{"location":{"x":x,"y":0,"z":z}}})
    await asyncio.sleep(.85)
   async def pos(a):return (await c(ac,"get_actor_transform",{"actor":a}))["location"]
   assert not await c(app,"IsPIERunning")
   await c(app,"StartPIE",{"options":{"bSimulate":False,"playMode":"PlayMode_InViewPort","warmupSeconds":1}})
   try:
    await c(sl,"Observe",{"ref":"w1","maxDepth":80});await c(sl,"Snapshot",{"ref":"w1","maxDepth":80});await c(sl,"Click",{"ref":"sp6"})
    player=await find("Stage1_Player");director=await find("Stage1_PuzzleDirector")
    hi=await find("Stage1_WheelHigh");lo=await find("Stage1_WheelLow");gate=await find("Stage1_GateBarrier")
    chair=await find("Workshop_DragonWheelchair")
    print("initial",await props(director,"IsLow","WheelX"),await props(hi,"bHidden"),await props(lo,"bHidden"),flush=True)
    assert (await props(director,"IsLow"))["IsLow"]
    assert (await props(hi,"bHidden"))["bHidden"] and not (await props(lo,"bHidden"))["bHidden"]
    await setpos(player,500,110)
    pp=await pos(player);ch=await pos(chair)
    assert abs(pp["x"]-ch["x"])<2 and abs(pp["z"]-ch["z"])<2,(pp,ch)
    await key("Q")
    before=await props(director,"IsLow","WheelX")
    await asyncio.sleep(1)
    after=await props(director,"IsLow","WheelX")
    print("HIGH_MOVEMENT",before,after,flush=True)
    assert not after["IsLow"] and after["WheelX"]>before["WheelX"]+10
    assert not (await props(hi,"bHidden"))["bHidden"] and (await props(lo,"bHidden"))["bHidden"]
    for i in range(90):
     wheel=await props(director,"WheelX")
     if 1140 < wheel["WheelX"] < 1250:
      break
     await asyncio.sleep(.08)
    else:
     raise RuntimeError(("Wheel did not reach target",wheel))
    await key("Q")
    assert (await props(director,"WheelSolved"))["WheelSolved"]
    print("WHEEL SOLVED",await props(director,"WheelSolved"),await props(gate,"bHidden"),flush=True)
    assert (await props(gate,"bHidden"))["bHidden"]
    gearhi=await find("Stage1_GearHigh");gearlo=await find("Stage1_GearLow");lift=await find("Stage1_LiftCollider")
    await setpos(player,8700,180)
    await key("E")
    assert not (await props(director,"LiftActive"))["LiftActive"]
    await key("Q")
    assert not (await props(gearhi,"bHidden"))["bHidden"] and (await props(gearlo,"bHidden"))["bHidden"]
    await key("E")
    await asyncio.sleep(5.3)
    st=await props(director,"LiftSolved","LiftAlpha")
    print("LIFT",st,"player",await pos(player),"chair",await pos(chair),"lift",await pos(lift),flush=True)
    assert st["LiftSolved"] and st["LiftAlpha"]>=229
    pp=await pos(player);ch=await pos(chair)
    assert abs(pp["x"]-ch["x"])<2 and abs(pp["z"]-ch["z"])<2
    print("PASS: visible variants, wheel movement/stop, gate, gear quality and lift with wheelchair",flush=True)
   finally:
    await c(app,"StopPIE")
asyncio.run(main())
