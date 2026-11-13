import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (rd,wr,_):
  async with ClientSession(rd,wr) as s:
   await s.initialize()
   async def call(ts,n,a):
    r=await s.call_tool('call_tool',{'toolset_name':ts,'tool_name':n,'arguments':a})
    print(n,r.content[0].text[:1500],flush=True)
    if r.isError: raise RuntimeError(str(r.content))
    return json.loads(r.content[0].text).get('returnValue')
   scene='editor_toolset.toolsets.scene.SceneTools'
   obj='editor_toolset.toolsets.object.ObjectTools'
   back=await call(scene,'add_to_scene_from_asset',{'asset_path':'/Engine/BasicShapes/Cube.Cube','name':'Stage1_BackgroundFill','xform':{'location':{'x':4500,'y':-500,'z':200},'scale':{'x':150,'y':0.05,'z':25}}})
   await call(obj,'set_properties',{'instance':{'refPath':back['refPath']+'.StaticMeshComponent0'},'values':json.dumps({'overrideMaterials':[{'refPath':'/Game/Stage1Generated/Meshes/M_Painted_Backdrop.M_Painted_Backdrop'}],'bodyInstance':{'collisionEnabled':'NoCollision','collisionProfileName':'NoCollision'}})})
   await call('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':['/Game/Level/Stage1','/Game/Stage1Generated/BP_Stage1Director','/Game/Stage1Generated/BP_Stage1Dragon']})
asyncio.run(main())
