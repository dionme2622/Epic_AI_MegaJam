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
    if z.isError:raise RuntimeError(str(z.content))
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:800],flush=True);return v
   app='EditorToolset.EditorAppToolset'; bp='editor_toolset.toolsets.blueprint.BlueprintTools';ob='editor_toolset.toolsets.object.ObjectTools';sc='editor_toolset.toolsets.scene.SceneTools';assets='editor_toolset.toolsets.asset.AssetTools';ref=lambda x:{'refPath':x}
   if await c(app,'IsPIERunning',{}):await c(app,'StopPIE',{})
   await c(sc,'load_level',{'level_path':'/Game/Level/Stage1'})
   for name in ['Ground','Exit','Door','Dragon','Stage1_EntryFade']:
    print('FIND',name,await c(sc,'find_actors',{'name':name,'tag':'','collision_channels':[]}),flush=True)
   shutil.copy2('Content/Level/Stage1.umap','output/Stage2Integrated/Stage1_before_integrated.umap')
   folder='/Game/Stage2Integrated';name='BP_Stage1ToIntegrated';path=folder+'/'+name+'.'+name
   b=await c(bp,'create',{'folder_path':folder,'asset_name':name,'asset_type':ref('/Script/Engine.Actor')})
   await c(bp,'add_variable',{'blueprint':ref(path),'name':'TransitionStarted','type_name':'bool'})
   await c(bp,'add_variable',{'blueprint':ref(path),'name':'ExitX','type_name':'float'})
   await c(bp,'set_variable_instance_editable',{'blueprint':ref(path),'variable_name':'ExitX','instance_editable':True})
   code=Path('output/Prologue_Fortress/StageExit.dsl').read_text(encoding='utf8');code=code[code.index('(event EventTick'):].replace('/Game/Level/Stage1.Stage1','/Game/Level/Stage2_Integrated.Stage2_Integrated')
   await c(bp,'write_graph_dsl',{'graph':ref(path+':EventGraph'),'code':code})
   await c(bp,'compile_blueprint',{'blueprint':ref(path)})
   a=await c(sc,'add_to_scene_from_asset',{'asset_path':path,'name':'Stage1_To_Stage2_FadeExit','xform':{'location':{'x':0,'y':0,'z':0}}})
   await c(ob,'set_properties',{'instance':a,'values':json.dumps({'ExitX':9900.0})})
   await c(assets,'save_assets',{'asset_paths':['/Game/Level/Stage1',folder+'/'+name]})
asyncio.run(main())
