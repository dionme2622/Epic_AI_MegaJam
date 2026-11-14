import asyncio,json,shutil
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
    return json.loads(z.content[0].text).get('returnValue')
   ref=lambda p:{'refPath':p};sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';bp='editor_toolset.toolsets.blueprint.BlueprintTools';assets='editor_toolset.toolsets.asset.AssetTools';app='EditorToolset.EditorAppToolset'
   assert not await c(app,'IsPIERunning',{})
   level='/Game/DirectorCut/Stage/Stage2';folder='/Game/Stage3Integrated';name='BP_Stage2ToStage3';path=folder+'/'+name+'.'+name
   await c(sc,'load_level',{'level_path':level});ws=(await c(sc,'find_actors',{'name':'WorldSettings','tag':'','collision_channels':[]}))[0];assert level+'.' in ws['refPath']
   shutil.copy2('Content/DirectorCut/Stage/Stage2.umap','output/Stage3Integrated/Stage2_before_transition.umap')
   actors=await c(sc,'find_actors',{'name':'','tag':'','collision_channels':[]});old=next((a for a in actors if a['refPath'].endswith('.BP_Stage1ToIntegrated_C_0')),None)
   print('OLD',old,flush=True);exitx=9900.0
   if old:exitx=json.loads(await c(ob,'get_properties',{'instance':old,'properties':['ExitX']}))['ExitX'];print('EXIT_X',exitx,flush=True)
   b=await c(bp,'create',{'folder_path':folder,'asset_name':name,'asset_type':ref('/Script/Engine.Actor')})
   await c(bp,'add_variable',{'blueprint':b,'name':'TransitionStarted','type_name':'bool'});await c(bp,'add_variable',{'blueprint':b,'name':'ExitX','type_name':'float'});await c(bp,'set_variable_instance_editable',{'blueprint':b,'variable_name':'ExitX','instance_editable':True})
   code=Path('output/Prologue_Fortress/StageExit.dsl').read_text(encoding='utf8');code=code[code.index('(event EventTick'):].replace('/Game/Level/Stage1.Stage1','/Game/Level/Stage3_Integrated.Stage3_Integrated')
   await c(bp,'write_graph_dsl',{'graph':ref(path+':EventGraph'),'code':code});await c(bp,'compile_blueprint',{'blueprint':b})
   a=await c(sc,'add_to_scene_from_asset',{'asset_path':path,'name':'Stage2_To_Stage3_FadeExit','xform':{'location':{'x':0,'y':0,'z':0}}});await c(ob,'set_properties',{'instance':a,'values':json.dumps({'ExitX':exitx})})
   if old:assert await c(sc,'remove_from_scene',{'actor':old})
   print('SAVE',await c(assets,'save_assets',{'asset_paths':[level,folder+'/'+name]}),flush=True)
asyncio.run(main())
