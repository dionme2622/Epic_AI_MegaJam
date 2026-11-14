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
   bp='editor_toolset.toolsets.blueprint.BlueprintTools';ob='editor_toolset.toolsets.object.ObjectTools';sc='editor_toolset.toolsets.scene.SceneTools';assets='editor_toolset.toolsets.asset.AssetTools'
   ref=lambda x:{'refPath':x};folder='/Game/DirectorCut/Transitions'
   backup='/Game/DirectorCut/Transitions/Backups/L_Stage1_BeforeTransition'
   if not await c(assets,'duplicate',{'path':'/Game/DirectorCut/Stage1/L_Stage1','new_path':backup}):raise RuntimeError('Could not back up open level')
   await c(assets,'save_assets',{'asset_paths':[backup]})
   for name in ['BP_StageRightExit','BP_StageFadeIn']:
    await c(bp,'create',{'folder_path':folder,'asset_name':name,'asset_type':ref('/Script/Engine.Actor')})
   exitbp=ref(folder+'/BP_StageRightExit.BP_StageRightExit')
   await c(bp,'add_variable',{'blueprint':exitbp,'name':'TransitionStarted','type_name':'bool'})
   await c(bp,'add_variable',{'blueprint':exitbp,'name':'ExitX','type_name':'float'})
   await c(bp,'set_variable_instance_editable',{'blueprint':exitbp,'variable_name':'ExitX','instance_editable':True})
   for name,source in [('BP_StageRightExit','StageExit.dsl'),('BP_StageFadeIn','StageFadeIn.dsl')]:
    await c(bp,'write_graph_dsl',{'graph':ref(folder+'/'+name+'.'+name+':EventGraph'),'code':Path('output/Prologue_Fortress/'+source).read_text(encoding='utf8')})
    await c(bp,'compile_blueprint',{'blueprint':ref(folder+'/'+name+'.'+name)})
   a=await c(sc,'add_to_scene_from_asset',{'asset_path':exitbp['refPath'],'name':'Stage1_RightExit_Fade','xform':{'location':{'x':0,'y':0,'z':0}}})
   await c(ob,'set_properties',{'instance':a,'values':json.dumps({'ExitX':1650.0})})
   print('EXIT_ACTOR',a,flush=True)
   await c(assets,'save_assets',{'asset_paths':['/Game/DirectorCut/Stage1/L_Stage1',folder+'/BP_StageRightExit',folder+'/BP_StageFadeIn']})
asyncio.run(main())
