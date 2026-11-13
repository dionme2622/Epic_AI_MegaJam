import bpy
from mathutils import Vector

root = r'D:\UnrealProject\Epic_AI_MegaJam\MegaJam\SourceAssets'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=root + r'\NewKnight\tripo_convert_1c33cd90-aa1b-4962-ae3e-405edf6eac71.fbx')
for o in bpy.data.objects:
    corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
    print('NEW', o.name, o.type, len(o.data.vertices) if o.type == 'MESH' else '',
          [(round(min(v[i] for v in corners), 3), round(max(v[i] for v in corners), 3)) for i in range(3)])
    if o.type == 'MESH':
        print('MATERIALS', [m.name for m in o.data.materials], 'UV', len(o.data.uv_layers))
        print('GROUPS', [g.name for g in o.vertex_groups][:30])
        for m in o.data.materials:
            if m and m.use_nodes:
                print('TEX', [(n.name, n.image.filepath if n.image else '') for n in m.node_tree.nodes if n.type == 'TEX_IMAGE'])
    if o.type == 'ARMATURE':
        print('TRANSFORM', tuple(o.location), tuple(o.rotation_euler), tuple(o.scale))
        for b in o.data.bones:
            if any(k in b.name for k in ('Hips','Spine','Shoulder','Arm','Hand','Leg','Foot')) and not any(k in b.name for k in ('Index','Middle','Pinky','Ring','Thumb','ForeArmTwist')):
                print('BONE',b.name,tuple(round(x,3) for x in b.head_local),tuple(round(x,3) for x in b.tail_local))
bpy.ops.wm.open_mainfile(filepath=root + r'\Knight_Combat\Knight_Combat.blend')
for o in bpy.data.objects:
    if o.type not in {'MESH','ARMATURE'}: continue
    corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
    print('OLD', o.name, o.type, len(o.data.vertices) if o.type == 'MESH' else '',
          [(round(min(v[i] for v in corners), 3), round(max(v[i] for v in corners), 3)) for i in range(3)])
    if o.type == 'MESH': print('GROUPS', [g.name for g in o.vertex_groups][:30])
