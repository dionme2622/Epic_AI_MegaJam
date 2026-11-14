import asyncio,json
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
   sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools';app='EditorToolset.EditorAppToolset'
   if await c(app,'IsPIERunning',{}):await c(app,'StopPIE',{})
   await c(sc,'load_level',{'level_path':'/Game/Level/Stage2_ShadowBody_Prototype'});await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   pawn=next(x for x in await c(sc,'find_actors',{'name':'Dragon','tag':'','collision_channels':[]}) if 'DirectorCutDragon' in x['refPath']);move={'refPath':pawn['refPath']+'.CharMoveComp'}
   await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':450,'y':0,'z':54}}});await asyncio.sleep(.6)
   await c(ob,'set_properties',{'instance':move,'values':json.dumps({'movementMode':'MOVE_Falling','velocity':{'x':340,'y':0,'z':445}})});await asyncio.sleep(.85)
   print('JUMP_RESULT',await c(ac,'get_actor_transform',{'actor':pawn}),flush=True)
   await c(app,'StopPIE',{})
asyncio.run(main())
