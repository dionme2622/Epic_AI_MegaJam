import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   p='/Game/Level/UEDPIE_0_Stage2_FocusProp_Prototype.Stage2_FocusProp_Prototype:PersistentLevel.BP_FocusPropPuzzle_C_0.'
   for name,x,y in [('NearPiece',450,200),('FarPiece',500,-200)]:
    z=await s.call_tool('call_tool',{'toolset_name':'editor_toolset.toolsets.object.ObjectTools','tool_name':'set_properties','arguments':{'instance':{'refPath':p+name},'values':json.dumps({'relativeLocation':{'x':x,'y':y,'z':300}})}})
    print(z.content[0].text)
asyncio.run(main())
