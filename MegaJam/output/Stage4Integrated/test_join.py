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
   ref=lambda x:{'refPath':x};sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools';bp='editor_toolset.toolsets.blueprint.BlueprintTools';app='EditorToolset.EditorAppToolset';asset='editor_toolset.toolsets.asset.AssetTools'
   level='/Game/DirectorCut/Stage/Stage4';folder='/Game/Stage4Integrated/Tests';name='BP_TempWalkQA';path=folder+'/'+name+'.'+name
   await c(sc,'load_level',{'level_path':level});ws=(await c(sc,'find_actors',{'name':'WorldSettings','tag':'','collision_channels':[]}))[0];assert level+'.' in ws['refPath']
   b=await c(bp,'create',{'folder_path':folder,'asset_name':name,'asset_type':ref('/Script/Engine.Actor')})
   code='(event EventTick (Pawn|Input|AddMovementInput :self (Game|GetPlayerPawn :PlayerIndex 0) :WorldDirection (Math|Vector|MakeVector :X 1.0 :Y 0.0 :Z 0.0) :ScaleValue 1.0))'
   await c(bp,'write_graph_dsl',{'graph':ref(path+':EventGraph'),'code':code});await c(bp,'compile_blueprint',{'blueprint':b})
   qa=await c(sc,'add_to_scene_from_asset',{'asset_path':path,'name':'Stage4_TemporaryWalkQA','xform':{'location':{'x':0,'y':0,'z':0}}})
   try:
    await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}});pawn=next(x for x in await c(sc,'find_actors',{'name':'Dragon','tag':'','collision_channels':[]}) if 'DirectorCutDragon' in x['refPath']);await asyncio.sleep(1)
    doors=await c(sc,'find_actors',{'name':'Door','tag':'','collision_channels':[]});focusdoor=next(a for a in doors if '/Game/DirectorCut/Stage/UEDPIE_0_Stage4.' in a['refPath'])
    print('DOOR_OPEN',await c(ob,'set_properties',{'instance':focusdoor,'values':json.dumps({'bOpen':True})}),flush=True);await asyncio.sleep(2)
    for start,target in [(1050,1450)]:
     await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':start,'y':0,'z':85}}})
     for i in range(35):
      p=await c(ac,'get_actor_transform',{'actor':pawn});x=p['location']['x']
      if x>target:print('WALK_OK',start,x,flush=True);break
      await asyncio.sleep(.15)
     else:print('WALK_FAILED',start,p,flush=True);raise RuntimeError(f'Cannot cross section join at {start}')
   finally:
    if await c(app,'IsPIERunning',{}):await c(app,'StopPIE',{})
    print('REMOVE_QA',await c(sc,'remove_from_scene',{'actor':qa}),flush=True)
    await c(asset,'save_assets',{'asset_paths':[level]});print('DELETE_QA',await c(asset,'delete',{'path':folder+'/'+name}),flush=True)
asyncio.run(main())

