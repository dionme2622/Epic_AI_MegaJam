import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(n,a):
    z=await s.call_tool('call_tool',{'toolset_name':'editor_toolset.toolsets.blueprint.BlueprintTools','tool_name':n,'arguments':a})
    if z.isError:raise RuntimeError(str(z.content))
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:1200],flush=True);return v
   ref=lambda x:{'refPath':x};path='/Game/FocusPropPrototype/BP_FocusIntro';bp=await c('create',{'folder_path':'/Game/FocusPropPrototype','asset_name':'BP_FocusIntro','asset_type':ref('/Script/Engine.Actor')})
   for name in ['ShotCamera','PuzzleController','ReturnTarget']:
    await c('add_object_variable',{'blueprint':bp,'name':name,'object_class':ref('/Script/Engine.Actor')})
    if name!='ReturnTarget':await c('set_variable_instance_editable',{'blueprint':bp,'variable_name':name,'instance_editable':True})
   graph=ref(path+'.BP_FocusIntro:EventGraph')
   for q in ['GetViewTarget','SetViewTargetwithBlend','Delay','SetActorTickEnabled','SetIgnoreMoveInput','IsValid']:
    await c('find_node_types',{'graph':graph,'type_id_filter':q,'context_pins':[]})
asyncio.run(main())
