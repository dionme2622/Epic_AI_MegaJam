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
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:400],flush=True);return v
   asset='editor_toolset.toolsets.asset.AssetTools'; scene='editor_toolset.toolsets.scene.SceneTools'; bp='editor_toolset.toolsets.blueprint.BlueprintTools';obj='editor_toolset.toolsets.object.ObjectTools'
   folder='/Game/FocusPropPrototype'; dest='/Game/Level/Stage2_FocusProp_Prototype'
   '''
   for name in ['SM_Focus_KeyHead','SM_Focus_KeyShaft']:
    await c('editor_toolset.toolsets.static_mesh.StaticMeshTools','import_file',{'folder_path':folder,'asset_name':name,'source_file':'C:/LHH/Epic_AI_MegaJam/MegaJam/output/FocusPuzzle/'+name+'.fbx','import_materials':True,'import_textures':False,'combine_meshes':True})
   await c(bp,'create',{'folder_path':folder,'asset_name':'BP_FocusPropPuzzle','asset_type':{'refPath':'/Script/MegaJam.FocusPropPuzzle'}})
   for comp,name in [('NearPiece','SM_Focus_KeyHead'),('FarPiece','SM_Focus_KeyShaft')]:
    await c(obj,'set_properties',{'instance':{'refPath':folder+'/BP_FocusPropPuzzle.Default__BP_FocusPropPuzzle_C:'+comp},'values':json.dumps({'staticMesh':{'refPath':f'{folder}/{name}.{name}'}})})
   await c(bp,'compile_blueprint',{'blueprint':{'refPath':folder+'/BP_FocusPropPuzzle.BP_FocusPropPuzzle'}})
   '''
   await c(asset,'duplicate',{'path':'/Game/Level/Stage2_ShadowStealth_Prototype','new_path':dest})
   await c(asset,'save_assets',{'asset_paths':['/Game/NewMap',dest,folder+'/BP_FocusPropPuzzle',folder+'/SM_Focus_KeyHead',folder+'/SM_Focus_KeyShaft']})
   await c(scene,'load_level',{'level_path':dest})
   old=await c(scene,'find_actors',{'name':'SS_','tag':'','collision_channels':[]})
   for actor in old: await c(scene,'remove_from_scene',{'actor':actor})
   async def add(name,path,x,y,z,sx=1,sy=1,sz=1):return await c(scene,'add_to_scene_from_asset',{'asset_path':path,'name':name,'xform':{'location':{'x':x,'y':y,'z':z},'scale':{'x':sx,'y':sy,'z':sz}}})
   cube='/Engine/BasicShapes/Cube.Cube'
   await add('Focus_Floor',cube,450,0,-50,18,8,1)
   await add('Focus_BackWall',cube,450,-450,300,18,.2,7)
   await add('Focus_Stage',cube,500,-300,75,7,4,1.5)
   door=await add('Focus_ExitDoor','/Game/Stage2ShadowPrototype/BP_S2_Door.BP_S2_Door',1150,0,150,.5,3,3)
   puzzle=await add('Focus_Controller',folder+'/BP_FocusPropPuzzle.BP_FocusPropPuzzle',0,0,0)
   await c(obj,'set_properties',{'instance':puzzle,'values':json.dumps({'exitDoor':door})})
   label=await c(scene,'add_to_scene_from_class',{'actor_type':{'refPath':'/Script/Engine.TextRenderActor'},'name':'Focus_Controls','xform':{'location':{'x':-140,'y':-210,'z':280},'rotation':{'pitch':0,'yaw':90,'roll':0}}})
   await c(obj,'set_properties',{'instance':{'refPath':label['refPath']+'.NewTextRenderComponent'},'values':json.dumps({'text':'FOCUS PUZZLE\nE: USE CAMERA','worldSize':32.0,'textRenderColor':{'r':1,'g':.8,'b':.2,'a':1}})})
   await c(asset,'save_assets',{'asset_paths':[dest]})
asyncio.run(main())
