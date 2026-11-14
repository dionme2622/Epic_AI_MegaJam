import asyncio,json,base64
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
async def main():
 async with streamable_http_client('http://127.0.0.1:8000/mcp') as (r,w,_):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def c(t,n,a):
    z=await s.call_tool('call_tool',{'toolset_name':t,'tool_name':n,'arguments':a})
    print(n, str(z.content)[:600],flush=True)
    if z.isError:return None
    return json.loads(z.content[0].text).get('returnValue')
   app='EditorToolset.EditorAppToolset';ob='editor_toolset.toolsets.object.ObjectTools';act='editor_toolset.toolsets.actor.ActorTools'
   p='/Game/Level/Stage2_FocusProp_Prototype.Stage2_FocusProp_Prototype:PersistentLevel.BP_FocusPropPuzzle_C_0.'
   for n,fields in [('NearPiece',['relativeLocation','staticMesh']),('FarPiece',['relativeLocation','staticMesh']),('PuzzleCamera',['relativeLocation','relativeRotation','fieldOfView'])]:
    await c(ob,'get_properties',{'instance':{'refPath':p+n},'properties':fields})
   await c(app,'StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
   img=await c(app,'CaptureEditorImage',{})
   if img:Path('output/FocusPuzzle/intro_before.png').write_bytes(base64.b64decode(img['data']))
   await c('editor_toolset.toolsets.scene.SceneTools','find_actors',{'name':'Dragon','tag':'','collision_channels':[]})
   await c(app,'StopPIE',{})
asyncio.run(main())
