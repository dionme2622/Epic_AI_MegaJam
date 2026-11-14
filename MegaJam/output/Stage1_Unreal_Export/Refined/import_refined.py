import asyncio,json
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError:raise RuntimeError(f'{n}: {z.content}')
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:550],flush=True);return v
   folder='/Game/Stage1Generated/RefinedMachinery';mat='editor_toolset.toolsets.material.MaterialTools';obj='editor_toolset.toolsets.object.ObjectTools';sm='editor_toolset.toolsets.static_mesh.StaticMeshTools';asset='editor_toolset.toolsets.asset.AssetTools'
   ref=lambda x:{'refPath':x}
   async def props(o,v):return await c(obj,'set_properties',{'instance':o,'values':json.dumps(v)})
   materials={}
   settings=[('WheelStone',(.20,.18,.20),0,.82),('WheelStoneLight',(.43,.37,.32),0,.78),('AgedBronze',(.39,.20,.055),.70,.38),('PaleBrass',(.68,.42,.12),.65,.30),('DarkIron',(.075,.095,.11),.72,.42)]
   for name,color,metal,rough in settings:
    m=await c(mat,'create_material',{'folder_path':folder,'asset_name':'M_'+name});materials[name]=m
    e=await c(mat,'add_expression',{'material_or_function':m,'expression_class':ref('/Script/Engine.MaterialExpressionConstant3Vector'),'x':-450,'y':0})
    await props(e,{'constant':dict(zip(['r','g','b','a'],[*color,1]))})
    await c(mat,'connect_to_output',{'expression':e,'output_name':'','material_property':'MP_BaseColor'})
    for k,val,y in [('MP_Metallic',metal,180),('MP_Roughness',rough,280)]:
     e=await c(mat,'add_expression',{'material_or_function':m,'expression_class':ref('/Script/Engine.MaterialExpressionConstant'),'x':-450,'y':y})
     await props(e,{'r':val});await c(mat,'connect_to_output',{'expression':e,'output_name':'','material_property':k})
    await c(mat,'recompile',{'material_or_function':m})
   models=['Wheel_Refined_High','Wheel_Refined_Low','Gear_Refined_High','Gear_Refined_Low']
   mapping={'Wheel_Refined_High':['WheelStone','DarkIron','AgedBronze','WheelStoneLight','PaleBrass'],'Wheel_Refined_Low':['WheelStone','DarkIron','AgedBronze','WheelStoneLight','PaleBrass'],'Gear_Refined_High':['AgedBronze','DarkIron','PaleBrass'],'Gear_Refined_Low':['AgedBronze','DarkIron','PaleBrass']}
   for name in models:
    await c(sm,'import_file',{'folder_path':folder,'asset_name':name,'source_file':str(Path('C:/LHH/Epic_AI_MegaJam/MegaJam/output/Stage1_Unreal_Export/Refined')/(name+'.fbx')).replace('\\','/'),'import_materials':False,'import_textures':False,'combine_meshes':True})
    info=await c(obj,'get_properties',{'instance':ref(folder+'/'+name+'.'+name),'properties':['staticMaterials']})
    print('SLOTS',name,info,flush=True)
   Path('output/Stage1_Unreal_Export/Refined/material_mapping.json').write_text(json.dumps(mapping,indent=2),encoding='utf8')
   await c(asset,'save_assets',{'asset_paths':[folder+'/'+n for n in models]+[folder+'/M_'+n for n,_,_,_ in settings]})
asyncio.run(main())
