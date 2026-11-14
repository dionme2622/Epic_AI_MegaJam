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
   sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';assets='editor_toolset.toolsets.asset.AssetTools'
   await c(sc,'load_level',{'level_path':'/Game/Level/Stage2_ShadowBody_Prototype'});ws=(await c(sc,'find_actors',{'name':'WorldSettings','tag':'','collision_channels':[]}))[0];assert '/Game/Level/Stage2_ShadowBody_Prototype.' in ws['refPath']
   p=await c(sc,'add_to_scene_from_class',{'actor_type':{'refPath':'/Script/Engine.PostProcessVolume'},'name':'ShadowStage_ColorGrade','xform':{'location':{'x':0,'y':0,'z':0}}});await c(ob,'set_properties',{'instance':p,'values':json.dumps({'bUnbound':True})})
   v=json.loads(await c(ob,'get_properties',{'instance':p,'properties':['settings']}))['settings'];print('SHADOW_PROPS',json.dumps({k:v[k] for k in v if ('shadow' in k.lower() or 'indirect' in k.lower() or 'exposure' in k.lower())},ensure_ascii=False),flush=True)
   await c(assets,'save_assets',{'asset_paths':['/Game/Level/Stage2_ShadowBody_Prototype']})
asyncio.run(main())
