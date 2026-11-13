import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (rd,wr,_):
  async with ClientSession(rd,wr) as s:
   await s.initialize()
   async def c(t,n,a):
    r=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if r.isError: raise RuntimeError(str(r.content))
    return json.loads(r.content[0].text).get('returnValue')
   p='/Game/Level/UEDPIE_0_Stage1.Stage1:PersistentLevel.'; actor={'refPath':p+'BP_Stage1Dragon_C_0'}; ctrl={'refPath':p+'BP_Stage1Director_C_0'}
   async def setpos(x,z):
    await c('editor_toolset.toolsets.actor.ActorTools','set_actor_transform',{'actor':actor,'xform':{'location':{'x':x,'y':0,'z':z}}}); await asyncio.sleep(1)
   async def press(): await c('SlateInspectorToolset.SlateInspectorToolset','PressKey',{'key':'E'})
   async def show(label): print(label,await c('editor_toolset.toolsets.actor.ActorTools','get_actor_transform',{'actor':actor}),await c('editor_toolset.toolsets.object.ObjectTools','get_properties',{'instance':ctrl,'properties':['LiftAlpha','LiftActive']}),flush=True)
   await setpos(8700,380); await press(); await asyncio.sleep(5); await show('DOWN')
   await setpos(8830,150); await show('EDGE_BEFORE'); await press(); await asyncio.sleep(5); await show('EDGE_AFTER')
asyncio.run(main())
