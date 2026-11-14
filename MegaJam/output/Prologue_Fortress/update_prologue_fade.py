import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(n,a):
    z=await s.call_tool('call_tool',{'toolset_name':'editor_toolset.toolsets.blueprint.BlueprintTools','tool_name':n,'arguments':a})
    if z.isError:raise RuntimeError(f'{n} {z.content}')
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:400],flush=True);return v
   ref=lambda x:{'refPath':x};base='/Game/DirectorCut/Prologue/BP_PrologueStageTransition.BP_PrologueStageTransition';graph=ref(base+':EventGraph')
   ev=ref(base+':EventGraph.K2Node_CustomEvent_0');op=ref(base+':EventGraph.K2Node_CallFunction_1')
   fade=ref(base+':EventGraph.K2Node_CallFunction_2')
   mgr=ref(base+':EventGraph.K2Node_CallFunction_3')
   delay=ref(base+':EventGraph.K2Node_CallFunction_4')
   await c('set_node_position',{'node':op,'pos':{'x':1000,'y':350}})
   pin=lambda node,d,i:{'node':node,'direction':'EGPD_'+d,'index_id':i}
   async def connect(a,ai,b,bi):await c('connect_pins',{'output_pin':pin(a,'Output',ai),'input_pin':pin(b,'Input',bi)})
   async def value(n,i,v):await c('set_pin_value',{'pin':pin(n,'Input',i),'value':v})
   await c('break_pins',{'output_pin':pin(ev,'Output',1),'input_pin':pin(op,'Input',0)})
   await connect(ev,1,fade,0);await connect(mgr,0,fade,1);await connect(fade,0,delay,0);await connect(delay,0,op,0)
   for i,v in [(2,'0.0'),(3,'1.0'),(4,'1.5'),(5,'(R=0.000000,G=0.000000,B=0.000000,A=1.000000)'),(6,'false'),(7,'true')]:await value(fade,i,v)
   await value(delay,1,'1.6')
   await value(op,1,'/Game/DirectorCut/Stage1/L_Stage1.L_Stage1')
   await c('compile_blueprint',{'blueprint':ref(base)})
   await c('get_node_infos',{'nodes':[fade,delay,op]})
   z=await s.call_tool('call_tool',{'toolset_name':'editor_toolset.toolsets.asset.AssetTools','tool_name':'save_assets','arguments':{'asset_paths':['/Game/DirectorCut/Prologue/BP_PrologueStageTransition']}})
   if z.isError:raise RuntimeError(str(z.content))
   print('SAVED',z.content,flush=True)
asyncio.run(main())
