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
    return json.loads(z.content[0].text).get('returnValue')
   ob='editor_toolset.toolsets.object.ObjectTools';tex='editor_toolset.toolsets.texture.TextureTools';mat='editor_toolset.toolsets.material.MaterialTools';sc='editor_toolset.toolsets.scene.SceneTools';assets='editor_toolset.toolsets.asset.AssetTools'
   ref=lambda p:{'refPath':p};folder='/Game/ResolutionCorridor/DotMarkers'
   async def props(o,v):return await c(ob,'set_properties',{'instance':o,'values':json.dumps(v)})
   t=(await c(tex,'import_file',{'folder_path':folder,'asset_name':'T_Dots_SafeV2','source_file':'C:/LHH/Epic_AI_MegaJam/MegaJam/output/ResolutionCorridor/DotMarkers/Dots_Safe.png'}))[0]
   m=await c(mat,'create_material',{'folder_path':folder,'asset_name':'M_Dots_SafeV2'})
   e=await c(mat,'add_expression',{'material_or_function':m,'expression_class':ref('/Script/Engine.MaterialExpressionTextureSample'),'x':-400,'y':0})
   await props(e,{'texture':t})
   for output,mp in [('RGB','MP_EmissiveColor'),('A','MP_OpacityMask')]:
    await c(mat,'connect_to_output',{'expression':e,'output_name':output,'material_property':mp})
   await props(m,{'shadingModel':'MSM_Unlit','blendMode':'BLEND_Masked','twoSided':True})
   await c(mat,'recompile',{'material_or_function':m})
   guides=await c(sc,'find_actors',{'name':'Resolution_Guide','tag':'','collision_channels':[]})
   if len(guides)!=3:raise RuntimeError('Expected exactly three guides')
   for a in guides:await props(ref(a['refPath']+'.StaticMeshComponent0'),{'overrideMaterials':[m]})
   await c(assets,'save_assets',{'asset_paths':['/Game/Level/Stage2_ResolutionCorridor_Prototype',folder+'/T_Dots_SafeV2',folder+'/M_Dots_SafeV2']})
asyncio.run(main())
