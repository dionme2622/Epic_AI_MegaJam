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
   obj='editor_toolset.toolsets.object.ObjectTools';act='editor_toolset.toolsets.actor.ActorTools';p='/Game/Level/UEDPIE_0_Stage2_BloomSign_Prototype.Stage2_BloomSign_Prototype:PersistentLevel.';pp={'refPath':p+'PostProcessVolume_0'}
   for name,x in [('moon',900),('sun',1450)]:
    await c(act,'set_actor_transform',{'actor':{'refPath':p+'BP_Dragon_C_0'},'xform':{'location':{'x':x,'y':0,'z':92},'rotation':{'pitch':0,'yaw':0,'roll':0},'scale':{'x':1,'y':1,'z':1}}})
    await asyncio.sleep(.4)
    for intensity in [0,70]:
     await c(obj,'set_properties',{'instance':pp,'values':json.dumps({'settings':{'bloomIntensity':intensity}})});await asyncio.sleep(.4)
     img=await c('EditorToolset.EditorAppToolset','CaptureEditorImage',{});Path(f'output/BloomPuzzle/compare_{name}_{intensity}.png').write_bytes(base64.b64decode(img['data']));print(name,intensity,flush=True)
asyncio.run(main())
