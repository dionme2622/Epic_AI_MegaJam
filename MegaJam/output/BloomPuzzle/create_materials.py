import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError: raise RuntimeError(f'{n}: {z.content}')
    v=json.loads(z.content[0].text).get('returnValue'); print(n,str(v)[:500],flush=True);return v
   mat='editor_toolset.toolsets.material.MaterialTools';obj='editor_toolset.toolsets.object.ObjectTools';folder='/Game/BloomPuzzlePrototype'
   for name,col in [('M_BloomFace',{'r':7.0,'g':5.0,'b':2.0,'a':1.0}),('M_BloomInk',{'r':.012,'g':.006,'b':.018,'a':1.0})]:
    m=await c(mat,'create_material',{'folder_path':folder,'asset_name':name})
    expr=await c(mat,'add_expression',{'material_or_function':m,'expression_class':{'refPath':'/Script/Engine.MaterialExpressionConstant3Vector'},'x':-300,'y':0})
    await c(obj,'set_properties',{'instance':expr,'values':json.dumps({'constant':col})})
    await c(mat,'connect_to_output',{'expression':expr,'output_name':'','material_property':'MP_EmissiveColor'})
    await c(obj,'set_properties',{'instance':m,'values':json.dumps({'shadingModel':'MSM_Unlit'})})
    await c(mat,'recompile',{'material_or_function':m})
   await c('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':[folder+'/M_BloomFace',folder+'/M_BloomInk']})
asyncio.run(main())
