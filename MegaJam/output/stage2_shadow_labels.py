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
    return json.loads(z.content[0].text).get('returnValue')
   scene='editor_toolset.toolsets.scene.SceneTools';obj='editor_toolset.toolsets.object.ObjectTools'
   for name,x,z,txt in [('SS_Controls',100,300,'A/D MOVE  |  E GRAB / RELEASE\nQ SHADOW ON / OFF'),('SS_Hint',650,380,'LIGHT DETECTS YOU\nSHADOW ON: HIDE BEHIND BOX'),('SS_LeverHint',1350,280,'E: PULL LEVER')]:
    a=await c(scene,'add_to_scene_from_class',{'actor_type':{'refPath':'/Script/Engine.TextRenderActor'},'name':name,'xform':{'location':{'x':x,'y':-290,'z':z},'rotation':{'pitch':0,'yaw':90,'roll':0}}})
    await c(obj,'set_properties',{'instance':{'refPath':a['refPath']+'.NewTextRenderComponent'},'values':json.dumps({'text':txt,'worldSize':26.0,'textRenderColor':{'r':1,'g':0.75,'b':0.05,'a':1}})})
   print(await c('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':['/Game/Level/Stage2_ShadowStealth_Prototype']}))
asyncio.run(main())
