import bpy, math, json
from pathlib import Path
from mathutils import Matrix, Quaternion, Vector

root = Path(r'D:\UnrealProject\Epic_AI_MegaJam\MegaJam\SourceAssets\NewKnight')
src = root / 'tripo_convert_1c33cd90-aa1b-4962-ae3e-405edf6eac71.fbx'
tex = root / 'tripo_convert_1c33cd90-aa1b-4962-ae3e-405edf6eac71.fbm' / 'heroic_knight_3d_model_basecolor.PNG'
sword_src = Path(r'C:\Users\서가은\Downloads\Knight_Combat_Package\Knight_Combat\Knight_Sword.fbx')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(src))
arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
body = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
arm.name = 'Knight_New_Rig'
body.name = 'Knight_New_Body'
arm.scale = (0.02, 0.02, 0.02)

mat = bpy.data.materials.new('M_Knight_New_BaseColor')
mat.use_nodes = True
nodes = mat.node_tree.nodes
nodes.clear()
out = nodes.new('ShaderNodeOutputMaterial')
out.location = (350, 0)
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.location = (50, 0)
bsdf.inputs['Roughness'].default_value = 0.55
bsdf.inputs['Metallic'].default_value = 0.18
img = nodes.new('ShaderNodeTexImage')
img.location = (-300, 100)
img.image = bpy.data.images.load(str(tex), check_existing=True)
img.image.pack()
mat.node_tree.links.new(img.outputs['Color'], bsdf.inputs['Base Color'])
mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
body.data.materials.clear()
body.data.materials.append(mat)

before = set(bpy.context.scene.objects)
bpy.ops.import_scene.fbx(filepath=str(sword_src))
swords = [o for o in set(bpy.context.scene.objects)-before if o.type == 'MESH']
assert len(swords) == 1, [o.name for o in swords]
sword = swords[0]
sword.name = 'Knight_New_Sword'
hand = arm.data.bones['mixamorig:RightHand']
hand_world = arm.matrix_world @ hand.head_local
sword.parent = arm
sword.matrix_parent_inverse = Matrix.Identity(4)
sword.location = hand.head_local + Vector((-1.0, -1.0, 0.0))
sword.scale = (50.0, 50.0, 50.0)
for g in list(sword.vertex_groups): sword.vertex_groups.remove(g)
g = sword.vertex_groups.new(name='mixamorig:RightHand')
g.add(list(range(len(sword.data.vertices))), 1.0, 'REPLACE')
mod = sword.modifiers.new('Rigid_Hand_Skin', 'ARMATURE')
mod.object = arm

def world_axis_pose(bone_name, axis, degrees):
    p = arm.pose.bones[bone_name]
    rest = arm.data.bones[bone_name].matrix_local.to_quaternion()
    q = Quaternion(Vector(axis), math.radians(degrees))
    p.rotation_mode = 'QUATERNION'
    p.rotation_quaternion = rest.inverted() @ q @ rest

scene = bpy.context.scene
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 121
action = bpy.data.actions.new('Knight_New_Combat_Idle')
arm.animation_data_create()
arm.animation_data.action = action
for frame in (1, 31, 61, 91, 121):
    phase = (frame-1) / 120 * 2 * math.pi
    scene.frame_set(frame)
    world_axis_pose('mixamorig:RightArm', (0,1,0), -58 + 2*math.sin(phase))
    world_axis_pose('mixamorig:LeftArm', (0,1,0), 63 - 2*math.sin(phase))
    world_axis_pose('mixamorig:RightForeArm', (0,1,0), 44 + 2*math.sin(phase))
    world_axis_pose('mixamorig:LeftForeArm', (0,1,0), -42 - 2*math.sin(phase))
    world_axis_pose('mixamorig:Spine1', (0,1,0), 3 + 1.2*math.sin(phase))
    for name in ('RightArm','LeftArm','RightForeArm','LeftForeArm','Spine1'):
        arm.pose.bones['mixamorig:'+name].keyframe_insert(data_path='rotation_quaternion', frame=frame)
    hips = arm.pose.bones['mixamorig:Hips']
    hips.location = (0, 0, 0.25*math.sin(phase))
    hips.keyframe_insert(data_path='location', frame=frame)

scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Knight_New_Combat_Idle.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in (arm,body,sword): o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=str(root/'Knight_New_Combat_Idle.fbx'), use_selection=True,
    object_types={'ARMATURE','MESH'}, add_leaf_bones=False, bake_anim=True,
    bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
    path_mode='COPY', embed_textures=True)

report = {'body_vertices':len(body.data.vertices),'sword_vertices':len(sword.data.vertices),
          'bones':len(arm.data.bones),'frames':121,'texture':str(tex),
          'hand_weights':min((v.groups[0].weight for v in sword.data.vertices), default=0),
          'body_unweighted':sum(not v.groups for v in body.data.vertices)}
for f in (1,31,61,91,121):
    scene.frame_set(f)
    deps = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(deps)
    mesh = ev.to_mesh()
    coords = [ev.matrix_world @ v.co for v in mesh.vertices]
    report[str(f)] = {'min_z':min(v.z for v in coords),'max_z':max(v.z for v in coords),
                      'bbox_x':[min(v.x for v in coords),max(v.x for v in coords)]}
    ev.to_mesh_clear()
(root/'validation_new.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('VALIDATION',json.dumps(report))
