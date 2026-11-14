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
   app='EditorToolset.EditorAppToolset';sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools'
   # PIE already running
   for name in ['Dragon','Stage1_To_Stage2_FadeExit','Ground']:
    print(name,await c(sc,'find_actors',{'name':name,'tag':'','collision_channels':[]}),flush=True)
   players=await c(sc,'find_actors',{'name':'Player','tag':'','collision_channels':[]});pawn=next(a for a in players if 'BP_Stage1Dragon' in a['refPath'])
   exit=(await c(sc,'find_actors',{'name':'Stage1_To_Stage2_FadeExit','tag':'','collision_channels':[]}))[0]
   await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':9800,'y':0,'z':300}}});await asyncio.sleep(1)
   print('BEFORE',await c(ac,'get_actor_transform',{'actor':pawn}),await c(ob,'get_properties',{'instance':exit,'properties':['ExitX','TransitionStarted']}),flush=True)
   img=await c(app,'CaptureEditorImage',{});Path('output/Stage2Integrated/stage1_end.png').write_bytes(base64.b64decode(img['data']))
   await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':9950,'y':0,'z':300}}});await asyncio.sleep(.4)
   print('TRIGGERED',await c(ob,'get_properties',{'instance':exit,'properties':['TransitionStarted']}),flush=True)
   await asyncio.sleep(2)
   a=await c(sc,'find_actors',{'name':'Stage2_EntryFade','tag':'','collision_channels':[]});print('DESTINATION',a,flush=True)
   if not a:raise RuntimeError('Transition destination missing')
   await asyncio.sleep(2);img=await c(app,'CaptureEditorImage',{});Path('output/Stage2Integrated/transition_done.png').write_bytes(base64.b64decode(img['data']))
asyncio.run(main())

