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
    print(n,z.content[0].text[:250],flush=True);return json.loads(z.content[0].text).get('returnValue')
   scene='editor_toolset.toolsets.scene.SceneTools'; obj='editor_toolset.toolsets.object.ObjectTools'
   labels=[(None,300,'SHADOW: Q ON/OFF\nA: F/G   B: H/J'),('S2_LabelSymbols',1550,'SYMBOLS  1 / 2 / 3\nSTAR > MOON > SUN'),('S2_LabelFilm',2600,'FILMS: 4 / 5 / 6\nB: BLOOM  Q: SHADOW\nN: EXPOSURE'),('S2_LabelConsole',3200,'ANSWER: 7 / 8 / 9\nENTER: SUBMIT   P: STATUS')]
   for name,x,txt in labels:
    a={'refPath':'/Game/Level/Stage2.Stage2:PersistentLevel.TextRenderActor_0'} if name is None else await c(scene,'add_to_scene_from_class',{'actor_type':{'refPath':'/Script/Engine.TextRenderActor'},'name':name,'xform':{'location':{'x':x,'y':-150,'z':320},'rotation':{'pitch':0,'yaw':90,'roll':0}}})
    await c(obj,'set_properties',{'instance':{'refPath':a['refPath']+'.NewTextRenderComponent'},'values':json.dumps({'text':txt,'worldSize':24.0,'textRenderColor':{'r':1,'g':0.85,'b':0.1,'a':1}})})
   await c('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':['/Game/Level/Stage2']})
asyncio.run(main())
