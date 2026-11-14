import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError:raise RuntimeError(str(z.content))
    print(n,z.content[0].text[:250],flush=True)
   obj='editor_toolset.toolsets.object.ObjectTools';bp='editor_toolset.toolsets.blueprint.BlueprintTools';p='/Game/Level/Stage2_BloomSign_Prototype.Stage2_BloomSign_Prototype:PersistentLevel.'
   values=json.dumps({'relativeScale3D':{'x':.45,'y':1,'z':.45}})
   await c(obj,'set_properties',{'instance':{'refPath':'/Game/BloomPuzzlePrototype/BP_BloomSign.Default__BP_BloomSign_C:Symbol'},'values':values})
   await c(bp,'compile_blueprint',{'blueprint':{'refPath':'/Game/BloomPuzzlePrototype/BP_BloomSign.BP_BloomSign'}})
   for i in range(3):
    await c(obj,'set_properties',{'instance':{'refPath':p+f'BP_BloomSign_C_{i}.Symbol'},'values':values})
   await c(obj,'set_properties',{'instance':{'refPath':p+'BP_BloomController_C_0'},'values':json.dumps({'bloomIntensity':70.0})})
   await c('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':['/Game/BloomPuzzlePrototype/BP_BloomSign','/Game/Level/Stage2_BloomSign_Prototype']})
asyncio.run(main())
