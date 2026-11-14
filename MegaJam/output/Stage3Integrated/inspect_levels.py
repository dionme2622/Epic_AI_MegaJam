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
    if z.isError:raise RuntimeError(f'{n} {z.content}')
    return json.loads(z.content[0].text).get('returnValue')
   sc='editor_toolset.toolsets.scene.SceneTools';ac='editor_toolset.toolsets.actor.ActorTools';ob='editor_toolset.toolsets.object.ObjectTools'
   levels=['/Game/DirectorCut/Stage/Stage2','/Game/Level/Stage3_puzzle1','/Game/Level/Stage3_puzzle','/Game/Level/Stage3_puzzle3'];report={}
   for path in levels:
    await c(sc,'load_level',{'level_path':path});wset=(await c(sc,'find_actors',{'name':'WorldSettings','tag':'','collision_channels':[]}))[0];assert path+'.' in wset['refPath'],wset
    actors=await c(sc,'find_actors',{'name':'','tag':'','collision_channels':[]});rows=[]
    for a in actors:
     try:
      cl=await c(ob,'get_class',{'instance':a});tf=await c(ac,'get_actor_transform',{'actor':a});bounds=await c(ac,'get_actor_bounds',{'actor':a});rows.append({'ref':a['refPath'],'class':cl['refPath'],'transform':tf,'bounds':bounds})
     except Exception as e:rows.append({'ref':a['refPath'],'error':str(e)})
    report[path]=rows;print('LEVEL',path,'ACTORS',len(rows),flush=True)
    for z in rows:
     cl=z.get('class','');tf=z.get('transform',{}).get('location',{});name=z['ref'].split('.')[-1]
     if not any(n in cl for n in ['StaticMeshActor','Brush','WorldSettings','DefaultPhysicsVolume','AbstractNavData','Buoyancy','GameplayDebugger','ChaosDebug']):print(' ',name,cl,tf,flush=True)
    for z in rows:
     b=z.get('bounds',{});mi=b.get('min',{});ma=b.get('max',{})
     if mi and ma and abs(ma['x']-mi['x'])>400:print(' BOUNDS',z['ref'].split('.')[-1],round(mi['x']),round(ma['x']),round(mi['z']),round(ma['z']),flush=True)
   Path('output/Stage3Integrated/levels_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
asyncio.run(main())
