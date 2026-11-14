import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError: raise RuntimeError(str(z.content))
    print(n,z.content[0].text[:250],flush=True)
   root='/Game/Level/Stage2_FocusProp_Prototype.Stage2_FocusProp_Prototype:PersistentLevel.'
   bp='/Game/FocusPropPrototype/BP_FocusPropPuzzle.Default__BP_FocusPropPuzzle_C:'
   mat='/Game/Stage1Generated/Meshes/'
   cases=[(bp+'NearPiece','M_Brass_Trim'),(bp+'FarPiece','M_Brass_Trim'),(root+'StaticMeshActor_3.StaticMeshComponent0','M_Floor_Stone'),(root+'StaticMeshActor_4.StaticMeshComponent0','M_Stone_Plum'),(root+'StaticMeshActor_5.StaticMeshComponent0','M_Backstage_Wood')]
   for path,name in cases:
    await c('editor_toolset.toolsets.object.ObjectTools','set_properties',{'instance':{'refPath':path},'values':json.dumps({'overrideMaterials':[{'refPath':f'{mat}{name}.{name}'}]})})
   await c('editor_toolset.toolsets.blueprint.BlueprintTools','compile_blueprint',{'blueprint':{'refPath':'/Game/FocusPropPrototype/BP_FocusPropPuzzle.BP_FocusPropPuzzle'}})
   await c('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':['/Game/FocusPropPrototype/BP_FocusPropPuzzle','/Game/Level/Stage2_FocusProp_Prototype']})
asyncio.run(main())
