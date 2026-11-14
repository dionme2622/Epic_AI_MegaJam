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
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:180],flush=True);return v
   scene='editor_toolset.toolsets.scene.SceneTools';obj='editor_toolset.toolsets.object.ObjectTools';act='editor_toolset.toolsets.actor.ActorTools';p='/Game/Level/Stage2_BloomSign_Prototype.Stage2_BloomSign_Prototype:PersistentLevel.'
   async def move(name,x,y,z,yaw=0):
    await c(act,'set_actor_transform',{'actor':{'refPath':p+name},'xform':{'location':{'x':x,'y':y,'z':z},'rotation':{'pitch':0,'yaw':yaw,'roll':0},'scale':{'x':1,'y':1,'z':1}}})
   for i,x in enumerate([350,900,1450]):
    await move('BP_BloomSign_C_'+str(i),x,-160,140)
    await move('TextRenderActor_'+str(i),x,-175,235,90)
   await move('TextRenderActor_4',-170,-220,225,90)
   await move('TextRenderActor_5',1900,-175,220,90)
   await c(obj,'set_properties',{'instance':{'refPath':p+'BP_BloomController_C_0'},'values':json.dumps({'bloomIntensity':18.0})})
   for ix,x in enumerate([0,1100]):
    for group,mat in [('Wood','M_Backstage_Wood'),('Brass','M_Brass_Trim'),('Curtain','M_Theatre_Curtain')]:
     mesh=f'/Game/FocusPropPrototype/Detail/SM_FocusDetail_{group}.SM_FocusDetail_{group}'
     actor=await c(scene,'add_to_scene_from_asset',{'asset_path':mesh,'name':f'Bloom_Set_{group}_{ix}','xform':{'location':{'x':x,'y':110,'z':0}}})
     component={'refPath':actor['refPath']+'.StaticMeshComponent0'}
     await c(obj,'set_properties',{'instance':component,'values':json.dumps({'overrideMaterials':[{'refPath':f'/Game/Stage1Generated/Meshes/{mat}.{mat}'}],'bodyInstance':{'collisionEnabled':'NoCollision','collisionProfileName':'NoCollision'}})})
   await c('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':['/Game/Level/Stage2_BloomSign_Prototype']})
asyncio.run(main())
