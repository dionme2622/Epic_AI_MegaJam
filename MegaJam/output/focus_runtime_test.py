import asyncio,json,re
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError: raise RuntimeError(str(z.content))
    return json.loads(z.content[0].text).get('returnValue')
   sl='SlateInspectorToolset.SlateInspectorToolset'; obj='editor_toolset.toolsets.object.ObjectTools'
   snap=await c(sl,'Snapshot',{'ref':'','maxDepth':3});ref=re.search(r'\[ref=(w\d+)\]',snap).group(1)
   await c(sl,'Observe',{'ref':ref,'maxDepth':30});await asyncio.sleep(.7);await c(sl,'Snapshot',{'ref':ref,'maxDepth':30});print('CLICK',await c(sl,'Click',{'ref':'sp5'}),flush=True)
   p='/Game/Level/UEDPIE_0_Stage2_FocusProp_Prototype.Stage2_FocusProp_Prototype:PersistentLevel.'; puzzle={'refPath':p+'BP_FocusPropPuzzle_C_0'}
   async def props(a,n):return json.loads(await c(obj,'get_properties',{'instance':a,'properties':n}))
   async def key(k):await c(sl,'PressKey',{'key':k});await asyncio.sleep(.3)
   print('INIT',await props(puzzle,['bActive','bNearSelected','bSolved','exitDoor']),flush=True)
   await key('E');print('ENTER',await props(puzzle,['bActive','bNearSelected','bSolved']),flush=True)
   cam={'refPath':p+'BP_FocusPropPuzzle_C_0.PuzzleCamera'}
   print('CAM_NEAR',await props(cam,['postProcessSettings']),flush=True)
   await key('Q'); print('TOGGLE',await props(puzzle,['bActive','bNearSelected']),flush=True)
   print('CAM_FAR',await props(cam,['postProcessSettings']),flush=True)
   near={'refPath':p+'BP_FocusPropPuzzle_C_0.NearPiece'};far={'refPath':p+'BP_FocusPropPuzzle_C_0.FarPiece'}
   for a,x,y in [(near,450,200),(far,500,-200)]:
    await c(obj,'set_properties',{'instance':a,'values':json.dumps({'relativeLocation':{'x':x,'y':y,'z':300}})})
   await key('R'); print('RESET',await props(near,['relativeLocation']),await props(far,['relativeLocation']),flush=True)
   for a,x,y in [(near,450,200),(far,500,-200)]:
    await c(obj,'set_properties',{'instance':a,'values':json.dumps({'relativeLocation':{'x':x,'y':y,'z':300}})})
   await key('Enter');current=await props(cam,['postProcessSettings']);print('SUCCESS_DOF',current['postProcessSettings']['depthOfFieldEnabled'],current['postProcessSettings']['depthOfFieldScale'],flush=True)
   await asyncio.sleep(2);print('COMPLETE',await props(puzzle,['bActive','bSolved']),await props({'refPath':p+'BP_S2_Door_C_1'},['bOpen']),flush=True)
asyncio.run(main())
