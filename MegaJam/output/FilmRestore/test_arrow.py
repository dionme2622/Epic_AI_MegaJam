import asyncio,json,re,base64
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
   sl='SlateInspectorToolset.SlateInspectorToolset';ob='editor_toolset.toolsets.object.ObjectTools';snp=await c(sl,'Snapshot',{'ref':'','maxDepth':3});win=re.search(r'\[ref=(w\d+)\]',snp).group(1)
   await c(sl,'Observe',{'ref':win,'maxDepth':30});await asyncio.sleep(1);await c(sl,'Snapshot',{'ref':win,'maxDepth':30});print('CLICK',await c(sl,'Click',{'ref':'sp5'}),flush=True)
   for k in ['E','B','Two','Q']:
    await c(sl,'PressKey',{'key':k});await asyncio.sleep(.3)
   p='/Game/Level/UEDPIE_0_Stage2_FilmRestore_Prototype.Stage2_FilmRestore_Prototype:PersistentLevel.BP_FilmRestorePuzzle_C_0'
   for path,fields in [(p,['currentFilm','bShadowOn','bBloomOn']),(p+'.ClueB',['bVisible','relativeLocation','staticMesh']),(p+'.ShadowMask',['bVisible'])]:
    print(path.split('.')[-1],await c(ob,'get_properties',{'instance':{'refPath':path},'properties':fields}),flush=True)
   img=await c('EditorToolset.EditorAppToolset','CaptureEditorImage',{});Path('output/FilmRestore/arrow_check.png').write_bytes(base64.b64decode(img['data']))
asyncio.run(main())
