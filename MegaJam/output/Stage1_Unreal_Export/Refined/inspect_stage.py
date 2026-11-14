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
   sc='editor_toolset.toolsets.scene.SceneTools';obj='editor_toolset.toolsets.object.ObjectTools'
   for tag in ['WheelPiece','GearHigh','GearLow']:
    actors=await c(sc,'find_actors',{'name':'','tag':tag,'collision_channels':[]})
    for a in actors:
     print(tag,a,json.loads(await c(obj,'get_properties',{'instance':a,'properties':['tags']})))
     print(json.loads(await c(obj,'get_properties',{'instance':{'refPath':a['refPath']+'.StaticMeshComponent0'},'properties':['staticMesh','overrideMaterials','mobility','bodyInstance']})),flush=True)
asyncio.run(main())
