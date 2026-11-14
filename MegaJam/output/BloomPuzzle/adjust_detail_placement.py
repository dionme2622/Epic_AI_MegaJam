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
   sc='editor_toolset.toolsets.scene.SceneTools';ac='editor_toolset.toolsets.actor.ActorTools'
   for label in ['Bloom_Sign','Bloom_Number']:
    actors=await c(sc,'find_actors',{'name':label,'tag':'','collision_channels':[]})
    if len(actors)!=3:raise RuntimeError('Expected three '+label+' actors')
    for a in actors:
     t=await c(ac,'get_actor_transform',{'actor':a})
     t['location']['z']=160 if label=='Bloom_Sign' else 205
     t['location']['y']=-150 if label=='Bloom_Sign' else -140
     if label=='Bloom_Number':t['location']['x']+=100
     await c(ac,'set_actor_transform',{'actor':a,'xform':t});print(label,t['location'],flush=True)
   # Put the long set-dressing rails behind the luminous signs instead of
   # drawing them across the clues in the player camera.
   for group,depth in [('Bloom_Set_Brass',70),('Bloom_Set_Wood',80),('Bloom_Set_Curtain',110)]:
    actors=await c(sc,'find_actors',{'name':group,'tag':'','collision_channels':[]})
    for a in actors:
     t=await c(ac,'get_actor_transform',{'actor':a});t['location']['y']=depth
     await c(ac,'set_actor_transform',{'actor':a,'xform':t})
   signs=await c(sc,'find_actors',{'name':'Bloom_Sign','tag':'','collision_channels':[]})
   ob='editor_toolset.toolsets.object.ObjectTools'
   for a in signs:
    for component in ['Frame','Face','Symbol']:
     await c(ob,'set_properties',{'instance':{'refPath':a['refPath']+'.'+component},'values':json.dumps({'castShadow':False})})
   await c('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':['/Game/Level/Stage2_BloomSign_Prototype']})
asyncio.run(main())
