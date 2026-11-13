import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def call(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    print(n,a.get('instance',a.get('actor','')),z.content[0].text[:4500])
   pref='/Game/Level/UEDPIE_0_Stage1.Stage1:PersistentLevel.'
   for name in ['BP_Stage1Dragon_C_0','StaticMeshActor_7','StaticMeshActor_9','CameraActor_0']:
    await call('editor_toolset.toolsets.actor.ActorTools','get_actor_transform',{'actor':{'refPath':pref+name}})
   for path,props in [(pref+'BP_Stage1Dragon_C_0.CharacterMesh0',['relativeScale3D','relativeLocation','skeletalMeshAsset']), (pref+'StaticMeshActor_7.StaticMeshComponent0',['bodyInstance','mobility']), (pref+'StaticMeshActor_9.StaticMeshComponent0',['bodyInstance','mobility'])]:
    await call('editor_toolset.toolsets.object.ObjectTools','get_properties',{'instance':{'refPath':path},'properties':props})
asyncio.run(main())
