import asyncio,json,base64
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a});return json.loads(z.content[0].text).get('returnValue')
   sc='editor_toolset.toolsets.scene.SceneTools';sl='SlateInspectorToolset.SlateInspectorToolset';ac='editor_toolset.toolsets.actor.ActorTools';app='EditorToolset.EditorAppToolset'
   for n in ['Dragon','Focus_Controller']:
    a=(await c(sc,'find_actors',{'name':n,'tag':'','collision_channels':[]}))[0];print(n,await c(ac,'get_actor_transform',{'actor':a}),flush=True)
   await c(sl,'Observe',{'ref':'w1','maxDepth':25});print(await c(sl,'Snapshot',{'ref':'w1','maxDepth':8}),flush=True)
   img=await c(app,'CaptureEditorImage',{});Path('output/Stage2Integrated/focus_check.png').write_bytes(base64.b64decode(img['data']))
asyncio.run(main())
