import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a});
    if z.isError: raise RuntimeError(f'{n}: {z.content}')
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:300],flush=True);return v
   asset='editor_toolset.toolsets.asset.AssetTools'; scene='editor_toolset.toolsets.scene.SceneTools'; bp='editor_toolset.toolsets.blueprint.BlueprintTools'; obj='editor_toolset.toolsets.object.ObjectTools'
   await c(scene,'load_level',{'level_path':'/Game/Level/Stage2_ShadowStealth_Prototype'})
   prefix='/Game/Stage2ShadowPrototype/'
   for suffix in ['Crate','Door','Lever','Spotlight','SectionManager']:
    await c(bp,'create',{'folder_path':prefix,'asset_name':'BP_S2_'+suffix,'asset_type':{'refPath':'/Script/MegaJam.Stage2Shadow'+suffix}})
   for suffix,component,mesh in [('Crate','Mesh','Cube'),('Door','Mesh','Cube'),('Lever','Mesh','Cylinder'),('Spotlight','Fixture','Cylinder')]:
    ref=f'{prefix}BP_S2_{suffix}.Default__BP_S2_{suffix}_C:{component}'
    await c(obj,'set_properties',{'instance':{'refPath':ref},'values':json.dumps({'staticMesh':{'refPath':f'/Engine/BasicShapes/{mesh}.{mesh}'}})})
   for suffix in ['Crate','Door','Lever','Spotlight','SectionManager']:
    await c(bp,'compile_blueprint',{'blueprint':{'refPath':f'{prefix}BP_S2_{suffix}.BP_S2_{suffix}'}})
   await c(asset,'save_assets',{'asset_paths':[prefix+'BP_S2_'+x for x in ['Crate','Door','Lever','Spotlight','SectionManager']]})
asyncio.run(main())
