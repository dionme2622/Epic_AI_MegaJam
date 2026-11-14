import bpy, math
from pathlib import Path
from mathutils import Vector
root=Path('C:/LHH/Epic_AI_MegaJam/MegaJam/output/BloomPuzzle')
out=root/'DetailRefined';out.mkdir(exist_ok=True)
def clear():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(n,col):
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.diffuse_color=(*col,1);return m
gold=material('DetailBrass',(.55,.32,.09));iron=material('DetailIron',(.10,.075,.07))
def block(n,loc,dim,m,bevel=.012):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
 o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if bevel:
  mod=o.modifiers.new('Beveled edges','BEVEL');mod.width=bevel;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def stud(x,z,y,r,m):
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=.025,location=(x,y,z),rotation=(math.pi/2,0,0))
 bpy.context.object.data.materials.append(m)
def prism(n,points,thick,m):
 # silhouette in XZ plane, centered at the icon origin
 verts=[(x,y,z) for y in [-thick/2,thick/2] for x,z in points]
 N=len(points);faces=[tuple(reversed(range(N))),tuple(range(N,N*2))]
 faces += [(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update()
 o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);o.data.materials.append(m);return o
def sparkle(x,z,r,m):
 points=[]
 for i in range(8):
  a=math.pi/2+i*math.pi/4;rr=r if i%2==0 else r*.24
  points.append((x+rr*math.cos(a),z+rr*math.sin(a)))
 prism('Tiny star',points,.07,m)
def export(name):
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join()
 o=bpy.context.object;o.name=name;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False)
 print('EXPORT',name,'vertices',len(o.data.vertices),'mats',[m.name for m in o.data.materials],flush=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))
clear()
# Layered bevels sit outside the 1.30 m luminous square, so they do not cover the glyph.
for z in [-.735,.735]:
 block('Outer iron rail',(0,0,z),(1.66,.18,.15),iron)
 block('Inlaid brass edge',(0,.105,z),(1.56,.045,.055),gold,.008)
for x in [-.735,.735]:
 block('Outer iron upright',(x,0,0),(.15,.18,1.40),iron)
 block('Inlaid brass edge',(x,.105,0),(.055,.045,1.40),gold,.008)
for x in [-.735,.735]:
 for z in [-.735,.735]:
  block('Corner plate',(x,.135,z),(.20,.06,.20),gold,.018)
  stud(x,z,.18,.027,iron)
for x in [-.46,0,.46]:
 for z in [-.735,.735]:stud(x,z,.14,.022,gold)
for z in [-.38,0,.38]:
 for x in [-.735,.735]:stud(x,z,.14,.022,gold)
export('SM_Bloom_Frame_Ornate')
for n in ['Star','Moon','Sun']:
 clear();bpy.ops.import_scene.fbx(filepath=str(root/('SM_Bloom_'+n+'.fbx')))
 base=next(o for o in bpy.context.scene.objects if o.type=='MESH')
 ink=base.data.materials[0] if len(base.data.materials) else material('DetailInk',(.012,.006,.018))
 if not len(base.data.materials):base.data.materials.append(ink)
 if n=='Star':
  sparkle(-.37,.34,.075,ink);sparkle(.38,-.30,.060,ink)
 elif n=='Moon':
  sparkle(.31,.17,.105,ink);sparkle(.31,-.16,.045,ink)
 else:
  for i in range(8):
   a=i*math.pi/4+math.pi/8
   sparkle(.38*math.cos(a),.38*math.sin(a),.04,ink)
 bpy.ops.object.select_all(action='DESELECT')
 export('SM_Bloom_'+n+'_Refined')
