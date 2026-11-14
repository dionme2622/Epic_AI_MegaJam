import asyncio,json
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError:raise RuntimeError(f'{n}: {z.content}')
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:400],flush=True);return v
   ref=lambda x:{'refPath':x};sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';sm='editor_toolset.toolsets.static_mesh.StaticMeshTools';act='editor_toolset.toolsets.actor.ActorTools';asset='editor_toolset.toolsets.asset.AssetTools'
   root='/Game/BloomPuzzlePrototype/DetailRefined';names=['SM_Bloom_Frame_Ornate','SM_Bloom_Star_Refined','SM_Bloom_Moon_Refined','SM_Bloom_Sun_Refined']
   def mesh(n):return ref(root+'/'+n+'.'+n)
   for n in names:
    await c(sm,'import_file',{'folder_path':root,'asset_name':n,'source_file':'C:/LHH/Epic_AI_MegaJam/MegaJam/output/BloomPuzzle/DetailRefined/'+n+'.fbx','import_materials':False,'import_textures':False,'combine_meshes':True})
    print('SLOTS',n,await c(sm,'get_material_slots',{'mesh':mesh(n)}),flush=True)
   dark=ref('/Game/Stage1Generated/RefinedMachinery/M_DarkIron.M_DarkIron');gold=ref('/Game/Stage1Generated/Meshes/M_Brass_Trim.M_Brass_Trim');ink=ref('/Game/BloomPuzzlePrototype/M_BloomInk.M_BloomInk')
   for slot,material in [('DetailIron',dark),('DetailBrass',gold)]:await c(sm,'set_material',{'mesh':mesh(names[0]),'slot_name':slot,'material':material})
   for n in names[1:]:await c(sm,'set_material',{'mesh':mesh(n),'slot_name':'DetailInk','material':ink})
   signs=await c(sc,'find_actors',{'name':'Bloom_Sign','tag':'','collision_channels':[]})
   nums=await c(sc,'find_actors',{'name':'Bloom_Number','tag':'','collision_channels':[]})
   if len(signs)!=3 or len(nums)!=3:raise RuntimeError('Expected exactly three signs and three number labels')
   for a in signs:
    symref=ref(a['refPath']+'.Symbol');frameref=ref(a['refPath']+'.Frame')
    old=json.loads(await c(ob,'get_properties',{'instance':symref,'properties':['staticMesh']}))['staticMesh']['refPath']
    kind=next((x for x in ['Star','Moon','Sun'] if 'SM_Bloom_'+x in old),None)
    if not kind:raise RuntimeError('Unknown sign mesh '+old)
    await c(ob,'set_properties',{'instance':symref,'values':json.dumps({'staticMesh':mesh('SM_Bloom_'+kind+'_Refined'),'overrideMaterials':[]})})
    await c(ob,'set_properties',{'instance':frameref,'values':json.dumps({'staticMesh':mesh(names[0]),'overrideMaterials':[dark,gold]})})
   for a in signs+nums:
    transform=await c(act,'get_actor_transform',{'actor':a});transform['location']['z']+=35.0
    await c(act,'set_actor_transform',{'actor':a,'xform':transform})
   await c(asset,'save_assets',{'asset_paths':['/Game/Level/Stage2_BloomSign_Prototype']+[root+'/'+n for n in names]})
asyncio.run(main())
