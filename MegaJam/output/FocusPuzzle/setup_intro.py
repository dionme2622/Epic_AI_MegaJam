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
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:550],flush=True);return v
   ref=lambda x:{'refPath':x};sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';bp='editor_toolset.toolsets.blueprint.BlueprintTools';act='editor_toolset.toolsets.actor.ActorTools';asset='editor_toolset.toolsets.asset.AssetTools'
   blueprint='/Game/FocusPropPrototype/BP_FocusIntro.BP_FocusIntro'
   await c(bp,'compile_blueprint',{'blueprint':ref(blueprint)})
   camera=await c(sc,'add_to_scene_from_class',{'actor_type':ref('/Script/Engine.CameraActor'),'name':'FocusIntro_KeyCamera','xform':{'location':{'x':475,'y':1050,'z':405},'rotation':{'pitch':-6,'yaw':-90,'roll':0}}})
   await c(act,'get_components',{'actor':camera})
   controller=await c(sc,'find_actors',{'name':'Focus_Controller','tag':'','collision_channels':[]})
   if len(controller)!=1:
    controller=await c(sc,'find_actors',{'name':'FocusPropPuzzle','tag':'','collision_channels':[]})
   if len(controller)!=1:raise RuntimeError('Could not identify exactly one focus puzzle')
   intro=await c(sc,'add_to_scene_from_asset',{'asset_path':blueprint,'name':'FocusIntro_Director','xform':{'location':{'x':0,'y':0,'z':0}}})
   await c(ob,'set_properties',{'instance':intro,'values':json.dumps({'ShotCamera':camera,'PuzzleController':controller[0]})})
   await c(ob,'get_properties',{'instance':intro,'properties':['ShotCamera','PuzzleController']})
   await c(asset,'save_assets',{'asset_paths':['/Game/FocusPropPrototype/BP_FocusIntro','/Game/Level/Stage2_FocusProp_Prototype']})
asyncio.run(main())
