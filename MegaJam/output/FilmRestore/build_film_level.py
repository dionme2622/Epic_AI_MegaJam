import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError: raise RuntimeError(f'{n}: {z.content}')
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:180],flush=True);return v
   folder='/Game/FilmRestorePrototype';dest='/Game/Level/Stage2_FilmRestore_Prototype';asset='editor_toolset.toolsets.asset.AssetTools';scene='editor_toolset.toolsets.scene.SceneTools';bp='editor_toolset.toolsets.blueprint.BlueprintTools';obj='editor_toolset.toolsets.object.ObjectTools';sm='editor_toolset.toolsets.static_mesh.StaticMeshTools';mat='editor_toolset.toolsets.material.MaterialTools'
   ref=lambda x:{'refPath':x}
   async def props(o,v):await c(obj,'set_properties',{'instance':o,'values':json.dumps(v)})
   names=['SM_Film_Frame','SM_Film_Three','SM_Film_Arrow','SM_Film_Shadow','SM_Film_Gear','SM_Film_Projector']
   for name in names:await c(sm,'import_file',{'folder_path':folder,'asset_name':name,'source_file':'C:/LHH/Epic_AI_MegaJam/MegaJam/output/FilmRestore/'+name+'.fbx','import_materials':False,'import_textures':False,'combine_meshes':True})
   m=await c(mat,'create_material',{'folder_path':folder,'asset_name':'M_FilmExposureInk'})
   ex=await c(mat,'add_expression',{'material_or_function':m,'expression_class':ref('/Script/Engine.MaterialExpressionConstant3Vector'),'x':-300,'y':0})
   await props(ex,{'constant':{'r':2.0,'g':1.4,'b':.55,'a':1}})
   await c(mat,'connect_to_output',{'expression':ex,'output_name':'','material_property':'MP_EmissiveColor'})
   await props(m,{'shadingModel':'MSM_Unlit'});await c(mat,'recompile',{'material_or_function':m})
   await c(bp,'create',{'folder_path':folder,'asset_name':'BP_FilmRestorePuzzle','asset_type':ref('/Script/MegaJam.FilmRestorePuzzle')})
   cdo=folder+'/BP_FilmRestorePuzzle.Default__BP_FilmRestorePuzzle_C:'
   cube=ref('/Engine/BasicShapes/Cube.Cube');dark=ref('/Game/BloomPuzzlePrototype/M_BloomInk.M_BloomInk');bright=ref('/Game/BloomPuzzlePrototype/M_BloomFace.M_BloomFace');gold=ref('/Game/Stage1Generated/Meshes/M_Brass_Trim.M_Brass_Trim')
   mesh=lambda n:ref(folder+'/'+n+'.'+n)
   cases=[('Frame',mesh('SM_Film_Frame'),gold),('Screen',cube,bright),('ClueA',mesh('SM_Film_Three'),dark),('ClueB',mesh('SM_Film_Arrow'),dark),('ClueC',mesh('SM_Film_Gear'),m),('ShadowMask',mesh('SM_Film_Shadow'),dark)]
   for comp,meshval,material in cases:
    vals={'staticMesh':meshval,'overrideMaterials':[material]}
    if comp=='Screen':vals['relativeScale3D']={'x':5.3,'y':.08,'z':3.3}
    if comp=='ClueA':vals['relativeScale3D']={'x':.6,'y':1,'z':.6}
    await props(ref(cdo+comp),vals)
   await c(bp,'compile_blueprint',{'blueprint':ref(folder+'/BP_FilmRestorePuzzle.BP_FilmRestorePuzzle')})
   ok=await c(asset,'duplicate',{'path':'/Game/Level/Stage2_FocusProp_Prototype','new_path':dest})
   if not ok:raise RuntimeError('Level duplicate failed')
   await c(asset,'save_assets',{'asset_paths':[dest,folder+'/BP_FilmRestorePuzzle',folder+'/M_FilmExposureInk']+[folder+'/'+n for n in names]})
   await c(scene,'load_level',{'level_path':dest})
   actors=await c(scene,'find_actors',{'name':'Focus','tag':'','collision_channels':[]})
   for a in actors:await c(scene,'remove_from_scene',{'actor':a})
   async def add(name,path,x,y,z,sx=1,sy=1,sz=1):return await c(scene,'add_to_scene_from_asset',{'asset_path':path,'name':name,'xform':{'location':{'x':x,'y':y,'z':z},'scale':{'x':sx,'y':sy,'z':sz}}})
   flo=await add('Film_Floor','/Engine/BasicShapes/Cube.Cube',450,0,-50,18,8,1)
   wall=await add('Film_Backdrop','/Engine/BasicShapes/Cube.Cube',450,-450,300,18,.2,7)
   for a,material in [(flo,'M_Floor_Stone'),(wall,'M_Stone_Plum')]:
    await props(ref(a['refPath']+'.StaticMeshComponent0'),{'overrideMaterials':[ref('/Game/Stage1Generated/Meshes/'+material+'.'+material)]})
   pp=await c(scene,'add_to_scene_from_class',{'actor_type':ref('/Script/Engine.PostProcessVolume'),'name':'Film_PostProcess','xform':{'location':{'x':0,'y':0,'z':0}}});await props(pp,{'bUnbound':True})
   door=await add('Film_ExitDoor','/Game/Stage2ShadowPrototype/BP_S2_Door.BP_S2_Door',1150,0,150,.5,3,3)
   puzzle=await add('Film_Controller',folder+'/BP_FilmRestorePuzzle.BP_FilmRestorePuzzle',0,0,0)
   await props(puzzle,{'exitDoor':door,'postProcessVolume':pp})
   projector=await add('Film_Projector',folder+'/SM_Film_Projector.SM_Film_Projector',100,-150,0)
   await props(ref(projector['refPath']+'.StaticMeshComponent0'),{'overrideMaterials':[gold],'bodyInstance':{'collisionEnabled':'NoCollision','collisionProfileName':'NoCollision'}})
   for group,material in [('Wood','M_Backstage_Wood'),('Brass','M_Brass_Trim'),('Curtain','M_Theatre_Curtain')]:
    path=f'/Game/FocusPropPrototype/Detail/SM_FocusDetail_{group}.SM_FocusDetail_{group}'
    a=await add('Film_Set_'+group,path,0,-130,0)
    await props(ref(a['refPath']+'.StaticMeshComponent0'),{'overrideMaterials':[ref('/Game/Stage1Generated/Meshes/'+material+'.'+material)],'bodyInstance':{'collisionEnabled':'NoCollision','collisionProfileName':'NoCollision'}})
   label=await c(scene,'add_to_scene_from_class',{'actor_type':ref('/Script/Engine.TextRenderActor'),'name':'Film_Instructions','xform':{'location':{'x':-160,'y':-220,'z':280},'rotation':{'pitch':0,'yaw':90,'roll':0}}})
   await props(ref(label['refPath']+'.NewTextRenderComponent'),{'text':'E: USE PROJECTOR','worldSize':32.0,'textRenderColor':{'r':1,'g':.8,'b':.2,'a':1}})
   await c(asset,'save_assets',{'asset_paths':[dest]})
asyncio.run(main())
