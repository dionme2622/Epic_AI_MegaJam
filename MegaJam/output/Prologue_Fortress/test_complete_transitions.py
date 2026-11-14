import asyncio,json,base64,time
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def call(t,n,a,strict=True):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError:
     if strict:raise RuntimeError(f'{n}: {z.content}')
     return None
    return json.loads(z.content[0].text).get('returnValue')
   sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools';app='EditorToolset.EditorAppToolset'
   async def image(n):
    z=await call(app,'CaptureEditorImage',{});Path('output/Prologue_Fortress/'+n+'.png').write_bytes(base64.b64decode(z['data']))
   await call(sc,'load_level',{'level_path':'/Game/DirectorCut/Prologue/L_BossPrologue'})
   await call(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   print('PROLOGUE_PLAY',flush=True)
   await asyncio.sleep(23)
   await image('transition_prologue_pre')
   await asyncio.sleep(.8);await image('transition_prologue_dark')
   for _ in range(30):
    stage=await call(sc,'find_actors',{'name':'Stage1_RightExit_Fade','tag':'','collision_channels':[]})
    if stage:break
    await asyncio.sleep(.2)
   if not stage:raise RuntimeError('Prologue did not reach L_Stage1')
   print('L_STAGE1',stage,flush=True);await image('transition_stage_entry_early')
   await asyncio.sleep(2);await image('transition_stage_entry_done')
   dragons=await call(sc,'find_actors',{'name':'Dragon','tag':'','collision_channels':[]})
   if len(dragons)!=1:raise RuntimeError(f'Expected one player dragon: {dragons}')
   pawn=dragons[0];exitactor=stage[0]
   await call(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':1620,'y':0,'z':90}}});await asyncio.sleep(.6)
   state=json.loads(await call(ob,'get_properties',{'instance':exitactor,'properties':['ExitX','TransitionStarted']}))
   print('BEFORE_EXIT',state,flush=True);assert not state['TransitionStarted'] and state['ExitX']==1650
   await call(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':1642,'y':0,'z':55}}})
   comp={'refPath':pawn['refPath']+'.CharMoveComp'}
   await call(ob,'set_properties',{'instance':comp,'values':json.dumps({'velocity':{'x':340,'y':0,'z':0}})})
   await asyncio.sleep(.55);await image('transition_exit_fade')
   state=json.loads(await call(ob,'get_properties',{'instance':exitactor,'properties':['TransitionStarted']}));print('EXIT_TRIGGERED',state,flush=True);assert state['TransitionStarted']
   for _ in range(30):
    fade=await call(sc,'find_actors',{'name':'Stage1_EntryFade','tag':'','collision_channels':[]})
    if fade:break
    await asyncio.sleep(.2)
   if not fade:raise RuntimeError('Exit did not reach /Game/Level/Stage1')
   print('STAGE1_LOADED',fade,flush=True);await image('transition_stage1_entry_early')
   await asyncio.sleep(2);await image('transition_stage1_entry_done')
   await call(app,'StopPIE',{});print('COMPLETE',flush=True)
asyncio.run(main())
