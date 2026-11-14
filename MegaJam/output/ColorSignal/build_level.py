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
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:200],flush=True);return v
   folder='/Game/ColorSignalPrototype';dest='/Game/Level/Stage2_ColorSignal_Prototype'
   asset='editor_toolset.toolsets.asset.AssetTools';scene='editor_toolset.toolsets.scene.SceneTools';bp='editor_toolset.toolsets.blueprint.BlueprintTools';obj='editor_toolset.toolsets.object.ObjectTools';mat='editor_toolset.toolsets.material.MaterialTools';tex='editor_toolset.toolsets.texture.TextureTools'
   ref=lambda x:{'refPath':x}
   async def props(o,v):await c(obj,'set_properties',{'instance':o,'values':json.dumps(v)})
   texture=(await c(tex,'import_file',{'folder_path':folder,'asset_name':'T_ColorSignal','source_file':'C:/LHH/Epic_AI_MegaJam/MegaJam/output/ColorSignal/SignalAtlas.png'}))[0]
   m=await c(mat,'create_material',{'folder_path':folder,'asset_name':'M_ColorSignal'})
   ex=await c(mat,'add_expression',{'material_or_function':m,'expression_class':ref('/Script/Engine.MaterialExpressionTextureSample'),'x':-300,'y':0})
   await props(ex,{'texture':texture})
   await c(mat,'connect_to_output',{'expression':ex,'output_name':'RGB','material_property':'MP_EmissiveColor'})
   await props(m,{'shadingModel':'MSM_Unlit'});await c(mat,'recompile',{'material_or_function':m})
   white=await c(mat,'create_material',{'folder_path':folder,'asset_name':'M_SignalWhite'})
   e=await c(mat,'add_expression',{'material_or_function':white,'expression_class':ref('/Script/Engine.MaterialExpressionConstant3Vector'),'x':-300,'y':0})
   await props(e,{'constant':{'r':.65,'g':.65,'b':.65,'a':1}})
   await c(mat,'connect_to_output',{'expression':e,'output_name':'','material_property':'MP_EmissiveColor'})
   await props(white,{'shadingModel':'MSM_Unlit'});await c(mat,'recompile',{'material_or_function':white})
   await c(bp,'create',{'folder_path':folder,'asset_name':'BP_ColorSignalPuzzle','asset_type':ref('/Script/MegaJam.ColorSignalPuzzle')})
   cdo=folder+'/BP_ColorSignalPuzzle.Default__BP_ColorSignalPuzzle_C:'
   cube=ref('/Engine/BasicShapes/Cube.Cube');gold=ref('/Game/Stage1Generated/Meshes/M_Brass_Trim.M_Brass_Trim')
   frame=ref('/Game/FilmRestorePrototype/SM_Film_Frame.SM_Film_Frame');arrow=ref('/Game/FilmRestorePrototype/SM_Film_Arrow.SM_Film_Arrow')
   for comp,mesh,material,scale in [('Frame',frame,gold,(1.25,1,1)),('SignalPanel',cube,m,(6.8,.08,1.2)),('RecordBackground',cube,white,(6.8,.08,3.2))]+[(f'Dial{i}',arrow,white,(.45,1,.45)) for i in range(1,5)]:
    await props(ref(cdo+comp),{'staticMesh':mesh,'overrideMaterials':[material],'relativeScale3D':dict(zip(('x','y','z'),scale))})
   await c(bp,'compile_blueprint',{'blueprint':ref(folder+'/BP_ColorSignalPuzzle.BP_ColorSignalPuzzle')})
   ok=await c(asset,'duplicate',{'path':'/Game/Level/Stage2_FocusProp_Prototype','new_path':dest})
   if not ok:raise RuntimeError('Level duplicate failed')
   await c(asset,'save_assets',{'asset_paths':[dest,folder+'/BP_ColorSignalPuzzle',folder+'/M_ColorSignal',folder+'/M_SignalWhite',folder+'/T_ColorSignal']})
   await c(scene,'load_level',{'level_path':dest})
   for a in await c(scene,'find_actors',{'name':'Focus','tag':'','collision_channels':[]}):await c(scene,'remove_from_scene',{'actor':a})
   async def add(name,path,x,y,z,sx=1,sy=1,sz=1):return await c(scene,'add_to_scene_from_asset',{'asset_path':path,'name':name,'xform':{'location':{'x':x,'y':y,'z':z},'scale':{'x':sx,'y':sy,'z':sz}}})
   floor=await add('Color_Floor','/Engine/BasicShapes/Cube.Cube',450,0,-50,18,8,1)
   wall=await add('Color_Backdrop','/Engine/BasicShapes/Cube.Cube',450,-450,300,18,.2,7)
   for a,material in [(floor,'M_Floor_Stone'),(wall,'M_Stone_Pl em'.replace('Pl em','Plum'))]:
    await props(ref(a['refPath']+'.StaticMeshComponent0'),{'overrideMaterials':[ref('/Game/Stage1Generated/Meshes/'+material+'.'+material)]})
   door=await add('Color_ExitDoor','/Game/Stage2ShadowPrototype/BP_S2_Door.BP_S2_Door',1150,0,150,.5,3,3)
   puzzle=await add('Color_Controller',folder+'/BP_ColorSignalPuzzle.BP_ColorSignalPuzzle',0,0,0)
   await props(puzzle,{'exitDoor':door})
   for group,material in [('Wood','M_Backstage_Wood'),('Brass','M_Brass_Trim'),('Curtain','M_Theatre_Curtain')]:
    path=f'/Game/FocusPropPrototype/Detail/SM_FocusDetail_{group}.SM_FocusDetail_{group}'
    a=await add('Color_Set_'+group,path,0,-130,0)
    await props(ref(a['refPath']+'.StaticMeshComponent0'),{'overrideMaterials':[ref('/Game/Stage1Generated/Meshes/'+material+'.'+material)],'bodyInstance':{'collisionEnabled':'NoCollision','collisionProfileName':'NoCollision'}})
   label=await c(scene,'add_to_scene_from_class',{'actor_type':ref('/Script/Engine.TextRenderActor'),'name':'Color_Instructions','xform':{'location':{'x':-160,'y':-220,'z':280},'rotation':{'pitch':0,'yaw':90,'roll':0}}})
   await props(ref(label['refPath']+'.NewTextRenderComponent'),{'text':'E: USE COLOR SIGNAL','worldSize':32.0,'textRenderColor':{'r':1,'g':.8,'b':.2,'a':1}})
   await c(asset,'save_assets',{'asset_paths':[dest]})
asyncio.run(main())
