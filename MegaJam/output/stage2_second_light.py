import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError: raise RuntimeError(str(z.content))
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:200],flush=True);return v
   scene='editor_toolset.toolsets.scene.SceneTools';obj='editor_toolset.toolsets.object.ObjectTools';p='/Game/Level/Stage2_ShadowStealth_Prototype.Stage2_ShadowStealth_Prototype:PersistentLevel.'
   spot=await c(scene,'add_to_scene_from_asset',{'asset_path':'/Game/Stage2ShadowPrototype/BP_S2_Spotlight.BP_S2_Spotlight','name':'SS_Spotlight_2','xform':{'location':{'x':1250,'y':0,'z':600}}})
   await c(obj,'set_properties',{'instance':spot,'values':json.dumps({'range':1000,'halfAngle':20,'sweepAngle':25,'sweepPeriod':8,'detectionDelay':.8})})
   await c(obj,'set_properties',{'instance':{'refPath':p+'BP_S2_SectionManager_C_0'},'values':json.dumps({'secondSpotlight':spot})})
   await c(obj,'set_properties',{'instance':{'refPath':p+'TextRenderActor_2.NewTextRenderComponent'},'values':json.dumps({'text':'Q OFF: FIND LEVER\nQ ON: HIDE / E: PULL'})})
   await c('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':['/Game/Level/Stage2_ShadowStealth_Prototype']})
asyncio.run(main())
