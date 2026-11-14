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
   sc='editor_toolset.toolsets.scene.SceneTools';app='EditorToolset.EditorAppToolset';sl='SlateInspectorToolset.SlateInspectorToolset';ac='editor_toolset.toolsets.actor.ActorTools';ob='editor_toolset.toolsets.object.ObjectTools'
   if await c(app,'IsPIERunning',{}):await c(app,'StopPIE',{})
   await c(sc,'load_level',{'level_path':'/Game/Level/Stage2_ShadowBody_Prototype'});await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   pawn=next(x for x in await c(sc,'find_actors',{'name':'Dragon','tag':'','collision_channels':[]}) if 'DirectorCutDragon' in x['refPath'])
   await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':270,'y':0,'z':60}}});await asyncio.sleep(1)
   await c(sl,'Observe',{'ref':'w1','maxDepth':100});snap=await c(sl,'Snapshot',{'ref':'w1','maxDepth':100});gear=re.search(r'button "⚙".*?\[ref=(b\d+)\]',snap).group(1);print('GEAR',gear,flush=True);await c(sl,'Click',{'ref':gear});await asyncio.sleep(.5)
   snap=await c(sl,'Snapshot',{'ref':'w1','maxDepth':100});print('MENU','\n'.join(x for x in snap.splitlines() if 'button ' in x or 'text "그림자' in x),flush=True)
   Path('output/ShadowStage/menu.txt').write_text(snap,encoding='utf8')
   # User can choose shadow off; test using the corresponding Slate button below.
   m=re.search(r'text "그림자".*?(?=text "[^\n]*"|\Z)',snap,re.S)
   await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':530,'y':0,'z':-100}}});await asyncio.sleep(2)
   print('RESPAWN',await c(ac,'get_actor_transform',{'actor':pawn}),flush=True)
   await c(app,'StopPIE',{})
asyncio.run(main())
