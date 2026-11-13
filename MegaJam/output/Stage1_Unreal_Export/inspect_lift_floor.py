import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (rd,wr,_):
  async with ClientSession(rd,wr) as s:
   await s.initialize()
   async def call(ts,n,a):
    r=await s.call_tool('call_tool',{'toolset_name':ts,'tool_name':n,'arguments':a})
    print(n,r.content[0].text[:5500],flush=True)
   p='/Game/Level/UEDPIE_0_Stage1.Stage1:PersistentLevel.'
   await call('editor_toolset.toolsets.actor.ActorTools','set_actor_transform',{'actor':{'refPath':p+'BP_Stage1Dragon_C_0'},'xform':{'location':{'x':8700,'y':0,'z':180}}})
   await asyncio.sleep(1)
   for path,props in [(p+'BP_Stage1Dragon_C_0.CharMoveComp',['currentFloor']),(p+'BP_Stage1Dragon_C_0.CollisionCylinder',['capsuleHalfHeight','capsuleRadius']),(p+'StaticMeshActor_7.StaticMeshComponent0',['bodyInstance']),(p+'StaticMeshActor_9.StaticMeshComponent0',['bodyInstance'])]:
    await call('editor_toolset.toolsets.object.ObjectTools','get_properties',{'instance':{'refPath':path},'properties':props})
asyncio.run(main())
