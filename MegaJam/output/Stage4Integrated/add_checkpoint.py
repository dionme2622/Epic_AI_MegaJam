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
    return json.loads(z.content[0].text).get('returnValue')
   ref=lambda p:{'refPath':p};sc='editor_toolset.toolsets.scene.SceneTools';bp='editor_toolset.toolsets.blueprint.BlueprintTools';asset='editor_toolset.toolsets.asset.AssetTools';path='/Game/Stage4Integrated/L_ShadowStage';folder='/Game/Stage4Integrated';name='BP_ShadowStageCheckpoint';p=folder+'/'+name+'.'+name
   await c(sc,'load_level',{'level_path':path});ws=(await c(sc,'find_actors',{'name':'WorldSettings','tag':'','collision_channels':[]}))[0];assert path+'.' in ws['refPath']
   b=await c(bp,'create',{'folder_path':folder,'asset_name':name,'asset_type':ref('/Script/Engine.Actor')})
   code='''(event EventTick
    (bind pawn (Game|GetPlayerPawn :PlayerIndex 0))
    (bind pos (Transformation|GetActorLocation :self pawn))
    (bind checkpoint (Transformation|GetActorLocation :self self))
    (if (and (> (.x pos) (- (.x checkpoint) 40.0)) (< (.z pos) -140.0))
        (Transformation|SetActorLocation :self pawn :NewLocation checkpoint :bSweep false :bTeleport true)))'''
   await c(bp,'write_graph_dsl',{'graph':ref(p+':EventGraph'),'code':code});await c(bp,'compile_blueprint',{'blueprint':b})
   a=await c(sc,'add_to_scene_from_asset',{'asset_path':p,'name':'ShadowStage_FallCheckpoint','xform':{'location':{'x':-200,'y':0,'z':92}}});print('ADDED',a,flush=True)
   await c(asset,'save_assets',{'asset_paths':[path,folder+'/'+name]});print('SAVED',flush=True)
asyncio.run(main())
