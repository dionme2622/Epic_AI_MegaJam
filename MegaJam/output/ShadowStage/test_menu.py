import asyncio,json,base64
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
   sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools';app='EditorToolset.EditorAppToolset';sl='SlateInspectorToolset.SlateInspectorToolset'
   if await c(app,'IsPIERunning',{}):await c(app,'StopPIE',{})
   await c(sc,'load_level',{'level_path':'/Game/Level/Stage2_ShadowBody_Prototype'})
   await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   a=await c(sc,'find_actors',{'name':'Dragon','tag':'','collision_channels':[]});pawn=next(x for x in a if 'DirectorCutDragon' in x['refPath']);print('PAWN',pawn,flush=True)
   await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':270,'y':0,'z':65}}});await asyncio.sleep(1)
   z=await c(app,'CaptureEditorImage',{});Path('output/ShadowStage/on.png').write_bytes(base64.b64decode(z['data']))
   await c(sl,'Observe',{'ref':'w1','maxDepth':35});snap=await c(sl,'Snapshot',{'ref':'w1','maxDepth':35});print('UI','\n'.join(x for x in snap.splitlines() if 'button' in x and ('⚙' in x or '설정' in x)),flush=True)
   await c(sl,'Click',{'ref':'sp6'});await c(sl,'PressKey',{'key':'Escape'});await asyncio.sleep(.8)
   snap=await c(sl,'Snapshot',{'ref':'sp6','maxDepth':100});print('MENU',snap[-8500:],flush=True)
asyncio.run(main())
