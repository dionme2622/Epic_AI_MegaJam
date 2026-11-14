import asyncio,json,base64
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError:raise RuntimeError(str(z.content))
    return json.loads(z.content[0].text).get('returnValue')
   app='EditorToolset.EditorAppToolset';ac='editor_toolset.toolsets.actor.ActorTools'
   if not await c(app,'IsPIERunning',{}):await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   p='/Game/Level/UEDPIE_0_Stage2_ResolutionCorridor_Prototype.Stage2_ResolutionCorridor_Prototype:PersistentLevel.'
   await c(ac,'set_actor_transform',{'actor':{'refPath':p+'DirectorCutDragon_0'},'xform':{'location':{'x':400,'y':0,'z':85}}});await asyncio.sleep(.8)
   z=await c(app,'CaptureEditorImage',{});Path('output/ResolutionCorridor/tile_close.png').write_bytes(base64.b64decode(z['data']))
   print('CAPTURED')
asyncio.run(main())
