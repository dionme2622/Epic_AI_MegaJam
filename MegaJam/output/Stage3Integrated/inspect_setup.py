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
   sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools'
   for path in ['/Game/Level/Stage3_puzzle1','/Game/Level/Stage3_puzzle','/Game/Level/Stage3_puzzle3']:
    await c(sc,'load_level',{'level_path':path});world=(await c(sc,'find_actors',{'name':'WorldSettings','tag':'','collision_channels':[]}))[0];print('MODE',path,await c(ob,'get_properties',{'instance':world,'properties':['defaultGameMode']}),flush=True)
    for a in await c(sc,'find_actors',{'name':'','tag':'','collision_channels':[]}):
     n=a['refPath'].split('.')[-1]
     if n in ['StaticMeshActor_0','Floor_0']:
      p={'refPath':a['refPath']+'.StaticMeshComponent0'};print(n,await c(ob,'get_properties',{'instance':p,'properties':['staticMesh']}),await c(ac,'get_actor_transform',{'actor':a}),flush=True)
asyncio.run(main())
