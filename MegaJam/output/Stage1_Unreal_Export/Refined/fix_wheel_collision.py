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
   scene='editor_toolset.toolsets.scene.SceneTools';obj='editor_toolset.toolsets.object.ObjectTools'
   actors=await c(scene,'find_actors',{'name':'','tag':'WheelPiece','collision_channels':[]})
   if len(actors)!=2:raise RuntimeError('Expected exactly two wheel variants')
   for a in actors:
    tags=json.loads(await c(obj,'get_properties',{'instance':a,'properties':['tags']}))['tags']
    if not ('StageHigh' in tags or 'StageLow' in tags):raise RuntimeError(f'Unexpected wheel: {a}')
   for a in actors:
    comp={'refPath':a['refPath']+'.StaticMeshComponent0'}
    await c(obj,'set_properties',{'instance':comp,'values':json.dumps({'bodyInstance':{'collisionEnabled':'NoCollision','collisionProfileName':'NoCollision'}})})
    v=json.loads(await c(obj,'get_properties',{'instance':comp,'properties':['bodyInstance']}))['bodyInstance']
    print('WHEEL',a['refPath'],v['collisionEnabled'],v['collisionProfileName'],flush=True)
    assert v['collisionEnabled']=='NoCollision'
   await c('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':['/Game/Level/Stage1']})
asyncio.run(main())
