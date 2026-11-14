import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   p='/Game/Level/UEDPIE_0_Stage2_FilmRestore_Prototype.Stage2_FilmRestore_Prototype:PersistentLevel.BP_FilmRestorePuzzle_C_0.'
   for name in ['ClueA','ClueB','ClueC','ShadowMask','Screen']:
    z=await s.call_tool('call_tool',{'toolset_name':'editor_toolset.toolsets.object.ObjectTools','tool_name':'get_properties','arguments':{'instance':{'refPath':p+name},'properties':['relativeLocation','relativeRotation','relativeScale3D','staticMesh','overrideMaterials','bVisible','bHiddenInGame']}})
    print(name,z.content[0].text[:2000],flush=True)
asyncio.run(main())
