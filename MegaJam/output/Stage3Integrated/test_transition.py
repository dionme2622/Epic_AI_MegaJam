import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError:raise RuntimeError(f'{n}: {z.content}')
    return json.loads(z.content[0].text).get('returnValue')
   app='EditorToolset.EditorAppToolset';sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools'
   await c(sc,'load_level',{'level_path':'/Game/DirectorCut/Stage/Stage2'});await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   a=await c(sc,'find_actors',{'name':'Player','tag':'','collision_channels':[]});pawn=next(a for a in a if 'BP_Stage1Dragon' in a['refPath'])
   ex=(await c(sc,'find_actors',{'name':'Stage2_To_Stage3_FadeExit','tag':'','collision_channels':[]}))[0]
   await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':9800,'y':0,'z':350}}});await asyncio.sleep(.6);print('PRE',await c(ob,'get_properties',{'instance':ex,'properties':['TransitionStarted','ExitX']}),flush=True)
   await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':9950,'y':0,'z':350}}});await asyncio.sleep(.5);print('TRIGGER',await c(ob,'get_properties',{'instance':ex,'properties':['TransitionStarted']}),flush=True)
   await asyncio.sleep(2);dest=await c(sc,'find_actors',{'name':'Stage3_EntryFade','tag':'','collision_channels':[]});print('DEST',dest,flush=True);assert dest and '/Game/Level/UEDPIE_0_Stage3_Integrated.' in dest[0]['refPath']
   await c(app,'StopPIE',{})
asyncio.run(main())
