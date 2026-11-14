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
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:500],flush=True);return v
   ref=lambda p:{'refPath':p};sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';bp='editor_toolset.toolsets.blueprint.BlueprintTools';assets='editor_toolset.toolsets.asset.AssetTools';app='EditorToolset.EditorAppToolset'
   if await c(app,'IsPIERunning',{}):await c(app,'StopPIE',{})
   await c(sc,'load_level',{'level_path':'/Game/Level/Stage2_ShadowBody_Prototype'})
   ws=(await c(sc,'find_actors',{'name':'WorldSettings','tag':'','collision_channels':[]}))[0]
   assert '/Game/Level/Stage2_ShadowBody_Prototype.' in ws['refPath']
   await c(ob,'set_properties',{'instance':ws,'values':json.dumps({'defaultGameMode':ref('/Script/MegaJam.DirectorCutTestMode')})})
   folder='/Game/ShadowBodyStage';name='BP_DragonLowerCollectible';p=folder+'/'+name+'.'+name
   b=await c(bp,'create',{'folder_path':folder,'asset_name':name,'asset_type':ref('/Script/Engine.StaticMeshActor')})
   await c(bp,'add_variable',{'blueprint':b,'name':'Collected','type_name':'bool'})
   code='''(event EventTick
    (if (and (not (Variables|Default|GetCollected)) (> (.x (Transformation|GetActorLocation :self (Game|GetPlayerPawn :PlayerIndex 0))) (- (.x (Transformation|GetActorLocation :self self)) 100.0)))
       (Variables|Default|SetCollected true)
       (Rendering|SetActorHiddenInGame :self self :bNewHidden true)))'''
   await c(bp,'write_graph_dsl',{'graph':ref(p+':EventGraph'),'code':code})
   await c(bp,'compile_blueprint',{'blueprint':b})
   print('COMP',await c('editor_toolset.toolsets.actor.ActorTools','get_components',{'actor':ref(p+'.Default__BP_DragonLowerCollectible_C')}),flush=True)
   old=(await c(sc,'find_actors',{'name':'Dragon_LowerBody','tag':'','collision_channels':[]}))[0];await c(sc,'remove_from_scene',{'actor':old})
   a=await c(sc,'add_to_scene_from_asset',{'asset_path':p,'name':'Dragon_LowerBody_Collectible','xform':{'location':{'x':2340,'y':-25,'z':70}}})
   comp=ref(a['refPath']+'.StaticMeshComponent0')
   await c(ob,'set_properties',{'instance':comp,'values':json.dumps({'staticMesh':ref('/Game/ShadowBodyStage/SM_DragonLowerBody.SM_DragonLowerBody'),'bodyInstance':{'collisionEnabled':'NoCollision','collisionProfileName':'NoCollision'}})})
   await c(assets,'save_assets',{'asset_paths':['/Game/Level/Stage2_ShadowBody_Prototype',folder+'/'+name]})
asyncio.run(main())
