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
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:300],flush=True);return v
   folder='/Game/ResolutionCorridor/DotMarkers';dest='/Game/Level/Stage2_ResolutionCorridor_Prototype'
   tex='editor_toolset.toolsets.texture.TextureTools';mat='editor_toolset.toolsets.material.MaterialTools';ob='editor_toolset.toolsets.object.ObjectTools';sc='editor_toolset.toolsets.scene.SceneTools';ac='editor_toolset.toolsets.actor.ActorTools';assets='editor_toolset.toolsets.asset.AssetTools'
   ref=lambda p:{'refPath':p}
   async def props(o,v):return await c(ob,'set_properties',{'instance':o,'values':json.dumps(v)})
   materials={}
   for kind in ['Neutral','Safe']:
    texture=(await c(tex,'import_file',{'folder_path':folder,'asset_name':'T_Dots_'+kind,'source_file':'C:/LHH/Epic_AI_MegaJam/MegaJam/output/ResolutionCorridor/DotMarkers/Dots_'+kind+'.png'}))[0]
    m=await c(mat,'create_material',{'folder_path':folder,'asset_name':'M_Dots_'+kind});materials[kind]=m
    e=await c(mat,'add_expression',{'material_or_function':m,'expression_class':ref('/Script/Engine.MaterialExpressionTextureSample'),'x':-400,'y':0})
    await props(e,{'texture':texture})
    await c(mat,'connect_to_output',{'expression':e,'output_name':'RGB','material_property':'MP_EmissiveColor'})
    await c(mat,'connect_to_output',{'expression':e,'output_name':'A','material_property':'MP_OpacityMask'})
    await props(m,{'shadingModel':'MSM_Unlit','blendMode':'BLEND_Masked','twoSided':True})
    await c(mat,'recompile',{'material_or_function':m})
   guides=await c(sc,'find_actors',{'name':'Resolution_Guide','tag':'','collision_channels':[]})
   tiles=await c(sc,'find_actors',{'name':'Resolution_Tile','tag':'','collision_channels':[]})
   if len(guides)!=3 or len(tiles)!=5:raise RuntimeError('Unexpected corridor actors')
   values=[]
   for tile in tiles:
    pos=await c(ac,'get_actor_transform',{'actor':tile})
    info=json.loads(await c(ob,'get_properties',{'instance':tile,'properties':['bSafe','safeOrder']}))
    values.append((pos['location']['x'],info['bSafe'],info['safeOrder']))
   values.sort()
   if [(b,n) for _,b,n in values if b]!=[(True,0),(True,1),(True,2)]:raise RuntimeError('Unexpected safe order')
   cube=ref('/Engine/BasicShapes/Cube.Cube')
   for g in guides:
    t=await c(ac,'get_actor_transform',{'actor':g});t['location']['y']=-220;t['scale']={'x':1.35,'y':.025,'z':1.35}
    await c(ac,'set_actor_transform',{'actor':g,'xform':t})
    await props(ref(g['refPath']+'.StaticMeshComponent0'),{'staticMesh':cube,'overrideMaterials':[materials['Safe']],'castShadow':False,'bodyInstance':{'collisionEnabled':'NoCollision','collisionProfileName':'NoCollision'}})
   for idx,(x,_,_) in enumerate(values,1):
    a=await c(sc,'add_to_scene_from_asset',{'asset_path':'/Engine/BasicShapes/Cube.Cube','name':'Resolution_DotPattern_'+str(idx),'xform':{'location':{'x':x,'y':-230,'z':160},'scale':{'x':1.35,'y':.025,'z':1.35}}})
    await props(ref(a['refPath']+'.StaticMeshComponent0'),{'overrideMaterials':[materials['Neutral']],'castShadow':False,'bodyInstance':{'collisionEnabled':'NoCollision','collisionProfileName':'NoCollision'}})
   await c(assets,'save_assets',{'asset_paths':[dest]+[folder+'/'+prefix+'_'+kind for kind in ['Neutral','Safe'] for prefix in ['T_Dots','M_Dots']]})
asyncio.run(main())
