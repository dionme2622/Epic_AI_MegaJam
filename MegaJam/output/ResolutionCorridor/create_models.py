import bpy
from pathlib import Path
out=Path('C:/LHH/Epic_AI_MegaJam/MegaJam/output/ResolutionCorridor')
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(n,color):
 m=bpy.data.materials.new(n);m.diffuse_color=(*color,1);return m
stone=mat('FloorStone',(.29,.25,.28));rim=mat('IronRim',(.12,.12,.14));gold=mat('BronzeStud',(.51,.32,.10));arrow=mat('ArrowLight',(.1,1,.7))
def cube(n,loc,dim,m,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if bevel:
  x=o.modifiers.new('Soft edges','BEVEL');x.width=bevel;x.segments=2;bpy.ops.object.modifier_apply(modifier=x.name)
 return o
def export(n):
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name=n
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=str(out/(n+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False)
 print(n,len(o.data.vertices),[m.name for m in o.data.materials],flush=True);bpy.ops.wm.save_as_mainfile(filepath=str(out/(n+'.blend')))
cube('Tile housing',(0,0,-.03),(1.56,2.8,.19),rim,.012)
cube('Stone surface',(0,0,.07),(1.42,2.66,.09),stone,.015)
for x in [-.68,.68]:
 for y in [-1.25,1.25]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=.035,depth=.012,location=(x,y,.122));bpy.context.object.data.materials.append(gold)
export('SM_ResolutionTile')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
grid=['00100','00100','00100','11111','01110','00100']
for z,row in enumerate(grid):
 for x,v in enumerate(row):
  if v=='1':cube('Pixel',(x*.17-.34,0,.425-z*.17),(.155,.055,.155),arrow,.002)
export('SM_ResolutionArrow')
