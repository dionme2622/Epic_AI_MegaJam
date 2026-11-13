import asyncio,json
from pathlib import Path
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
   bp='editor_toolset.toolsets.blueprint.BlueprintTools'
   obj='editor_toolset.toolsets.object.ObjectTools'
   act='editor_toolset.toolsets.actor.ActorTools'
   director='/Game/Stage1Generated/BP_Stage1Director.BP_Stage1Director'
   player='/Game/Stage1Generated/BP_Stage1Dragon.BP_Stage1Dragon'
   level='/Game/Level/Stage1.Stage1:PersistentLevel.'
   await call(bp,'add_variable',{'blueprint':{'refPath':director},'name':'LiftDescending','type_name':'bool'})
   await call(bp,'write_graph_dsl',{'graph':{'refPath':director+':EventGraph'},'code':Path('output/Stage1_Unreal_Export/director_v3.dsl').read_text(encoding='utf8')})
   await call(bp,'write_graph_dsl',{'graph':{'refPath':player+':EventGraph'},'code':Path('output/Stage1_Unreal_Export/player_v3.dsl').read_text(encoding='utf8')})
   for path in ['/Game/Stage1Generated/BP_Stage1Dragon.Default__BP_Stage1Dragon_C:CharacterMesh0',level+'BP_Stage1Dragon_C_0.CharacterMesh0']:
    await call(obj,'set_properties',{'instance':{'refPath':path},'values':json.dumps({'relativeScale3D':{'x':1.8,'y':1.8,'z':1.8}})})
   await call(act,'set_actor_transform',{'actor':{'refPath':level+'StaticMeshActor_9'},'xform':{'location':{'x':8700,'y':0,'z':22}}})
   await call(act,'set_actor_transform',{'actor':{'refPath':level+'CameraActor_0'},'xform':{'rotation':{'pitch':-4,'yaw':-90,'roll':0}}})
   await call(obj,'set_properties',{'instance':{'refPath':level+'StaticMeshActor_7'},'values':json.dumps({'bActorEnableCollision':False})})
   scene='editor_toolset.toolsets.scene.SceneTools'
   back=await call(scene,'add_to_scene_from_asset',{'asset_path':'/Engine/BasicShapes/Cube.Cube','name':'Stage1_BackgroundFill','xform':{'location':{'x':4500,'y':-500,'z':200},'scale':{'x':150,'y':0.05,'z':25}}})
   print('BACK',back,flush=True)
   await call(obj,'set_properties',{'instance':back,'values':json.dumps({'bActorEnableCollision':False})})
   await call(obj,'set_properties',{'instance':{'refPath':back['refPath']+'.StaticMeshComponent0'},'values':json.dumps({'overrideMaterials':[{'refPath':'/Game/Stage1Generated/Meshes/M_Painted_Backdrop.M_Painted_Backdrop'}]})})
   await call('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':['/Game/Level/Stage1','/Game/Stage1Generated/BP_Stage1Director','/Game/Stage1Generated/BP_Stage1Dragon']})
asyncio.run(main())
