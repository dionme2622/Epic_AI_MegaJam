import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def call(t,n,a):
    return await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
   app='EditorToolset.EditorAppToolset';ob='editor_toolset.toolsets.object.ObjectTools'
   r=await call(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':2}})
   if r.isError:raise RuntimeError(str(r.content))
   print('PLAY_STARTED',flush=True)
   await asyncio.sleep(3)
   pro={'refPath':'/Game/DirectorCut/Prologue/UEDPIE_0_L_BossPrologue.L_BossPrologue:PersistentLevel.BP_PrologueStageTransition_C_0'}
   x=await call(ob,'get_properties',{'instance':pro,'properties':['PrologueSequence']});print('PROLOGUE_RUNNING',x.content,flush=True)
   if x.isError: raise RuntimeError('Prologue did not start as expected')
   stage={'refPath':'/Game/Level/UEDPIE_0_Stage1.Stage1:PersistentLevel.BP_Stage1Director_C_0'}
   for i in range(20):
    await asyncio.sleep(3)
    x=await call(ob,'get_properties',{'instance':stage,'properties':['IsLow','WheelSolved']})
    if not x.isError:
     print('STAGE1_LOADED',x.content,flush=True)
     await call(app,'StopPIE',{});return
   raise RuntimeError('Stage1 did not load within 60 seconds')
asyncio.run(main())
