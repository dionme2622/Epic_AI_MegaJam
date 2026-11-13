import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError: raise RuntimeError(f'{n}: {z.content}')
    val=json.loads(z.content[0].text).get('returnValue'); print(n,str(val)[:250],flush=True); return val
   scene='editor_toolset.toolsets.scene.SceneTools'; obj='editor_toolset.toolsets.object.ObjectTools'
   async def add(name,asset,x,y,z,sx=1,sy=1,sz=1):
    return await c(scene,'add_to_scene_from_asset',{'asset_path':asset,'name':name,'xform':{'location':{'x':x,'y':y,'z':z},'scale':{'x':sx,'y':sy,'z':sz}}})
   async def props(ref,values): await c(obj,'set_properties',{'instance':ref,'values':json.dumps(values)})
   cube='/Engine/BasicShapes/Cube.Cube'; sphere='/Engine/BasicShapes/Sphere.Sphere'
   if False:
    pass
   # Build has already placed the geometry; continue with references below.
   '''
   await add('S2_TestFloor',cube,1700,0,-50,40,5,1)
   await add('S2_BackWall',cube,1700,-300,250,40,.2,6)
   await add('S2_ShadowWall',cube,500,-180,200,8,.1,4)
   a=await add('S2_ShadowPiece_A',cube,300,-70,100,1,.3,2)
   b=await add('S2_ShadowPiece_B',cube,700,-70,100,1,.3,2)
   for p in [a,b]: await props({'refPath':p['refPath']+'.StaticMeshComponent0'},{'mobility':'Movable'})
   for x in [500,900]: await add('S2_ShadowTarget',cube,x,0,4,1.1,1,.08)
   for i,x in enumerate([1550,1700,1850]): await add('S2_Symbol_'+str(i+1),[cube,sphere,cube][i],x,-100,120,.7,.7,.7)
   for i,x in enumerate([2600,2750,2900]): await add('S2_Film_'+str(i+1),cube,x,-100,120,.9,.2,1.4)
   await add('S2_Console',cube,3250,-70,60,1,1,1.2)
   pp=await c(scene,'add_to_scene_from_class',{'actor_type':{'refPath':'/Script/Engine.PostProcessVolume'},'name':'S2_PostProcess','xform':{'location':{'x':0,'y':0,'z':0}}})
   await props(pp,{'bUnbound':True})
   light=await c(scene,'add_to_scene_from_class',{'actor_type':{'refPath':'/Script/Engine.PointLight'},'name':'S2_PuzzleLight','xform':{'location':{'x':500,'y':200,'z':400}}})
   '''
   prefix='/Game/Level/Stage2.Stage2:PersistentLevel.'
   a={'refPath':prefix+'StaticMeshActor_4'}; b={'refPath':prefix+'StaticMeshActor_5'}
   pp={'refPath':prefix+'PostProcessVolume_0'}; light={'refPath':prefix+'PointLight_0'}
   comp={'refPath':light['refPath']+'.LightComponent0'}
   await props(comp,{'mobility':'Movable','intensity':15000.0,'attenuationRadius':1800.0})
   controller=await c(scene,'add_to_scene_from_asset',{'asset_path':'/Game/Stage2Prototype/BP_Stage2Prototype.BP_Stage2Prototype','name':'S2_PuzzleController','xform':{'location':{'x':0,'y':0,'z':0}}})
   await props(controller,{'postProcessVolume':pp,'puzzleLights':[light],'shadowPieceA':a,'shadowPieceB':b,'shadowTargetA':{'x':500,'y':-70,'z':100},'shadowTargetB':{'x':900,'y':-70,'z':100},'shadowTolerance':30.0})
   player=await c(scene,'add_to_scene_from_asset',{'asset_path':'/Game/Stage1Generated/BP_Stage1Dragon.BP_Stage1Dragon','name':'S2_Dragon','xform':{'location':{'x':0,'y':0,'z':100}}})
   await props(player,{'autoPossessPlayer':'Player0','bUseControllerRotationYaw':False})
   camera=await c(scene,'add_to_scene_from_class',{'actor_type':{'refPath':'/Script/Engine.CameraActor'},'name':'S2_Camera','xform':{'location':{'x':0,'y':650,'z':300},'rotation':{'pitch':-4,'yaw':-90,'roll':0}}})
   await props(camera,{'tags':['Stage1Camera']})
   await c('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':['/Game/Level/Stage2','/Game/Stage2Prototype/BP_Stage2Prototype']})
asyncio.run(main())
