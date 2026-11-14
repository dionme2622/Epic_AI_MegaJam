import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError:raise RuntimeError(f'{n}: {z.content}')
    return json.loads(z.content[0].text).get('returnValue')
   sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';asset='editor_toolset.toolsets.asset.AssetTools';path='/Game/Stage3Integrated/Sections/L_Resolution'
   await c(sc,'load_level',{'level_path':path});ws=(await c(sc,'find_actors',{'name':'WorldSettings','tag':'','collision_channels':[]}))[0];assert path+'.' in ws['refPath']
   ctrl=(await c(sc,'find_actors',{'name':'Resolution_Controller','tag':'','collision_channels':[]}))[0]
   vals={'bRestrictOverlayStart':True,'showOverlayFromOffsetX':-550.0,'hideOverlayBeyondX':1750.0,'bUseLocalCheckpoint':True,'localCheckpointOffset':{'x':-400.0,'y':0.0,'z':92.0}}
   print('SET',await c(ob,'set_properties',{'instance':ctrl,'values':json.dumps(vals)}),flush=True)
   print('VERIFY',await c(ob,'get_properties',{'instance':ctrl,'properties':list(vals)}),flush=True)
   print('SAVE',await c(asset,'save_assets',{'asset_paths':[path]}),flush=True)
   await c(sc,'load_level',{'level_path':'/Game/Level/Stage3_Integrated'})
asyncio.run(main())
