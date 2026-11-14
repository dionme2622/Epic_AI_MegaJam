import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError:raise RuntimeError(f'{n}: {z.content}')
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:250],flush=True);return v
   ref=lambda p:{'refPath':p};folder='/Game/ResolutionCorridor';dest='/Game/Level/Stage2_ResolutionCorridor_Prototype'
   ob='editor_toolset.toolsets.object.ObjectTools';bp='editor_toolset.toolsets.blueprint.BlueprintTools';sc='editor_toolset.toolsets.scene.SceneTools';sm='editor_toolset.toolsets.static_mesh.StaticMeshTools';mat='editor_toolset.toolsets.material.MaterialTools';assets='editor_toolset.toolsets.asset.AssetTools'
   async def props(o,v):return await c(ob,'set_properties',{'instance':o,'values':json.dumps(v)})
   for n in ['SM_ResolutionTile','SM_ResolutionArrow']:
    await c(sm,'import_file',{'folder_path':folder,'asset_name':n,'source_file':'C:/LHH/Epic_AI_MegaJam/MegaJam/output/ResolutionCorridor/'+n+'.fbx','import_materials':False,'import_textures':False,'combine_meshes':True})
   arrowmat=await c(mat,'create_material',{'folder_path':folder,'asset_name':'M_ResolutionArrow'})
   e=await c(mat,'add_expression',{'material_or_function':arrowmat,'expression_class':ref('/Script/Engine.MaterialExpressionConstant3Vector'),'x':-300,'y':0})
   await props(e,{'constant':{'r':.08,'g':1.1,'b':.75,'a':1}})
   await c(mat,'connect_to_output',{'expression':e,'output_name':'','material_property':'MP_EmissiveColor'})
   await props(arrowmat,{'shadingModel':'MSM_Unlit'});await c(mat,'recompile',{'material_or_function':arrowmat})
   tile=ref(folder+'/SM_ResolutionTile.SM_ResolutionTile');arrow=ref(folder+'/SM_ResolutionArrow.SM_ResolutionArrow')
   for slot,path in [('IronRim','/Game/Stage1Generated/RefinedMachinery/M_DarkIron.M_DarkIron'),('FloorStone','/Game/Stage1Generated/Meshes/M_Floor_Stone.M_Floor_Stone'),('BronzeStud','/Game/Stage1Generated/Meshes/M_Brass_Trim.M_Brass_Trim')]:
    await c(sm,'set_material',{'mesh':tile,'slot_name':slot,'material':ref(path)})
   await c(sm,'set_material',{'mesh':arrow,'slot_name':'ArrowLight','material':arrowmat})
   for name,parent in [('BP_ResolutionTile','ResolutionCorridorTile'),('BP_ResolutionCorridor','ResolutionCorridor')]:
    await c(bp,'create',{'folder_path':folder,'asset_name':name,'asset_type':ref('/Script/MegaJam.'+parent)})
   await props(ref(folder+'/BP_ResolutionTile.Default__BP_ResolutionTile_C:Mesh'),{'staticMesh':tile})
   for n in ['BP_ResolutionTile','BP_ResolutionCorridor']:await c(bp,'compile_blueprint',{'blueprint':ref(folder+'/'+n+'.'+n)})
   if not await c(assets,'duplicate',{'path':'/Game/Level/Stage2_FocusProp_Prototype','new_path':dest}):raise RuntimeError('Could not copy level')
   await c(assets,'save_assets',{'asset_paths':[dest,folder+'/BP_ResolutionTile',folder+'/BP_ResolutionCorridor',folder+'/SM_ResolutionTile',folder+'/SM_ResolutionArrow',folder+'/M_ResolutionArrow']})
   await c(sc,'load_level',{'level_path':dest})
   for a in await c(sc,'find_actors',{'name':'Focus','tag':'','collision_channels':[]}):await c(sc,'remove_from_scene',{'actor':a})
   ws=await c(sc,'find_actors',{'name':'WorldSettings','tag':'','collision_channels':[]})
   if len(ws)!=1:raise RuntimeError('Could not identify WorldSettings')
   await props(ws[0],{'defaultGameMode':ref('/Script/MegaJam.DirectorCutTestMode')})
   async def add(name,path,x,y,z,sx=1,sy=1,sz=1):return await c(sc,'add_to_scene_from_asset',{'asset_path':path,'name':name,'xform':{'location':{'x':x,'y':y,'z':z},'scale':{'x':sx,'y':sy,'z':sz}}})
   floor1=await add('Resolution_StartFloor','/Engine/BasicShapes/Cube.Cube',-135,0,-50,9.1,4,1)
   floor2=await add('Resolution_EndFloor','/Engine/BasicShapes/Cube.Cube',1570,0,-50,9,4,1)
   wall=await add('Resolution_BackWall','/Engine/BasicShapes/Cube.Cube',680,-300,275,24,.2,6.5)
   for a,m in [(floor1,'M_Floor_Stone'),(floor2,'M_Floor_Stone'),(wall,'M_Stone_Plum')]:
    await props(ref(a['refPath']+'.StaticMeshComponent0'),{'overrideMaterials':[ref('/Game/Stage1Generated/Meshes/'+m+'.'+m)]})
   for i,x in enumerate([400,560,720,880,1040]):
    a=await add('Resolution_Tile_'+str(i+1),folder+'/BP_ResolutionTile.BP_ResolutionTile',x,0,-12)
    await props(a,{'bSafe':i in [0,2,4],'safeOrder':i//2 if i in [0,2,4] else 0})
   arrows=[]
   for i,x in enumerate([400,720,1040]):
    a=await add('Resolution_Guide_'+str(i+1),folder+'/SM_ResolutionArrow.SM_ResolutionArrow',x,-230,160,1,1,1)
    await props(ref(a['refPath']+'.StaticMeshComponent0'),{'bodyInstance':{'collisionEnabled':'NoCollision','collisionProfileName':'NoCollision'},'castShadow':False})
    arrows.append(a)
   door=await add('Resolution_ExitDoor','/Game/Stage2ShadowPrototype/BP_S2_Door.BP_S2_Door',1350,0,150,.5,3,3)
   ctrl=await add('Resolution_Controller',folder+'/BP_ResolutionCorridor.BP_ResolutionCorridor',0,0,0)
   await props(ctrl,{'guidanceArrows':arrows,'exitDoor':door})
   for x in [320,1120]:
    column=await add('Resolution_Portal_Post','/Engine/BasicShapes/Cube.Cube',x,-270,170,.18,.35,3.4)
    await props(ref(column['refPath']+'.StaticMeshComponent0'),{'overrideMaterials':[ref('/Game/Stage1Generated/Meshes/M_Backstage_Wood.M_Backstage_Wood')],'bodyInstance':{'collisionEnabled':'NoCollision','collisionProfileName':'NoCollision'}})
   label=await c(sc,'add_to_scene_from_class',{'actor_type':ref('/Script/Engine.TextRenderActor'),'name':'Resolution_StartLabel','xform':{'location':{'x':20,'y':-230,'z':235},'rotation':{'pitch':0,'yaw':90,'roll':0}}})
   await props(ref(label['refPath']+'.NewTextRenderComponent'),{'text':'LOW RESOLUTION: FIND THE PATH','worldSize':20.0,'textRenderColor':{'r':.85,'g':.75,'b':.4,'a':1}})
   await c(assets,'save_assets',{'asset_paths':[dest]})
asyncio.run(main())
