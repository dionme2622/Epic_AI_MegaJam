import asyncio,json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    if z.isError: raise RuntimeError(f'{n}: {z.content}')
    v=json.loads(z.content[0].text).get('returnValue');print(n,str(v)[:180],flush=True);return v
   scene='editor_toolset.toolsets.scene.SceneTools'; obj='editor_toolset.toolsets.object.ObjectTools'
   async def add(name,asset,x,y,z,sx=1,sy=1,sz=1):
    return await c(scene,'add_to_scene_from_asset',{'asset_path':asset,'name':name,'xform':{'location':{'x':x,'y':y,'z':z},'scale':{'x':sx,'y':sy,'z':sz}}})
   async def props(ref,values): await c(obj,'set_properties',{'instance':ref,'values':json.dumps(values)})
   cube='/Engine/BasicShapes/Cube.Cube';base='/Game/Stage2ShadowPrototype/'
   await add('SS_Floor',cube,850,0,-50,22,6,1)
   await add('SS_Backdrop',cube,850,-330,300,22,.2,7)
   crate=await add('SS_Crate',base+'BP_S2_Crate.BP_S2_Crate',350,0,120,1.5,2,2.4)
   await props(crate,{'tags':['S2Cover'],'railMinX':250,'railMaxX':1050,'moveSpeed':140})
   door=await add('SS_Door',base+'BP_S2_Door.BP_S2_Door',1650,0,150,.5,3,3)
   lever=await add('SS_Lever',base+'BP_S2_Lever.BP_S2_Lever',1420,0,65,.35,.35,1.3)
   spot=await add('SS_Spotlight',base+'BP_S2_Spotlight.BP_S2_Spotlight',800,0,600)
   await props(spot,{'range':1000,'halfAngle':24,'sweepAngle':25,'sweepPeriod':7,'detectionDelay':.8})
   checkpoint=await c(scene,'add_to_scene_from_class',{'actor_type':{'refPath':'/Script/Engine.TargetPoint'},'name':'SS_Checkpoint','xform':{'location':{'x':0,'y':0,'z':92}}})
   manager=await add('SS_Manager',base+'BP_S2_SectionManager.BP_S2_SectionManager',0,0,0)
   await props(manager,{'spotlight':spot,'crate':crate,'lever':lever,'door':door,'checkpoint':checkpoint})
   await c('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':['/Game/Level/Stage2_ShadowStealth_Prototype']})
asyncio.run(main())
