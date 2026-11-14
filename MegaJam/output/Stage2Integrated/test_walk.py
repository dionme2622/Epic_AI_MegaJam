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
   app='EditorToolset.EditorAppToolset';bp='editor_toolset.toolsets.blueprint.BlueprintTools';sc='editor_toolset.toolsets.scene.SceneTools';ac='editor_toolset.toolsets.actor.ActorTools';ob='editor_toolset.toolsets.object.ObjectTools';ref=lambda p:{'refPath':p}
   name='BP_TempStage1WalkQA';path='/Game/Stage2Integrated/'+name+'.'+name
   b=await c(bp,'create',{'folder_path':'/Game/Stage2Integrated','asset_name':name,'asset_type':ref('/Script/Engine.Actor')})
   await c(bp,'write_graph_dsl',{'graph':ref(path+':EventGraph'),'code':'(event EventTick (Pawn|Input|AddMovementInput :self (Game|GetPlayerPawn :PlayerIndex 0) :WorldDirection (Math|Vector|MakeVector :X 1.0 :Y 0.0 :Z 0.0) :ScaleValue 1.0))'})
   await c(bp,'compile_blueprint',{'blueprint':b})
   qa=await c(sc,'add_to_scene_from_asset',{'asset_path':path,'name':'TemporaryWalkQA','xform':{'location':{'x':0,'y':0,'z':0}}})
   await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   players=await c(sc,'find_actors',{'name':'Player','tag':'','collision_channels':[]});pawn=next(a for a in players if 'BP_Stage1Dragon' in a['refPath'])
   await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':9800,'y':0,'z':350}}})
   for i in range(50):
    dest=await c(sc,'find_actors',{'name':'Stage2_EntryFade','tag':'','collision_channels':[]})
    if dest:print('WALK_DESTINATION_OK',dest,flush=True);break
    try:print('LOCATION',await c(ac,'get_actor_transform',{'actor':pawn}),flush=True)
    except: pass
    await asyncio.sleep(.15)
   else:print('WALK_FAILED',flush=True)
   await c(app,'StopPIE',{})
   print('QA',qa,flush=True)
   await c(sc,'delete_actors',{'actors':[qa]})
asyncio.run(main())
