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
   p='/Game/Level/UEDPIE_0_Stage2_ResolutionCorridor_Prototype.Stage2_ResolutionCorridor_Prototype:PersistentLevel.'
   ref=lambda x:{'refPath':p+x};pawn=ref('DirectorCutDragon_0');move=ref('DirectorCutDragon_0.CharMoveComp');ctrl=ref('BP_ResolutionCorridor_C_0')
   ac='editor_toolset.toolsets.actor.ActorTools';ob='editor_toolset.toolsets.object.ObjectTools'
   await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':465,'y':0,'z':60}}});await asyncio.sleep(.5)
   print('PRE',await c(ac,'get_actor_transform',{'actor':pawn}),flush=True)
   await c(ob,'set_properties',{'instance':move,'values':json.dumps({'movementMode':'MOVE_Falling','velocity':{'x':340,'y':0,'z':445}})})
   await asyncio.sleep(1.1)
   print('POST',await c(ac,'get_actor_transform',{'actor':pawn}),await c(ob,'get_properties',{'instance':ctrl,'properties':['progress','bFailing','bCompleted']}),flush=True)
asyncio.run(main())
