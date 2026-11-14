import asyncio,json
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
script='''import json

def run_tool(name, args):
    return execute_tool(name, json.dumps(args)).get("returnValue")

def run():
    sc="editor_toolset.toolsets.scene.SceneTools."
    ob="editor_toolset.toolsets.object.ObjectTools."
    ac="editor_toolset.toolsets.actor.ActorTools."
    output={}
    for level in ["/Game/Level/Stage4_puzzle0","/Game/Level/Stage4_puzzle1"]:
        run_tool(sc+"load_level",{"level_path":level})
        actors=run_tool(sc+"find_actors",{"name":"","tag":"","collision_channels":[]})
        rows=[]
        for a in actors:
            try:
                cl=run_tool(ob+"get_class",{"instance":a})
                xf=run_tool(ac+"get_actor_transform",{"actor":a})
                bounds=run_tool(ac+"get_actor_bounds",{"actor":a})
                rows.append({"ref":a["refPath"],"class":cl["refPath"],"xform":xf,"bounds":bounds})
            except Exception as e:
                rows.append({"ref":a["refPath"],"error":str(e)})
        output[level]=rows
    return output
'''
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize();z=await s.call_tool('call_tool',{'toolset_name':'editor_toolset.toolsets.programmatic.ProgrammaticToolset','tool_name':'execute_tool_script','arguments':{'script':script}})
   if z.isError:raise RuntimeError(str(z.content))
   data=json.loads(json.loads(z.content[0].text)['returnValue']);Path('output/Stage4Integrated/report.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
   for level,rows in data.items():
    print('\nLEVEL',level,'COUNT',len(rows),flush=True)
    for x in rows:
     cls=x.get('class','');name=x['ref'].split('.')[-1];p=x.get('xform',{}).get('location',{});b=x.get('bounds',{});mi=b.get('min',{});ma=b.get('max',{})
     if 'StaticMeshActor' not in cls and not any(t in cls for t in ['Brush','WorldSettings','DefaultPhysicsVolume','AbstractNavData','Buoyancy','GameplayDebugger','ChaosDebug','Atmosphere','SkyLight','Fog','DirectionalLight','VolumetricCloud']):print('ACTOR',name,cls,p,flush=True)
     if mi and ma and 400<ma['x']-mi['x']<50000:print('WIDE',name,round(mi['x']),round(ma['x']),round(mi['z']),round(ma['z']),flush=True)
asyncio.run(main())
