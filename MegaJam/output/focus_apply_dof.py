import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError: raise RuntimeError(str(z.content))
    print(z.content[0].text[:250],flush=True)
   settings={'bOverride_DepthOfFieldEnabled':True,'depthOfFieldEnabled':True,'bOverride_DepthOfFieldScale':True,'depthOfFieldScale':3.0,'bOverride_DepthOfFieldFstop':True,'depthOfFieldFstop':0.1,'bOverride_DepthOfFieldMinFstop':True,'depthOfFieldMinFstop':0.1,'bOverride_DepthOfFieldFocalDistance':True,'depthOfFieldFocalDistance':1300.0,'bOverride_DepthOfFieldSensorWidth':True,'depthOfFieldSensorWidth':70.0,'bOverride_DepthOfFieldNearTransitionRegion':True,'depthOfFieldNearTransitionRegion':20.0,'bOverride_DepthOfFieldFarTransitionRegion':True,'depthOfFieldFarTransitionRegion':20.0}
   paths=['/Game/FocusPropPrototype/BP_FocusPropPuzzle.Default__BP_FocusPropPuzzle_C:PuzzleCamera','/Game/Level/Stage2_FocusProp_Prototype.Stage2_FocusProp_Prototype:PersistentLevel.BP_FocusPropPuzzle_C_0.PuzzleCamera']
   for path in paths: await c('editor_toolset.toolsets.object.ObjectTools','set_properties',{'instance':{'refPath':path},'values':json.dumps({'postProcessSettings':settings})})
   await c('editor_toolset.toolsets.blueprint.BlueprintTools','compile_blueprint',{'blueprint':{'refPath':'/Game/FocusPropPrototype/BP_FocusPropPuzzle.BP_FocusPropPuzzle'}})
   await c('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':['/Game/FocusPropPrototype/BP_FocusPropPuzzle','/Game/Level/Stage2_FocusProp_Prototype']})
asyncio.run(main())
