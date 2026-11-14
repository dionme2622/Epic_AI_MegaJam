import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    if t=='editor_toolset.toolsets.scene.SceneTools' and n in ['add_to_scene_from_asset','remove_from_scene']:
     chk=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':'find_actors','arguments':{'name':'WorldSettings','tag':'','collision_channels':[]}}); worlds=json.loads(chk.content[0].text).get('returnValue'); assert len(worlds)==1 and '/Game/Level/Stage2_ShadowBody_Prototype.' in worlds[0]['refPath'],f'Unexpected level: {worlds}'
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError:raise RuntimeError(f'{n} {z.content}')
    v=json.loads(z.content[0].text).get('returnValue');return v
   ref=lambda p:{'refPath':p};sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools';sm='editor_toolset.toolsets.static_mesh.StaticMeshTools';assets='editor_toolset.toolsets.asset.AssetTools';bp='editor_toolset.toolsets.blueprint.BlueprintTools'
   level='/Game/Level/Stage2_ShadowBody_Prototype';folder='/Game/ShadowBodyStage'
   async def props(o,v):
    ok=await c(ob,'set_properties',{'instance':o,'values':json.dumps(v)});
    if not ok:print('SET FAILED',o,v,flush=True)
   await c(sc,'load_level',{'level_path':level})
   all=await c(sc,'find_actors',{'name':'','tag':'','collision_channels':[]})
   for a in all:
    n=a['refPath'].split('.')[-1]
    if n.startswith(('StaticMeshActor_','Floor_','BP_S2_Door','BP_Focus','TextRenderActor','CameraActor_','SkyAtmosphere_','ExponentialHeightFog_','VolumetricCloud_')):
     print('REMOVE',n,await c(sc,'remove_from_scene',{'actor':a}),flush=True)
   async def add(name,path,x,y,z,sx,sy,sz,mat=None,collision=True,shadow=True):
    a=await c(sc,'add_to_scene_from_asset',{'asset_path':path,'name':name,'xform':{'location':{'x':x,'y':y,'z':z},'scale':{'x':sx,'y':sy,'z':sz}}})
    comp=ref(a['refPath']+'.StaticMeshComponent0');v={'castShadow':shadow}
    if mat:v['overrideMaterials']=[ref('/Game/Stage1Generated/Meshes/'+mat+'.'+mat)]
    if not collision:v['bodyInstance']={'collisionEnabled':'NoCollision','collisionProfileName':'NoCollision'}
    await props(comp,v);return a
   cube='/Engine/BasicShapes/Cube.Cube'
   await add('Shadow_Start',cube,-20,0,-35,6.0,4,0.7,'M_Floor_Stone')
   await add('Shadow_End',cube,2310,0,-35,7,4,.7,'M_Floor_Stone')
   for i,x in enumerate([410,680,950,1220,1490,1760]):
    await add(f'Shadow_SafePlatform_{i+1}',cube,x,0,-20,1.65,3.3,.4,'M_Floor_Stone')
    await add(f'Shadow_PlatformTrim_{i+1}',cube,x,-157,3,1.65,.12,.08,'M_Brass_Trim',False,False)
   await add('Shadow_PitBackdrop',cube,1100,0,-230,24,10,.1,'M_Stone_Dark',False,False)
   await add('Shadow_BackWall',cube,1100,-260,280,30,.25,7,'M_Stone_Plum',False,False)
   for i,x in enumerate([400,670,940,1210,1480,1750]):
    await add(f'Overhead_Rig_{i}',cube,x,0,365,2.5,5.2,.65,'M_Stone_Dark',False,True)
    await add(f'Overhead_Trim_{i}',cube,x,-240,396,2.6,.18,.13,'M_Brass_Trim',False,False)
    for j in [-1,1]:await add(f'Hanging_Chain_{i}_{j}',cube,x+j*95,-220,530,.06,.08,2.7,'M_Stone_Dark',False,False)
   for i,x in enumerate([-260,250,1930,2600]):
    await add(f'Stage_Pillar_{i}',cube,x,-240,250,.28,.4,5,'M_Backstage_Wood',False,False)
    await add(f'Pillar_Cap_{i}',cube,x,-240,490,.5,.5,.22,'M_Brass_Trim',False,False)
   await add('Storage_Pedestal',cube,2330,-30,30,3.0,1.6,.6,'M_Stone_Dark',True,False)
   await add('Storage_Pedestal_Trim',cube,2330,-30,62,3.1,1.7,.08,'M_Brass_Trim',False,False)
   dragon=await add('Dragon_LowerBody','/Game/ShadowBodyStage/SM_DragonLowerBody.SM_DragonLowerBody',2340,-25,70,1,1,1,None,False,False)
   print('BODY',dragon,flush=True)
   light=(await c(sc,'find_actors',{'name':'DirectionalLight','tag':'','collision_channels':[]}))[0]
   print('LIGHT_COMPONENTS',await c(ac,'get_components',{'actor':light}),flush=True)
   await c(assets,'save_assets',{'asset_paths':[level,folder+'/SM_DragonLowerBody']})
   print('BUILT',flush=True)
asyncio.run(main())


