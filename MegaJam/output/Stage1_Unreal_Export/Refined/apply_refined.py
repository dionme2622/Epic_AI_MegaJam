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
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:200],flush=True);return v
   sm='editor_toolset.toolsets.static_mesh.StaticMeshTools';ob='editor_toolset.toolsets.object.ObjectTools';assets='editor_toolset.toolsets.asset.AssetTools'
   root='/Game/Stage1Generated/RefinedMachinery';ref=lambda x:{'refPath':x}
   mapping=json.load(open('output/Stage1_Unreal_Export/Refined/material_mapping.json',encoding='utf8'))
   for name,mats in mapping.items():
    mesh=ref(root+'/'+name+'.'+name)
    for slot in mats:await c(sm,'set_material',{'mesh':mesh,'slot_name':slot,'material':ref(root+'/M_'+slot+'.M_'+slot)})
   for i,name in [(3,'Wheel_Refined_High'),(4,'Wheel_Refined_Low'),(5,'Gear_Refined_High'),(6,'Gear_Refined_Low')]:
    comp=ref(f'/Game/Level/Stage1.Stage1:PersistentLevel.StaticMeshActor_{i}.StaticMeshComponent0')
    await c(ob,'set_properties',{'instance':comp,'values':json.dumps({'staticMesh':ref(root+'/'+name+'.'+name),'overrideMaterials':[]})})
    await c(ob,'get_properties',{'instance':comp,'properties':['staticMesh','mobility']})
   await c(assets,'save_assets',{'asset_paths':['/Game/Level/Stage1']+[root+'/'+n for n in mapping]})
asyncio.run(main())
