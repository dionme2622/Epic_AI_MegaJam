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
   obj='editor_toolset.toolsets.object.ObjectTools';act='editor_toolset.toolsets.actor.ActorTools';p='/Game/Level/UEDPIE_0_Stage2_BloomSign_Prototype.Stage2_BloomSign_Prototype:PersistentLevel.'
   await c(act,'set_actor_transform',{'actor':{'refPath':p+'BP_Dragon_C_0'},'xform':{'location':{'x':350,'y':0,'z':92},'rotation':{'pitch':0,'yaw':0,'roll':0},'scale':{'x':1,'y':1,'z':1}}})
   for i in range(3):
    await c(obj,'set_properties',{'instance':{'refPath':p+f'BP_BloomSign_C_{i}.Symbol'},'values':json.dumps({'relativeScale3D':{'x':.45,'y':1,'z':.45}})})
   pp={'refPath':p+'PostProcessVolume_0'}
   for intensity in [0,30,60,100]:
    await c(obj,'set_properties',{'instance':pp,'values':json.dumps({'settings':{'bloomIntensity':intensity}})})
    await asyncio.sleep(.6)
    img=await c('EditorToolset.EditorAppToolset','CaptureEditorImage',{})
    Path(f'output/BloomPuzzle/glare_{intensity}.png').write_bytes(base64.b64decode(img['data']))
    print('CAPTURE',intensity,flush=True)
asyncio.run(main())
