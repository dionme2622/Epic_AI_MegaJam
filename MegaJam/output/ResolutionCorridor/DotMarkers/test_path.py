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
   app='EditorToolset.EditorAppToolset';ac='editor_toolset.toolsets.actor.ActorTools';ob='editor_toolset.toolsets.object.ObjectTools'
   await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   p='/Game/Level/UEDPIE_0_Stage2_ResolutionCorridor_Prototype.Stage2_ResolutionCorridor_Prototype:PersistentLevel.'
   ref=lambda n:{'refPath':p+n};pawn=ref('DirectorCutDragon_0');ctl=ref('BP_ResolutionCorridor_C_0');door=ref('BP_S2_Door_C_0')
   for x in [400,720,1040]:
    await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':x,'y':0,'z':85}}});await asyncio.sleep(.7)
    print('PAD',x,await c(ob,'get_properties',{'instance':ctl,'properties':['progress','bCompleted']}),flush=True)
   state=json.loads(await c(ob,'get_properties',{'instance':ctl,'properties':['bCompleted']}))
   opened=json.loads(await c(ob,'get_properties',{'instance':door,'properties':['bOpen']}))
   assert state['bCompleted'] and opened['bOpen']
   print('CLEAR',state,opened,flush=True);await c(app,'StopPIE',{})
asyncio.run(main())
