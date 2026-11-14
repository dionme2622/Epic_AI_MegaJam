import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError: raise RuntimeError(str(z.content))
    return json.loads(z.content[0].text).get('returnValue')
   p='/Game/Level/UEDPIE_0_Stage2_ShadowStealth_Prototype.Stage2_ShadowStealth_Prototype:PersistentLevel.'
   pawn={'refPath':p+'BP_Dragon_C_0'}; spot={'refPath':p+'BP_S2_Spotlight_C_0'}
   await c('editor_toolset.toolsets.actor.ActorTools','set_actor_transform',{'actor':pawn,'xform':{'location':{'x':250,'y':0,'z':92},'rotation':{'pitch':0,'yaw':0,'roll':0},'scale':{'x':1,'y':1,'z':1}}})
   found=False
   for i in range(28):
    v=json.loads(await c('editor_toolset.toolsets.object.ObjectTools','get_properties',{'instance':spot,'properties':['bPlayerInBeam','bPlayerCovered','ExposureTime']}))
    if v['bPlayerInBeam'] and v['bPlayerCovered']:print('COVER_SUCCESS',v,flush=True);found=True;break
    await asyncio.sleep(.25)
   if not found: print('COVER_NOT_OBSERVED',v,flush=True)
asyncio.run(main())
