"""Build an original Blender armature, skin and idle animation for the cleaned knight.

Run with Blender 5.3: blender -b -noaudio --python rig_animation.py
The supplied FBX is only a reference mesh/texture. No source rig or weights are used.
"""
from __future__ import annotations

import json
import math
import subprocess
import tempfile
from pathlib import Path

import bpy
from mathutils import Quaternion, Vector


ROOT = Path(__file__).resolve().parent
INPUT_BLEND = ROOT / 'CleanUV_Knight.blend'
OUTPUT_BLEND = ROOT / 'HeroicKnight_Clean_Rigged.blend'
OUTPUT_FBX = ROOT / 'HeroicKnight_Clean_Rigged.fbx'
REPORT = ROOT / 'rig_validation.json'
TARGET_HEIGHT_M = 1.73828


def load_body():
    if INPUT_BLEND.exists():
        bpy.ops.wm.open_mainfile(filepath=str(INPUT_BLEND))
    else:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        src = next(ROOT.glob('tripo_convert_*.fbx'))
        bpy.ops.import_scene.fbx(filepath=str(src))
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    assert len(meshes) == 1, [(o.name, o.type) for o in bpy.data.objects]
    body = meshes[0]
    body.name = 'Knight_Body'
    # The unrigged FBX imports at 0.869 m. Production character is 1.738 m.
    world = [body.matrix_world @ v.co for v in body.data.vertices]
    height = max(v.z for v in world) - min(v.z for v in world)
    ratio = TARGET_HEIGHT_M / height
    body.scale *= ratio
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    world = [body.matrix_world @ v.co for v in body.data.vertices]
    assert abs(min(v.z for v in world)) < .002
    assert abs(max(v.z for v in world) - TARGET_HEIGHT_M) < .002
    return body


def make_armature():
    data = bpy.data.armatures.new('HeroicKnight_Armature')
    arm = bpy.data.objects.new('HeroicKnight_Rig', data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

    # Bone heads/tails were placed from the supplied mesh's T pose in metres.
    specs = [
        ('root', (0, 0, 0), (0, 0, .08), None),
        ('pelvis', (0, 0, .76), (0, 0, .90), 'root'),
        ('spine', (0, 0, .90), (0, 0, 1.12), 'pelvis'),
        ('chest', (0, 0, 1.12), (0, 0, 1.30), 'spine'),
        ('neck', (0, 0, 1.30), (0, 0, 1.40), 'chest'),
        ('head', (0, -.015, 1.40), (0, -.025, 1.63), 'neck'),
    ]
    for side, s in [('L', 1), ('R', -1)]:
        specs += [
            (f'clavicle_{side}', (.11*s, 0, 1.275), (.33*s, 0, 1.275), 'chest'),
            (f'upperarm_{side}', (.33*s, 0, 1.275), (.57*s, 0, 1.275), f'clavicle_{side}'),
            (f'forearm_{side}', (.57*s, 0, 1.275), (.78*s, 0, 1.275), f'upperarm_{side}'),
            (f'hand_{side}', (.78*s, 0, 1.275), (.95*s, 0, 1.275), f'forearm_{side}'),
            (f'thigh_{side}', (.145*s, .005, .77), (.14*s, 0, .49), 'pelvis'),
            (f'shin_{side}', (.14*s, 0, .49), (.145*s, 0, .26), f'thigh_{side}'),
            (f'foot_{side}', (.145*s, 0, .26), (.145*s, -.16, .105), f'shin_{side}'),
            (f'toe_{side}', (.145*s, -.16, .105), (.145*s, -.245, .085), f'foot_{side}'),
        ]
    # Broad cape is weighted to chest/spine. A cape sway chain is provided for
    # later cloth animation but kept neutral in the exported idle.
    specs += [
        ('cape_upper', (0, .105, 1.25), (0, .13, 1.03), 'chest'),
        ('cape_lower', (0, .13, 1.03), (0, .14, .78), 'cape_upper'),
    ]
    bones = {}
    for name, head, tail, parent in specs:
        b = data.edit_bones.new(name)
        b.head = head
        b.tail = tail
        b.use_deform = name != 'root'
        if parent:
            b.parent = bones[parent]
            b.use_connect = False
        bones[name] = b
    bpy.ops.object.mode_set(mode='OBJECT')
    arm.show_in_front = True
    return arm


def auto_skin(body, arm):
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    try:
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        print('SKIN auto bone heat succeeded')
    except RuntimeError as exc:
        print('SKIN auto bone heat failed:', exc)
        bpy.ops.object.mode_set(mode='OBJECT')
        body.parent = arm
        mod = body.modifiers.get('Armature') or body.modifiers.new('Armature', 'ARMATURE')
        mod.object = arm
        procedural_skin(body)
    # Trim tiny heat artefacts and cap at four influences for game export.
    groups = body.vertex_groups
    if not groups:
        procedural_skin(body)
    # The back of the cape is well separated from the arms in the rest pose.
    # Heat weights sometimes leak a few percent of arm/thigh influence into it.
    # Keep the drape on its own chain plus its shoulder/chest attachment.
    for vertex in body.data.vertices:
        x, y, z = vertex.co
        if not (y > .12 and .72 < z < 1.30 and abs(x) < .40):
            continue
        leaks = [(groups[a.group].name, a.weight) for a in vertex.groups
                 if groups[a.group].name.startswith(('upperarm_', 'forearm_', 'hand_',
                                                       'thigh_', 'shin_', 'foot_', 'toe_'))]
        if not leaks:
            continue
        amount = sum(weight for _, weight in leaks)
        for name, _ in leaks:
            groups[name].remove([vertex.index])
        cape_name = 'cape_upper' if z > 1.0 else 'cape_lower'
        current = next((a.weight for a in vertex.groups
                        if groups[a.group].name == cape_name), 0.0)
        groups[cape_name].add([vertex.index], current + amount, 'REPLACE')
    for vertex in body.data.vertices:
        weights = [(groups[a.group].name, a.weight) for a in vertex.groups if a.weight > 1e-5]
        if not weights:
            # Should never occur, but keep every vertex skinned.
            groups['pelvis'].add([vertex.index], 1.0, 'REPLACE')
            continue
        weights.sort(key=lambda p: p[1], reverse=True)
        keep = weights[:4]
        denom = sum(w for _, w in keep)
        for name, _ in weights:
            groups[name].remove([vertex.index])
        for name, w in keep:
            groups[name].add([vertex.index], w / denom, 'REPLACE')


def procedural_skin(body):
    # Fallback and audit-friendly coordinate based skin. This is never used if
    # Blender's bone heat succeeds, but avoids an unweighted deliverable.
    names = ['pelvis','spine','chest','neck','head','cape_upper','cape_lower']
    names += [f'{part}_{side}' for side in ('L','R') for part in ('clavicle','upperarm','forearm','hand','thigh','shin','foot','toe')]
    gs = {n: body.vertex_groups.get(n) or body.vertex_groups.new(name=n) for n in names}
    def pair(a, b, t):
        t = min(1.0, max(0.0, t))
        return [(a, 1-t), (b, t)]
    for v in body.data.vertices:
        x, y, z = v.co
        a = abs(x)
        side = 'L' if x >= 0 else 'R'
        if z > 1.36 and a < .32:
            assignments = pair('neck', 'head', (z-1.36)/.06)
        elif z > 1.16 and a > .29:
            if a < .57:
                assignments = pair(f'upperarm_{side}', f'forearm_{side}', (a-.54)/.06)
            elif a < .78:
                assignments = pair(f'forearm_{side}', f'hand_{side}', (a-.75)/.06)
            else:
                assignments = [(f'hand_{side}',1)]
        elif z < .74 and a > .06:
            if z > .47:
                assignments = pair(f'shin_{side}', f'thigh_{side}', (z-.47)/.05)
            elif z > .26:
                assignments = pair(f'foot_{side}', f'shin_{side}', (z-.26)/.05)
            else:
                assignments = [(f'foot_{side}',1)]
        elif y > .105 and .77 < z < 1.26 and a < .36:
            assignments = pair('cape_lower','cape_upper',(z-.90)/.16)
        elif z > 1.26:
            assignments = pair('chest','neck',(z-1.28)/.10)
        elif z > 1.07:
            assignments = [('chest',1)]
        elif z > .86:
            assignments = pair('pelvis','spine',(z-.86)/.14)
        else:
            assignments = [('pelvis',1)]
        for name,w in assignments:
            if w > 1e-5: gs[name].add([v.index], float(w), 'REPLACE')


def rotation(pbone, axis, angle_deg):
    rest = pbone.bone.matrix_local.to_quaternion()
    q = Quaternion(Vector(axis), math.radians(angle_deg))
    pbone.rotation_mode = 'QUATERNION'
    pbone.rotation_quaternion = rest.inverted() @ q @ rest


def animate_idle(arm):
    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 61
    action = bpy.data.actions.new('HeroicKnight_Clean_Idle')
    arm.animation_data_create()
    arm.animation_data.action = action
    # 2 s, single cycle. Feet and root stay planted.
    for frame in (1, 16, 31, 46, 61):
        phase = 2 * math.pi * (frame-1) / 60
        scene.frame_set(frame)
        values = {
            'chest': ((1,0,0), 1.1*math.sin(phase)),
            'neck': ((0,1,0), .6*math.sin(phase+.4)),
            'head': ((0,1,0), 1.5*math.sin(phase+.3)),
            'clavicle_L': ((0,1,0), 4+1.2*math.sin(phase)),
            'clavicle_R': ((0,1,0), -4-1.2*math.sin(phase)),
            'upperarm_L': ((0,1,0), 58+2.2*math.sin(phase)),
            'upperarm_R': ((0,1,0), -58-2.2*math.sin(phase)),
            'forearm_L': ((0,1,0), -12+1.1*math.sin(phase+.7)),
            'forearm_R': ((0,1,0), 12-1.1*math.sin(phase+.7)),
            'cape_upper': ((1,0,0), .8*math.sin(phase+.5)),
            'cape_lower': ((1,0,0), 1.2*math.sin(phase+.8)),
        }
        for name,(axis,ang) in values.items():
            p=arm.pose.bones[name]
            rotation(p,axis,ang)
            p.keyframe_insert(data_path='rotation_quaternion',frame=frame)
    # Cyclic action controls keep interpolation looping through frame 61.
    scene.frame_set(1)
    return action


def metrics(body, arm):
    sums=[]; counts=[]; no_weight=0
    for v in body.data.vertices:
        w=[a.weight for a in v.groups if a.weight>1e-5]
        sums.append(sum(w)); counts.append(len(w))
        if not w: no_weight+=1
    frame_data={}
    loop_samples={}
    for frame in (1,16,31,46,61):
        bpy.context.scene.frame_set(frame)
        deps=bpy.context.evaluated_depsgraph_get()
        ev=body.evaluated_get(deps)
        mesh=ev.to_mesh()
        coords=[ev.matrix_world @ v.co for v in mesh.vertices]
        frame_data[str(frame)]={
            'min_z_m':min(p.z for p in coords), 'max_z_m':max(p.z for p in coords),
            'bbox_x_m':[min(p.x for p in coords),max(p.x for p in coords)],
            'all_finite':all(math.isfinite(c) for p in coords for c in p),
        }
        if frame in (1,61):
            loop_samples[frame]=coords
        ev.to_mesh_clear()
    bpy.context.scene.frame_set(1)
    return {
        'mesh_vertices':len(body.data.vertices), 'triangles':len(body.data.polygons),
        'bone_count':len(arm.data.bones), 'bones':[b.name for b in arm.data.bones],
        'weight_sum_min':min(sums),'weight_sum_max':max(sums),
        'max_influences':max(counts),'unweighted_vertices':no_weight,
        'animation':'HeroicKnight_Clean_Idle','frames':[1,61],'fps':30,
        'sampled_frames':frame_data,
        'max_loop_vertex_drift_m':max((a-b).length for a,b in zip(loop_samples[1],loop_samples[61])),
    }


def roundtrip_report():
    # Import the actual exported FBX into a fresh scene, verifying the file on
    # disk rather than only Blender's in-memory source.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(OUTPUT_FBX))
    armatures=[o for o in bpy.data.objects if o.type=='ARMATURE']
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    image_names=[(i.name, i.has_data, bool(i.packed_file), i.filepath) for i in bpy.data.images]
    actions=[]
    for a in bpy.data.actions:
        actions.append({'name':a.name,'range':[float(v) for v in a.frame_range]})
    result={
        'armatures':len(armatures), 'meshes':len(meshes),
        'bone_count':len(armatures[0].data.bones) if armatures else 0,
        'skin_modifier_count':sum(sum(m.type=='ARMATURE' for m in o.modifiers) for o in meshes),
        'uv_layers':[layer.name for layer in meshes[0].data.uv_layers] if meshes else [],
        'actions':actions,
        'images':image_names,
        'missing_images':[i.name for i in bpy.data.images if not i.has_data],
    }
    assert result['armatures']==1 and result['meshes']==1, result
    assert result['bone_count']==24 and result['skin_modifier_count']==1, result
    assert len(result['uv_layers'])==1, result
    assert not result['missing_images'], result
    assert actions, result
    return result


def make_render(body, arm, file, view='front'):
    scene=bpy.context.scene
    scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x=720
    scene.render.resolution_y=720
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.film_transparent=False
    scene.world.color=(.20,.22,.26)
    scene.view_settings.view_transform='AgX'
    cam=bpy.data.objects.get('Rig_QA_Camera')
    if cam is None:
        cam_data=bpy.data.cameras.new('Rig_QA_Camera')
        cam=bpy.data.objects.new('Rig_QA_Camera',cam_data)
        scene.collection.objects.link(cam)
    scene.camera=cam
    cam.data.type='ORTHO'; cam.data.ortho_scale=2.55
    cam.location={'front':(0,-4,1.01),'back':(0,4,1.01),'side':(4,0,1.01)}[view]
    cam.rotation_euler=(Vector((0,0,.89))-cam.location).to_track_quat('-Z','Y').to_euler()
    light=bpy.data.objects.get('Rig_QA_Light')
    if light is None:
        d=bpy.data.lights.new('Rig_QA_Light','AREA')
        d.energy=1100; d.shape='DISK'; d.size=3
        light=bpy.data.objects.new('Rig_QA_Light',d)
        scene.collection.objects.link(light)
    light.location=(2,-3,4)
    light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
    arm.hide_render=True
    scene.render.filepath=str(file)
    bpy.ops.render.render(write_still=True)
    arm.hide_render=False


def render_bend_test(body, arm):
    scene=bpy.context.scene
    scene.frame_set(1)
    active_action=arm.animation_data.action
    arm.animation_data.action=None
    for p in arm.pose.bones:
        p.rotation_mode='QUATERNION'
        p.rotation_quaternion=(1,0,0,0)
    # Isolated QA pose: shoulder, elbow and knee bends can be judged visually.
    tests={
        'upperarm_L':((0,1,0),-32),
        'forearm_L':((0,1,0),-42),
        'upperarm_R':((0,1,0),32),
        'forearm_R':((0,1,0),42),
        'thigh_L':((1,0,0),18),
        'shin_L':((1,0,0),-32),
        'head':((0,1,0),12),
    }
    for name,(axis,ang) in tests.items():
        rotation(arm.pose.bones[name],axis,ang)
    make_render(body,arm,ROOT/'HeroicKnight_Clean_BendTest.png')
    make_render(body,arm,ROOT/'HeroicKnight_Clean_BendBack.png',view='back')
    make_render(body,arm,ROOT/'HeroicKnight_Clean_BendSide.png',view='side')
    for name in tests:
        rotation(arm.pose.bones[name],tests[name][0],0)
    arm.animation_data.action=active_action
    scene.frame_set(2)
    scene.frame_set(1)


def render_idle_preview():
    scene=bpy.context.scene
    previous=(scene.render.resolution_x,scene.render.resolution_y,scene.render.filepath)
    scene.render.resolution_x=360
    scene.render.resolution_y=360
    scene.render.image_settings.file_format='PNG'
    cam=scene.camera
    cam.location=(0,-4,1.01)
    cam.rotation_euler=(Vector((0,0,.89))-cam.location).to_track_quat('-Z','Y').to_euler()
    with tempfile.TemporaryDirectory(prefix='knight_idle_') as td:
        temp=Path(td)
        for index, frame in enumerate(range(1,61,2)):
            scene.frame_set(frame)
            scene.render.filepath=str(temp/f'{index:03d}.png')
            bpy.ops.render.render(write_still=True)
        # Blender portable build has still-image encoders only. System Python
        # provides Pillow for a compact, reviewable looping GIF.
        code=(
            'from pathlib import Path; from PIL import Image; import sys; '
            'files=sorted(Path(sys.argv[1]).glob("*.png")); '
            'frames=[Image.open(p).convert("RGB") for p in files]; '
            'frames[0].save(sys.argv[2],save_all=True,append_images=frames[1:],'
            'duration=67,loop=0,optimize=True)'
        )
        subprocess.run(['py','-3','-c',code,str(temp),str(ROOT/'HeroicKnight_Clean_Idle.gif')],check=True)
    (scene.render.resolution_x,scene.render.resolution_y,scene.render.filepath)=previous
    scene.frame_set(1)


def main():
    body=load_body()
    arm=make_armature()
    auto_skin(body,arm)
    make_render(body,arm,ROOT/'HeroicKnight_Clean_Rest.png')
    action=animate_idle(arm)
    report=metrics(body,arm)
    assert report['unweighted_vertices']==0, report
    assert report['max_influences']<=4, report
    assert report['weight_sum_min']>.999 and report['weight_sum_max']<1.001, report
    assert all(v['all_finite'] for v in report['sampled_frames'].values())
    assert report['max_loop_vertex_drift_m']<1e-5, report
    bpy.context.scene.frame_set(1)
    make_render(body,arm,ROOT/'HeroicKnight_Clean_IdlePose.png')
    render_bend_test(body,arm)
    render_idle_preview()
    # Save editable project with the idle action active, then export only rig+mesh.
    bpy.context.scene.frame_set(1)
    arm.animation_data.action=action
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True); arm.select_set(True)
    bpy.context.view_layer.objects.active=arm
    bpy.ops.export_scene.fbx(
        filepath=str(OUTPUT_FBX),use_selection=True,object_types={'ARMATURE','MESH'},
        add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',
        mesh_smooth_type='FACE',
        bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,
        bake_anim_simplify_factor=0.0,path_mode='COPY',embed_textures=True,
    )
    report['fbx_roundtrip']=roundtrip_report()
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('RIG_REPORT',json.dumps(report,ensure_ascii=False))
    print('RIG_OUTPUT',str(OUTPUT_FBX))


if __name__=='__main__':
    main()
