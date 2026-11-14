import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   p='/Game/Level/UEDPIE_0_Stage2_FocusProp_Prototype.Stage2_FocusProp_Prototype:PersistentLevel.BP_FocusPropPuzzle_C_0.PuzzleCamera'
   settings={'bOverride_DepthOfFieldEnabled':True,'depthOfFieldEnabled':True,'bOverride_DepthOfFieldScale':True,'depthOfFieldScale':3.0,'bOverride_DepthOfFieldFstop':True,'depthOfFieldFstop':0.1,'bOverride_DepthOfFieldMinFstop':True,'depthOfFieldMinFstop':0.1,'bOverride_DepthOfFieldFocalDistance':True,'depthOfFieldFocalDistance':1300.0,'bOverride_DepthOfFieldSensorWidth':True,'depthOfFieldSensorWidth':70.0,'bOverride_DepthOfFieldNearTransitionRegion':True,'depthOfFieldNearTransitionRegion':20.0,'bOverride_DepthOfFieldFarTransitionRegion':True,'depthOfFieldFarTransitionRegion':20.0}
   z=await s.call_tool('call_tool',{'toolset_name':'editor_toolset.toolsets.object.ObjectTools','tool_name':'set_properties','arguments':{'instance':{'refPath':p},'values':json.dumps({'postProcessSettings':settings})}});print(z.content[0].text)
asyncio.run(main())
