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
   sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools';assets='editor_toolset.toolsets.asset.AssetTools';ref=lambda p:{'refPath':p}
   master='/Game/DirectorCut/Stage/Stage4';section='/Game/Stage4Integrated/L_ShadowStage'
   for source,target in [('/Game/Level/Stage4_puzzle0',master),('/Game/Level/Stage4_puzzle1',section)]:
    if not await c(assets,'duplicate',{'path':source,'new_path':target}):raise RuntimeError('Could not duplicate '+source)
    print('COPIED',target,flush=True)
   await c(assets,'save_assets',{'asset_paths':[master,section]})
   await c(sc,'load_level',{'level_path':section});ws=(await c(sc,'find_actors',{'name':'WorldSettings','tag':'','collision_channels':[]}))[0];assert section+'.' in ws['refPath']
   actors=await c(sc,'find_actors',{'name':'','tag':'','collision_channels':[]})
   for a in actors:
    n=a['refPath'].split('.')[-1]
    if n in ['DirectionalLight_0','SkyAtmosphere_0','SkyLight_0','ExponentialHeightFog_0','VolumetricCloud_0','PlayerStart_0','StaticMeshActor_0']:
     print('TRIM',n,await c(sc,'remove_from_scene',{'actor':a}),flush=True)
   pp=await c(sc,'add_to_scene_from_class',{'actor_type':ref('/Script/Engine.PostProcessVolume'),'name':'FinalShadow_ColorGrade','xform':{'location':{'x':1200,'y':0,'z':300},'scale':{'x':14,'y':12,'z':7}}})
   values={'bUnbound':False,'blendRadius':0.0,'settings':{'bOverride_ColorGainShadows':True,'colorGainShadows':{'x':.18,'y':.18,'z':.18,'w':1},'bOverride_ColorCorrectionShadowsMax':True,'colorCorrectionShadowsMax':.35,'bOverride_IndirectLightingIntensity':True,'indirectLightingIntensity':0.0}}
   await c(ob,'set_properties',{'instance':pp,'values':json.dumps(values)});print('GRADE',pp,await c(ac,'get_actor_bounds',{'actor':pp}),flush=True)
   await c(assets,'save_assets',{'asset_paths':[section]})
   await c(sc,'load_level',{'level_path':master});ws=(await c(sc,'find_actors',{'name':'WorldSettings','tag':'','collision_channels':[]}))[0];assert master+'.' in ws['refPath']
   await c(ob,'set_properties',{'instance':ws,'values':json.dumps({'defaultGameMode':ref('/Script/MegaJam.DirectorCutTestMode')})})
   inst=await c(sc,'create_level_instance',{'level_path':section,'name':'Stage4_ShadowStage','xform':{'location':{'x':1670,'y':0,'z':0}}});print('INSTANCE',inst,flush=True)
   await c(assets,'save_assets',{'asset_paths':[master]});print('SAVED',flush=True)
asyncio.run(main())
