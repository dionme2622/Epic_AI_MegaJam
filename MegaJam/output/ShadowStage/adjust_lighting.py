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
    if z.isError:raise RuntimeError(f'{n}: {z.content}')
    return json.loads(z.content[0].text).get('returnValue')
   sc='editor_toolset.toolsets.scene.SceneTools';app='EditorToolset.EditorAppToolset';sl='SlateInspectorToolset.SlateInspectorToolset';ac='editor_toolset.toolsets.actor.ActorTools';assets='editor_toolset.toolsets.asset.AssetTools'
   assert not await c(app,'IsPIERunning',{}),'PIE is running'
   await c(sc,'load_level',{'level_path':'/Game/Level/Stage2_ShadowBody_Prototype'})
   ws=(await c(sc,'find_actors',{'name':'WorldSettings','tag':'','collision_channels':[]}))[0];assert '/Game/Level/Stage2_ShadowBody_Prototype.' in ws['refPath']
   print('BACKUP',await c(assets,'duplicate',{'path':'/Game/Level/Stage2_ShadowBody_Prototype','new_path':'/Game/ShadowBodyStage/Backups/ShadowStage_BeforeLighting'}),flush=True)
   await c(assets,'save_assets',{'asset_paths':['/Game/ShadowBodyStage/Backups/ShadowStage_BeforeLighting']})
   light=(await c(sc,'find_actors',{'name':'DirectionalLight','tag':'','collision_channels':[]}))[0]
   await c(ac,'set_actor_transform',{'actor':light,'xform':{'rotation':{'pitch':-90,'yaw':0,'roll':0}}})
   rigs=await c(sc,'find_actors',{'name':'Overhead_Rig_','tag':'','collision_channels':[]});print('RIGS',len(rigs),flush=True)
   for a in rigs:
    assert '/Game/Level/Stage2_ShadowBody_Prototype.' in a['refPath']
    await c(ac,'set_actor_transform',{'actor':a,'xform':{'scale':{'x':2.85,'y':6.5,'z':.65}}})
   await c(assets,'save_assets',{'asset_paths':['/Game/Level/Stage2_ShadowBody_Prototype']})
   await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   pawn=next(x for x in await c(sc,'find_actors',{'name':'Dragon','tag':'','collision_channels':[]}) if 'DirectorCutDragon' in x['refPath'])
   await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':270,'y':0,'z':60}}});await asyncio.sleep(2)
   async def shot(n):
    z=await c(app,'CaptureEditorImage',{});Path('output/ShadowStage/'+n+'.png').write_bytes(base64.b64decode(z['data']))
   await shot('adjusted_on')
   await c(sl,'Observe',{'ref':'w1','maxDepth':100});snap=await c(sl,'Snapshot',{'ref':'w1','maxDepth':100});gear=re.search(r'button "⚙".*?\[ref=(b\d+)\]',snap).group(1)
   await c(sl,'Click',{'ref':gear});await c(sl,'PressKey',{'key':'Enter'});await asyncio.sleep(.5)
   snap=await c(sl,'Snapshot',{'ref':'w1','maxDepth':100});after=snap[snap.index('text "그림자"'):];low=re.search(r'button "낮음".*?\[ref=(b\d+)\]',after).group(1);close=re.search(r'button "닫기".*?\[ref=(b\d+)\]',after).group(1)
   await c(sl,'Click',{'ref':low});await c(sl,'PressKey',{'key':'Enter'});await asyncio.sleep(.5);await c(sl,'Click',{'ref':close});await c(sl,'PressKey',{'key':'Enter'});await asyncio.sleep(1);await shot('adjusted_off')
   await c(app,'StopPIE',{});print('SAVED_AND_TESTED',flush=True)
asyncio.run(main())
