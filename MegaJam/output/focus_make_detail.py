import bpy,math
from pathlib import Path
from mathutils import Vector
out=Path('C:/LHH/Epic_AI_MegaJam/MegaJam/output/FocusPuzzle/Detail');out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
groups={'Wood':[],'Brass':[],'Curtain':[],'Stone':[],'Head':[],'Shaft':[]}
def cube(group,loc,size,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=group;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Soft edges','BEVEL');mod.width=bevel;mod.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 groups[group].append(o);return o
def cyl(group,loc,radius,depth,rot=(math.pi/2,0,0),vertices=16):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=group;groups[group].append(o);return o
def torus(group,loc,major,minor):
 bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=12,location=loc,major_radius=major,minor_radius=minor,rotation=(math.pi/2,0,0));o=bpy.context.object;o.name=group;groups[group].append(o);return o
# The ring connector remains at x=+0.50m, matching the C++ alignment point.
torus('Head',(0,0,0),.38,.12)
torus('Head',(0,-.135,0),.37,.035)
for i in range(8):
 a=2*math.pi*i/8;cyl('Head',(.38*math.cos(a),-.155,.38*math.sin(a)),.035,.035,vertices=12)
cube('Shaft',(1,0,0),(2,.18,.18),.025)
cube('Shaft',(1.48,0,-.17),(.2,.2,.32),.018)
cube('Shaft',(1.82,0,-.20),(.22,.2,.38),.018)
for x in [.25,.45,1.05,1.25]: cube('Shaft',(x,-.11,0),(.04,.04,.22),.008)
# Set geometry uses metres, with +Y mapping to the background side in Unreal.
for x in [-.8,10.0]:
 cube('Wood',(x,3.5,3.2),(.28,.28,6.4),.04)
 for z in [.6,2.4,4.2,6.0]: cube('Brass',(x,3.32,z),(.36,.06,.10),.012)
cube('Wood',(4.6,3.5,6.25),(11,.3,.30),.04)
cube('Brass',(4.6,3.28,6.04),(10.8,.08,.08),.01)
cube('Curtain',(4.6,3.38,5.6),(10.7,.10,.62),.02)
for x in [0,1.3,2.6,3.9,5.2,6.5,7.8,9.1]: cube('Wood',(x,3.2,5.6),(.055,.1,.55),.01)
# Horizontal guide rails, posts, and separate visual slider markers.
for z in [1.98,2.18]: cube('Brass',(4.9,2.55,z),(7.9,.1,.06),.012)
for x in [1.0,8.8]: cube('Wood',(x,2.65,2.25),(.15,.2,.8),.025)
for x in [1.45,2.35,3.25,4.15,5.05,5.95,6.85,7.75,8.65]: cyl('Brass',(x,2.47,2.08),.035,.04,vertices=12)
# Exposed braces and rivets tell the player this is a constructed theatre set.
for x in [.1,9.1]:
 cube('Wood',(x,3.0,2.9),(.12,.14,5.6),.015)
 for z in [.5,1.5,2.5,3.5,4.5,5.5]: cyl('Brass',(x,2.90,z),.04,.04,vertices=12)
for x in [1.3,7.7]:
 cube('Wood',(x,3.1,.65),(.8,.55,1.3),.04)
 cube('Brass',(x,2.79,1.3),(.85,.08,.08),.01)

for group in ['Head','Shaft']:
 bpy.ops.object.select_all(action='DESELECT')
 for o in groups[group]: o.select_set(True)
 bpy.context.view_layer.objects.active=groups[group][0];bpy.ops.object.join()
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');groups[group]=[bpy.context.object]

def export(group):
 members=groups[group]
 if not members:return
 bpy.ops.object.select_all(action='DESELECT')
 for o in members:o.select_set(True)
 bpy.context.view_layer.objects.active=members[0]
 bpy.ops.export_scene.fbx(filepath=str(out/('SM_FocusDetail_'+group+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE')
for group in groups:export(group)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'FocusDetail_Source.blend'))
print('FOCUS_DETAIL_EXPORTED',out)
