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
   sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';asset='editor_toolset.toolsets.asset.AssetTools';ref=lambda p:{'refPath':p}
   master='/Game/Level/Stage3_Integrated';bloom='/Game/Stage3Integrated/Sections/L_Bloom';res='/Game/Stage3Integrated/Sections/L_Resolution'
   for src,dst in [('/Game/Level/Stage3_puzzle1',master),('/Game/Level/Stage3_puzzle',bloom),('/Game/Level/Stage3_puzzle3',res)]:
    print('COPY',dst,await c(asset,'duplicate',{'path':src,'new_path':dst}),flush=True)
   await c(asset,'save_assets',{'asset_paths':[master,bloom,res]})
   for path in [bloom,res]:
    await c(sc,'load_level',{'level_path':path});ws=(await c(sc,'find_actors',{'name':'WorldSettings','tag':'','collision_channels':[]}))[0];assert path+'.' in ws['refPath'],ws
    actors=await c(sc,'find_actors',{'name':'','tag':'','collision_channels':[]})
    for a in actors:
     n=a['refPath'].split('.')[-1]
     if n in ['DirectionalLight_0','SkyAtmosphere_0','SkyLight_0','ExponentialHeightFog_0','VolumetricCloud_0','PlayerStart_0','StaticMeshActor_0','Floor_0']:
      print('REMOVE',path,n,await c(sc,'remove_from_scene',{'actor':a}),flush=True)
    if path==bloom:
     ctrl=(await c(sc,'find_actors',{'name':'Bloom_Controller','tag':'','collision_channels':[]}))[0]
     print('BLOOM',await c(ob,'set_properties',{'instance':ctrl,'values':json.dumps({'bRestrictToArea':True,'areaMinOffsetX':-2200.0,'areaMaxOffsetX':500.0})}),flush=True)
    await c(asset,'save_assets',{'asset_paths':[path]})
   await c(sc,'load_level',{'level_path':master});ws=(await c(sc,'find_actors',{'name':'WorldSettings','tag':'','collision_channels':[]}))[0];assert master+'.' in ws['refPath']
   await c(ob,'set_properties',{'instance':ws,'values':json.dumps({'defaultGameMode':ref('/Script/MegaJam.DirectorCutTestMode')})})
   actors=await c(sc,'find_actors',{'name':'','tag':'','collision_channels':[]})
   for a in actors:
    if a['refPath'].endswith('.Floor_0'):print('REMOVE MASTER FLOOR',await c(sc,'remove_from_scene',{'actor':a}),flush=True)
   for level,name,x in [(bloom,'Stage3_Bloom',1900),(res,'Stage3_Resolution',5150)]:
    a=await c(sc,'create_level_instance',{'level_path':level,'name':name,'xform':{'location':{'x':x,'y':0,'z':0}}});print('INSTANCE',name,a,flush=True)
   await c(sc,'add_to_scene_from_asset',{'asset_path':'/Game/DirectorCut/Transitions/BP_StageFadeIn.BP_StageFadeIn','name':'Stage3_EntryFade','xform':{'location':{'x':0,'y':0,'z':0}}})
   print('SAVE',await c(asset,'save_assets',{'asset_paths':[master]}),flush=True)
asyncio.run(main())
