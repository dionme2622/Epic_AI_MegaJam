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
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:150],flush=True);return v
   folder='/Game/FocusPropPrototype/Detail'; obj='editor_toolset.toolsets.object.ObjectTools';bp='editor_toolset.toolsets.blueprint.BlueprintTools';scene='editor_toolset.toolsets.scene.SceneTools';assets='editor_toolset.toolsets.asset.AssetTools'
   for group in ['Wood','Brass','Curtain','Head','Shaft']:
    name='SM_FocusDetail_'+group
    await c('editor_toolset.toolsets.static_mesh.StaticMeshTools','import_file',{'folder_path':folder,'asset_name':name,'source_file':'C:/LHH/Epic_AI_MegaJam/MegaJam/output/FocusPuzzle/Detail/'+name+'.fbx','import_materials':False,'import_textures':False,'combine_meshes':True})
   for comp,group in [('NearPiece','Head'),('FarPiece','Shaft')]:
    await c(obj,'set_properties',{'instance':{'refPath':'/Game/FocusPropPrototype/BP_FocusPropPuzzle.Default__BP_FocusPropPuzzle_C:'+comp},'values':json.dumps({'staticMesh':{'refPath':f'{folder}/SM_FocusDetail_{group}.SM_FocusDetail_{group}'}})})
   await c(bp,'compile_blueprint',{'blueprint':{'refPath':'/Game/FocusPropPrototype/BP_FocusPropPuzzle.BP_FocusPropPuzzle'}})
   level='/Game/Level/Stage2_FocusProp_Prototype.Stage2_FocusProp_Prototype:PersistentLevel.'
   for comp,group in [('NearPiece','Head'),('FarPiece','Shaft')]:
    await c(obj,'set_properties',{'instance':{'refPath':level+'BP_FocusPropPuzzle_C_0.'+comp},'values':json.dumps({'staticMesh':{'refPath':f'{folder}/SM_FocusDetail_{group}.SM_FocusDetail_{group}'}})})
   for group,mat in [('Wood','M_Backstage_Wood'),('Brass','M_Brass_Trim'),('Curtain','M_Theatre_Curtain')]:
    name='SM_FocusDetail_'+group
    a=await c(scene,'add_to_scene_from_asset',{'asset_path':f'{folder}/{name}.{name}','name':'FocusDetail_'+group,'xform':{'location':{'x':0,'y':0,'z':0}}})
    component={'refPath':a['refPath']+'.StaticMeshComponent0'}
    material={'refPath':f'/Game/Stage1Generated/Meshes/{mat}.{mat}'}
    await c(obj,'set_properties',{'instance':component,'values':json.dumps({'overrideMaterials':[material],'bodyInstance':{'collisionEnabled':'NoCollision','collisionProfileName':'NoCollision'}})})
   paths=['/Game/FocusPropPrototype/BP_FocusPropPuzzle','/Game/Level/Stage2_FocusProp_Prototype']+[folder+'/SM_FocusDetail_'+x for x in ['Wood','Brass','Curtain','Head','Shaft']]
   await c(assets,'save_assets',{'asset_paths':paths})
asyncio.run(main())
