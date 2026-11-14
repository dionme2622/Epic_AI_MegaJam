import bpy, math
from mathutils import Vector
from pathlib import Path
out=Path(r'C:/LHH/Epic_AI_MegaJam/MegaJam/output/ShadowStage')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);return m
green=mat('DragonGreen',(.12,.28,.13));belly=mat('Belly',(.66,.51,.27));claw=mat('Claw',(.81,.77,.59));scale=mat('Scale',(.07,.17,.08))
def ell(n,loc,dim,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=loc);o=bpy.context.object;o.name=n;o.scale=dim;o.data.materials.append(m);return o
def cone_between(n,a,b,r1,r2,m):
 delta=Vector(b)-Vector(a);mid=(Vector(a)+Vector(b))/2;bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=r1,radius2=r2,depth=delta.length,location=mid);o=bpy.context.object;o.name=n;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();o.data.materials.append(m);return o
ell('Hip',(0,0,.92),(.48,.38,.30),green);ell('Underbelly',(.20,0,.91),(.31,.37,.24),belly)
for y in [-.25,.25]:
 ell('Thigh',(-.10,y,.62),(.24,.19,.35),green);ell('Shin',(.03,y,.30),(.17,.17,.27),green);ell('Foot',(.22,y,.10),(.30,.18,.12),green)
 for offset in [-.10,0,.10]:cone_between('Toe',(.41,y+offset,.11),(.52,y+offset,.06),.052,.008,claw)
cone_between('Tail base',(-.30,0,1),(-.95,0,.72),.21,.12,green);cone_between('Tail tip',(-.95,0,.72),(-1.55,0,.98),.12,.01,green)
for i in range(5):
 x=-.44-i*.19;z=.98-i*.03;cone_between('Tail ridge',(x,0,z),(x-.05,0,z+.20),.09,0,scale)
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.join();bpy.context.object.name='SM_DragonLowerBody'
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=str(out/'SM_DragonLowerBody.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'SM_DragonLowerBody.blend'))
