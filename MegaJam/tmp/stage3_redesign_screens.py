import asyncio, json, base64
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
 async with streamable_http_client('http://127.0.0.1:18765/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def call(ts,n,args={}):
    v=await s.call_tool('call_tool',{'toolset_name':ts,'tool_name':n,'arguments':args})
    if v.isError: raise RuntimeError(v.content)
    return json.loads(v.content[0].text)['returnValue']
   sc='editor_toolset.toolsets.scene.SceneTools';ac='editor_toolset.toolsets.actor.ActorTools';app='EditorToolset.EditorAppToolset';sl='SlateInspectorToolset.SlateInspectorToolset'
   assert not await call(app,'IsPIERunning')
   await call(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':2}})
   try:
    pawn=(await call(sc,'find_actors',{'name':'DirectorCutDragon','tag':'','collision_channels':[]}))[0]
    for i,x in enumerate((200,900,2250,2800,3350,3900,5360,5800,6800)):
     await call(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':x,'y':0,'z':58}}})
     await asyncio.sleep(1.1)
     d=await call(app,'CaptureEditorImage');Path(f'tmp/stage3_redesign_{i}.png').write_bytes(base64.b64decode(d['data']))
     print(i,x,flush=True)
   finally: await call(app,'StopPIE')
asyncio.run(main())
