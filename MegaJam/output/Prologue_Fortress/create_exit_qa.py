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
   ref=lambda p:{'refPath':p};bp='editor_toolset.toolsets.blueprint.BlueprintTools';sc='editor_toolset.toolsets.scene.SceneTools';asset='editor_toolset.toolsets.asset.AssetTools'
   await c('EditorToolset.EditorAppToolset','StopPIE',{})
   path='/Game/DirectorCut/Transitions/Tests/BP_TemporaryExitMoveQA'
   b=await c(bp,'create',{'folder_path':'/Game/DirectorCut/Transitions/Tests','asset_name':'BP_TemporaryExitMoveQA','asset_type':ref('/Script/Engine.Actor')})
   code='(event EventTick (Pawn|Input|AddMovementInput :self (Game|GetPlayerPawn :PlayerIndex 0) :WorldDirection (Math|Vector|MakeVector :X 1.0 :Y 0.0 :Z 0.0) :ScaleValue 1.0))'
   await c(bp,'write_graph_dsl',{'graph':ref(path+'.BP_TemporaryExitMoveQA:EventGraph'),'code':code})
   await c(bp,'compile_blueprint',{'blueprint':b})
   a=await c(sc,'add_to_scene_from_asset',{'asset_path':path+'.BP_TemporaryExitMoveQA','name':'TemporaryExitMoveQA','xform':{'location':{'x':0,'y':0,'z':0}}})
   print('QA_ACTOR',a,flush=True)
asyncio.run(main())
