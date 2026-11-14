import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a});print(n,z.content,flush=True);return z
   sl='SlateInspectorToolset.SlateInspectorToolset';obj='editor_toolset.toolsets.object.ObjectTools'
   for k in ['Return','Enter','Virtual_Accept']:
    await c(sl,'PressKey',{'key':k});await asyncio.sleep(1)
    await c(obj,'get_properties',{'instance':{'refPath':'/Game/Level/UEDPIE_0_Stage2_ColorSignal_Prototype.Stage2_ColorSignal_Prototype:PersistentLevel.BP_ColorSignalPuzzle_C_0'},'properties':['bActive','bSolved','dialValues']})
asyncio.run(main())
