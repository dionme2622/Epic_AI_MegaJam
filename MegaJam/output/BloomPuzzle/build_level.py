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
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:220],flush=True);return v
   folder='/Game/BloomPuzzlePrototype';dest='/Game/Level/Stage2_BloomSign_Prototype'
   asset='editor_toolset.toolsets.asset.AssetTools';scene='editor_toolset.toolsets.scene.SceneTools';bp='editor_toolset.toolsets.blueprint.BlueprintTools';obj='editor_toolset.toolsets.object.ObjectTools';sm='editor_toolset.toolsets.static_mesh.StaticMeshTools'
   async def props(ref,values):return await c(obj,'set_properties',{'instance':ref,'values':json.dumps(values)})
   for name in ['SM_Bloom_Frame','SM_Bloom_Star','SM_Bloom_Moon','SM_Bloom_Sun']:
    await c(sm,'import_file',{'folder_path':folder,'asset_name':name,'source_file':'C:/LHH/Epic_AI_MegaJam/MegaJam/output/BloomPuzzle/'+name+'.fbx','import_materials':False,'import_textures':False,'combine_meshes':True})
   for name,parent in [('BP_BloomSign','BloomPuzzleSign'),('BP_BloomController','BloomSignPuzzle')]:
    await c(bp,'create',{'folder_path':folder,'asset_name':name,'asset_type':{'refPath':'/Script/MegaJam.'+parent}})
   sign=folder+'/BP_BloomSign.Default__BP_BloomSign_C:'
   def assetref(path):return {'refPath':path}
   await props(assetref(sign+'Frame'),{'staticMesh':assetref(folder+'/SM_Bloom_Frame.SM_Bloom_Frame'),'overrideMaterials':[assetref('/Game/Stage1Generated/Meshes/M_Brass_Trim.M_Brass_Trim')]})
   await props(assetref(sign+'Face'),{'staticMesh':assetref('/Engine/BasicShapes/Cube.Cube'),'relativeScale3D':{'x':1.3,'y':.06,'z':1.3},'overrideMaterials':[assetref(folder+'/M_BloomFace.M_BloomFace')]})
   await props(assetref(sign+'Symbol'),{'overrideMaterials':[assetref(folder+'/M_BloomInk.M_BloomInk')]})
   await props(assetref(folder+'/BP_BloomController.Default__BP_BloomController_C:ConsoleMesh'),{'staticMesh':assetref('/Engine/BasicShapes/Cube.Cube'),'relativeScale3D':{'x':1.4,'y':.8,'z':1.4},'overrideMaterials':[assetref('/Game/Stage1Generated/Meshes/M_Backstage_Wood.M_Backstage_Wood')]})
   for name in ['BP_BloomSign','BP_BloomController']:await c(bp,'compile_blueprint',{'blueprint':assetref(folder+'/'+name+'.'+name)})
   result=await c(asset,'duplicate',{'path':'/Game/Level/Stage2_FocusProp_Prototype','new_path':dest})
   if not result:raise RuntimeError('Level copy failed')
   await c(asset,'save_assets',{'asset_paths':[dest,folder+'/BP_BloomSign',folder+'/BP_BloomController']+[folder+'/'+n for n in ['SM_Bloom_Frame','SM_Bloom_Star','SM_Bloom_Moon','SM_Bloom_Sun']]})
   await c(scene,'load_level',{'level_path':dest})
   actors=await c(scene,'find_actors',{'name':'Focus','tag':'','collision_channels':[]})
   for actor in actors:await c(scene,'remove_from_scene',{'actor':actor})
   async def add(name,path,x,y,z,sx=1,sy=1,sz=1):return await c(scene,'add_to_scene_from_asset',{'asset_path':path,'name':name,'xform':{'location':{'x':x,'y':y,'z':z},'scale':{'x':sx,'y':sy,'z':sz}}})
   cube='/Engine/BasicShapes/Cube.Cube'
   floor=await add('Bloom_Floor',cube,1050,0,-50,32,6,1)
   wall=await add('Bloom_Wall',cube,1050,-300,300,32,.2,7)
   for a,mat in [(floor,'M_Floor_Stone'),(wall,'M_Stone_Plum')]:
    await props(assetref(a['refPath']+'.StaticMeshComponent0'),{'overrideMaterials':[assetref(f'/Game/Stage1Generated/Meshes/{mat}.{mat}')]})
   for i,(x,symbol) in enumerate([(350,'Star'),(900,'Moon'),(1450,'Sun')],1):
    a=await add('Bloom_Sign_'+symbol,folder+'/BP_BloomSign.BP_BloomSign',x,-160,245)
    await props(assetref(a['refPath']+'.Symbol'),{'staticMesh':assetref(f'{folder}/SM_Bloom_{symbol}.SM_Bloom_{symbol}')})
    label=await c(scene,'add_to_scene_from_class',{'actor_type':assetref('/Script/Engine.TextRenderActor'),'name':'Bloom_Number_'+str(i),'xform':{'location':{'x':x,'y':-175,'z':350},'rotation':{'pitch':0,'yaw':90,'roll':0}}})
    await props(assetref(label['refPath']+'.NewTextRenderComponent'),{'text':str(i),'worldSize':38.0,'textRenderColor':{'r':1,'g':.8,'b':.2,'a':1}})
   pp=await c(scene,'add_to_scene_from_class',{'actor_type':assetref('/Script/Engine.PostProcessVolume'),'name':'Bloom_PostProcess','xform':{'location':{'x':0,'y':0,'z':0}}})
   await props(pp,{'bUnbound':True})
   door=await add('Bloom_ExitDoor','/Game/Stage2ShadowPrototype/BP_S2_Door.BP_S2_Door',2300,0,150,.5,3,3)
   ctl=await add('Bloom_Controller',folder+'/BP_BloomController.BP_BloomController',2000,0,70)
   await props(ctl,{'postProcessVolume':pp,'exitDoor':door,'bloomIntensity':7})
   label=await c(scene,'add_to_scene_from_class',{'actor_type':assetref('/Script/Engine.TextRenderActor'),'name':'Bloom_Instructions','xform':{'location':{'x':-170,'y':-220,'z':300},'rotation':{'pitch':0,'yaw':90,'roll':0}}})
   await props(assetref(label['refPath']+'.NewTextRenderComponent'),{'text':'B: BLOOM ON/OFF\nFIND THE SIGN ORDER\nE: USE CONSOLE','worldSize':30.0,'textRenderColor':{'r':1,'g':.8,'b':.2,'a':1}})
   label2=await c(scene,'add_to_scene_from_class',{'actor_type':assetref('/Script/Engine.TextRenderActor'),'name':'Bloom_ConsoleLabel','xform':{'location':{'x':1900,'y':-175,'z':250},'rotation':{'pitch':0,'yaw':90,'roll':0}}})
   await props(assetref(label2['refPath']+'.NewTextRenderComponent'),{'text':'E: INPUT ORDER','worldSize':30.0,'textRenderColor':{'r':1,'g':.8,'b':.2,'a':1}})
   await c(asset,'save_assets',{'asset_paths':[dest]})
asyncio.run(main())
