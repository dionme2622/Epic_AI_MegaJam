import asyncio,json,base64
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a});
    if z.isError:raise RuntimeError(str(z.content))
    return json.loads(z.content[0].text).get('returnValue')
   sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';ac='editor_toolset.toolsets.actor.ActorTools';app='EditorToolset.EditorAppToolset';sl='SlateInspectorToolset.SlateInspectorToolset'
   await c(sc,'load_level',{'level_path':'/Game/Level/Stage2_ShadowBody_Prototype'})
   l=(await c(sc,'find_actors',{'name':'DirectionalLight','tag':'','collision_channels':[]}))[0];print('LIGHT',await c(ac,'get_actor_transform',{'actor':l}),flush=True)
   comp=(await c(ac,'get_components',{'actor':l}))[0];print('LIGHTPROPS',await c(ob,'get_properties',{'instance':comp,'properties':['intensity','castShadows','mobility']}),flush=True)
   print('PLAYRUN',await c(app,'IsPIERunning',{}),flush=True)
   await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':2}})
   pawn=(await c(sc,'find_actors',{'name':'Dragon','tag':'','collision_channels':[]}))[0];print('PAWN',pawn,flush=True)
   await c(ac,'set_actor_transform',{'actor':pawn,'xform':{'location':{'x':300,'y':0,'z':80}}});await asyncio.sleep(2)
   img=await c(app,'CaptureEditorImage',{});Path('output/ShadowStage/shadow_on.png').write_bytes(base64.b64decode(img['data']))
   await c(sl,'Observe',{'ref':'w1','maxDepth':30});snap=await c(sl,'Snapshot',{'ref':'w1','maxDepth':12});print('SPLITTERS','\n'.join([x for x in snap.splitlines() if 'splitter' in x]),flush=True)
   await c(sl,'Click',{'ref':'sp6'});await c(sl,'PressKey',{'key':'Escape'});await asyncio.sleep(1)
   snap=await c(sl,'Snapshot',{'ref':'sp6','maxDepth':100});print('SETTINGS',snap[-5000:],flush=True)
asyncio.run(main())
