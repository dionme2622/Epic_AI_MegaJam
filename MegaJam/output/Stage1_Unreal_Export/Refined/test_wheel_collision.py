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
   app='EditorToolset.EditorAppToolset';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools';sl='SlateInspectorToolset.SlateInspectorToolset'
   await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   await c(sl,'Snapshot',{'ref':'','maxDepth':3});await c(sl,'Observe',{'ref':'w1','maxDepth':30});await c(sl,'Snapshot',{'ref':'w1','maxDepth':30});await c(sl,'Click',{'ref':'sp5'})
   p='/Game/Level/UEDPIE_0_Stage1.Stage1:PersistentLevel.';ref=lambda x:{'refPath':p+x};pawn=ref('BP_Stage1Dragon_C_0');ctrl=ref('BP_Stage1Director_C_0')
   for i in [3,4]:
    v=json.loads(await c(ob,'get_properties',{'instance':ref(f'StaticMeshActor_{i}.StaticMeshComponent0'),'properties':['bodyInstance']}))['bodyInstance']
    print('PIE_COLLISION',i,v['collisionEnabled'],flush=True);assert v['collisionEnabled']=='NoCollision'
   await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':180,'y':0,'z':150}}});await asyncio.sleep(1)
   before=await c(ac,'get_actor_transform',{'actor':pawn})
   for _ in range(35):await c(sl,'PressKey',{'key':'D'})
   after=await c(ac,'get_actor_transform',{'actor':pawn})
   print('PLAYER_POSITIONS',before['location'],after['location'],flush=True)
   st=json.loads(await c(ob,'get_properties',{'instance':ctrl,'properties':['IsLow','WheelX','WheelSolved']}));print('WHEEL_STATE',st,flush=True)
   await c(app,'StopPIE',{})
asyncio.run(main())
