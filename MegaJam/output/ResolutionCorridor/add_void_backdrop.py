import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError:raise RuntimeError(str(z.content))
    return json.loads(z.content[0].text).get('returnValue')
   sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';assets='editor_toolset.toolsets.asset.AssetTools'
   ref=lambda p:{'refPath':p}
   a=await c(sc,'add_to_scene_from_asset',{'asset_path':'/Engine/BasicShapes/Cube.Cube','name':'Resolution_NonblockingPit','xform':{'location':{'x':680,'y':0,'z':-230},'scale':{'x':24,'y':14,'z':.2}}})
   await c(ob,'set_properties',{'instance':ref(a['refPath']+'.StaticMeshComponent0'),'values':json.dumps({'overrideMaterials':[ref('/Game/Stage1Generated/Meshes/M_Stone_Dark.M_Stone_Dark')],'bodyInstance':{'collisionEnabled':'NoCollision','collisionProfileName':'NoCollision'}})})
   await c(assets,'save_assets',{'asset_paths':['/Game/Level/Stage2_ResolutionCorridor_Prototype']})
   print('BACKDROP',a)
asyncio.run(main())
