import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    print(n,z.content,flush=True)
    if z.isError:raise RuntimeError(str(z.content))
    return json.loads(z.content[0].text).get('returnValue')
   bp='editor_toolset.toolsets.blueprint.BlueprintTools';sc='editor_toolset.toolsets.scene.SceneTools';ob='editor_toolset.toolsets.object.ObjectTools';assets='editor_toolset.toolsets.asset.AssetTools'
   base='/Game/DirectorCut/Prologue/BP_PrologueStageTransition.BP_PrologueStageTransition'
   ref=lambda p:{'refPath':p};node=lambda n:ref(base+':EventGraph.'+n)
   pin=lambda n,d,i:{'node':node(n),'direction':d,'index_id':i}
   ev='K2Node_CustomEvent_0';bind='K2Node_AddDelegate_1';open='K2Node_CallFunction_1'
   await c(bp,'connect_pins',{'output_pin':pin(ev,'EGPD_Output',0),'input_pin':pin(bind,'EGPD_Input',2)})
   await c(bp,'connect_pins',{'output_pin':pin(ev,'EGPD_Output',1),'input_pin':pin(open,'EGPD_Input',0)})
   await c(bp,'set_pin_value',{'pin':pin(open,'EGPD_Input',1),'value':'/Game/Level/Stage1.Stage1'})
   await c(bp,'delete_node',{'node':node('K2Node_CreateDelegate_1')})
   await c(bp,'compile_blueprint',{'blueprint':ref(base)})
   a=await c(sc,'add_to_scene_from_asset',{'asset_path':base,'name':'Prologue_Stage1_Transition','xform':{'location':{'x':0,'y':0,'z':0}}})
   seq=ref('/Game/DirectorCut/Prologue/L_BossPrologue.L_BossPrologue:PersistentLevel.LevelSequenceActor_0')
   await c(ob,'set_properties',{'instance':a,'values':json.dumps({'PrologueSequence':seq})})
   await c(ob,'get_properties',{'instance':a,'properties':['PrologueSequence']})
   await c(assets,'save_assets',{'asset_paths':['/Game/DirectorCut/Prologue/BP_PrologueStageTransition','/Game/DirectorCut/Prologue/L_BossPrologue']})
asyncio.run(main())
