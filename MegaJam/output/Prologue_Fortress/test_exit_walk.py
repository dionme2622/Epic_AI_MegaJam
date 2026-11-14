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
   app='EditorToolset.EditorAppToolset';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools';sc='editor_toolset.toolsets.scene.SceneTools'
   await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':.5}})
   p='/Game/DirectorCut/Stage1/UEDPIE_0_L_Stage1.L_Stage1:PersistentLevel.'
   pawn={'refPath':p+'BP_DirectorCutDragon_C_0'};trigger={'refPath':p+'BP_StageRightExit_C_0'}
   await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':1450,'y':0,'z':55}}})
   async def image(n):
    z=await c(app,'CaptureEditorImage',{});Path('output/Prologue_Fortress/'+n+'.png').write_bytes(base64.b64decode(z['data']))
   for _ in range(24):
    v=json.loads(await c(ob,'get_properties',{'instance':trigger,'properties':['TransitionStarted','ExitX']}))
    loc=await c(ac,'get_actor_transform',{'actor':pawn})
    print('WALK',loc['location']['x'],v,flush=True)
    if v['TransitionStarted']:break
    await asyncio.sleep(.15)
   else:raise RuntimeError('Walking could not reach the exit threshold')
   await image('transition_exit_fade')
   for _ in range(30):
    found=await c(sc,'find_actors',{'name':'Stage1_EntryFade','tag':'','collision_channels':[]})
    if found:break
    await asyncio.sleep(.1)
   if not found:raise RuntimeError('Exit did not reach /Game/Level/Stage1')
   print('DESTINATION',found,flush=True);await image('transition_stage1_entry_early')
   await asyncio.sleep(2);await image('transition_stage1_entry_done')
   await c(app,'StopPIE',{});print('COMPLETE',flush=True)
asyncio.run(main())
