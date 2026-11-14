import bpy, math
from pathlib import Path
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
out=Path('C:/LHH/Epic_AI_MegaJam/MegaJam/output/FocusPuzzle'); out.mkdir(parents=True,exist_ok=True)
def export(name,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,mesh_smooth_type='FACE')
def material(name,col):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF') or m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=.65;p.inputs['Roughness'].default_value=.35
 return m
gold=material('M_Focus_Brass',(.64,.35,.08));steel=material('M_Focus_Teal',(.04,.32,.32))
bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=12,location=(0,0,0),major_radius=.38,minor_radius=.12,rotation=(math.pi/2,0,0))
ring=bpy.context.object;ring.name='SM_Focus_KeyHead';ring.data.materials.append(gold); export('SM_Focus_KeyHead',[ring])
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def box(name,loc,scale,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);return o
shaft=box('Shaft',(1,0,0),(2,.18,.18),steel)
teeth1=box('Tooth1',(1.48,0,-.19),(.18,.18,.35),steel)
teeth2=box('Tooth2',(1.85,0,-.19),(.18,.18,.35),steel)
bpy.ops.object.select_all(action='DESELECT')
for o in [shaft,teeth1,teeth2]:o.select_set(True)
bpy.context.view_layer.objects.active=shaft;bpy.ops.object.join();bpy.ops.object.origin_set(type='ORIGIN_CURSOR');export('SM_Focus_KeyShaft',[shaft])
bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=12,location=(-1.2,0,0),major_radius=.38,minor_radius=.12,rotation=(math.pi/2,0,0))
ring=bpy.context.object;ring.name='SM_Focus_KeyHead';ring.data.materials.append(gold)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'FocusProp_Source.blend'))
print('EXPORTED',out)
