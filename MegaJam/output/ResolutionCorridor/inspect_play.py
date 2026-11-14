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
   app='EditorToolset.EditorAppToolset';sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';sl='SlateInspectorToolset.SlateInspectorToolset'
   if not await c(app,'IsPIERunning',{}):await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   for name in ['Dragon','Resolution_Controller','Resolution_Guide','Resolution_Tile']:
    print(name,await c(sc,'find_actors',{'name':name,'tag':'','collision_channels':[]}),flush=True)
   z=await c(app,'CaptureEditorImage',{});Path('output/ResolutionCorridor/high.png').write_bytes(base64.b64decode(z['data']))
   snap=await c(sl,'Snapshot',{'ref':'','maxDepth':3});print('WINDOW',snap,flush=True)
   await c(sl,'Observe',{'ref':'w1','maxDepth':40});snap=await c(sl,'Snapshot',{'ref':'w1','maxDepth':40})
   Path('output/ResolutionCorridor/slate_snapshot.txt').write_text(snap,encoding='utf8')
asyncio.run(main())
