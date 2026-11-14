import asyncio,json,base64,re
from pathlib import Path
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
   sl='SlateInspectorToolset.SlateInspectorToolset';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools';app='EditorToolset.EditorAppToolset'
   p='/Game/Level/UEDPIE_0_Stage2_ResolutionCorridor_Prototype.Stage2_ResolutionCorridor_Prototype:PersistentLevel.'
   ref=lambda n:{'refPath':p+n};pawn=ref('DirectorCutDragon_0');ctrl=ref('BP_ResolutionCorridor_C_0');door=ref('BP_S2_Door_C_0')
   async def props(a,n):return json.loads(await c(ob,'get_properties',{'instance':a,'properties':n}))
   async def image(name):
    z=await c(app,'CaptureEditorImage',{});Path('output/ResolutionCorridor/'+name+'.png').write_bytes(base64.b64decode(z['data']))
   async def move(x,z=85):
    await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':x,'y':0,'z':z}}});await asyncio.sleep(.8)
   await c(sl,'Observe',{'ref':'w1','maxDepth':100});snap=await c(sl,'Snapshot',{'ref':'sp6','maxDepth':100})
   if 'text "해상도"' not in snap:raise RuntimeError('Settings menu is not open')
   for i in [10,11,12]: assert (await props(ref('StaticMeshActor_'+str(i)),['bHidden']))['bHidden']
   await c(sl,'Click',{'ref':'b61'});await asyncio.sleep(.5)
   for i in [10,11,12]: assert not (await props(ref('StaticMeshActor_'+str(i)),['bHidden']))['bHidden']
   print('LOW_ARROWS_VISIBLE',flush=True)
   await c(sl,'Click',{'ref':'b65'});await move(280);await image('low')
   await move(400);s1=await props(ctrl,['progress','bFailing','bCompleted']);print('SAFE1',s1,flush=True);assert s1['progress']==1 and not s1['bFailing']
   await move(560);await asyncio.sleep(.5);failure=await props(ctrl,['progress','bFailing']);print('FAILURE',failure,flush=True)
   await asyncio.sleep(1.5);reset=await props(ctrl,['progress','bFailing']);print('RESET',reset,await c(ac,'get_actor_transform',{'actor':pawn}),flush=True);assert reset['progress']==0 and not reset['bFailing']
   for x in [400,720,1040]:
    await move(x);print('SAFE',x,await props(ctrl,['progress','bCompleted']),flush=True)
   done=await props(ctrl,['progress','bCompleted']);print('DONE',done,await props(door,['bOpen']),flush=True);assert done['bCompleted'] and (await props(door,['bOpen']))['bOpen']
   await c(app,'StopPIE',{})
asyncio.run(main())
