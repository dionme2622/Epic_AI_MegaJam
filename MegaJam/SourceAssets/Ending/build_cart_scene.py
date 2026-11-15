"""Build a /-- launch ramp on the right of the original, level ending stage."""
from pathlib import Path
import json, math
import unreal

P = '/Game/DirectorCut/Ending/'
FPS, END = 24, 144
GROUND, RISE = 20.07, 360.0
LANE_Y, START_X = 3.5, 1165.85
RAMP_BOTTOM, RAMP_TOP, PLATFORM_END = 550.0, 1000.0, 1640.0
SLOPE = RISE / (RAMP_TOP - RAMP_BOTTOM)
ROOT = Path(unreal.Paths.project_dir()) / 'SourceAssets' / 'Ending'
lib = unreal.EditorAssetLibrary
ed = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if world.get_name() != 'L_BossEnding':
    assert ed.load_level(P + 'L_BossEnding')
actors = {a.get_actor_label(): a for a in sub.get_all_level_actors()}
controller = actors['Ending_Controller']
seq = unreal.load_asset(P + 'LS_BossEnding_Cart')
# Keep the sequence asset and its actor reference, removing all old stage animation.
for binding in list(seq.get_bindings()):
    binding.remove()
for track in list(seq.get_tracks()):
    seq.remove_track(track)
seq.delete_marked_frames()
seq.set_display_rate(unreal.FrameRate(FPS, 1))
seq.set_playback_start(0)
seq.set_playback_end(END)

# Restore only the stage/hero transforms changed by the previous revision.
baseline = json.loads((ROOT / 'stage_baseline.json').read_text(encoding='utf-8-sig'))
for row in baseline:
    actor = actors[row['label']]
    actor.set_actor_transform(unreal.Transform(location=unreal.Vector(*row['pos']),
        rotation=unreal.Rotator(pitch=row['rot'][0], yaw=row['rot'][1], roll=row['rot'][2]),
        scale=unreal.Vector(*row['scale'])), False, False)

cart = actors['Ending_Cart']
upper = actors['Ending Dragon Upper']
wheels = [actors['Ending_Cart_Wheel_' + str(i)] for i in range(1, 5)]
for actor in [cart, upper] + wheels:
    actor.detach_from_actor(unreal.DetachmentRule.KEEP_WORLD, unreal.DetachmentRule.KEEP_WORLD,
        unreal.DetachmentRule.KEEP_WORLD)
controller.set_editor_property('CartAccessories', wheels)
controller.set_editor_property('CartSceneActors', [])
for label, actor in actors.items():
    if label.startswith('Ending_CartScene_') and label not in ('Ending_CartScene_Rig', 'Ending_CartScene_Sequence'):
        sub.destroy_actor(actor)
rig = actors['Ending_CartScene_Rig']
rig.set_actor_transform(unreal.Transform(location=unreal.Vector(START_X, LANE_Y, GROUND + RISE)), False, False)
rig.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
cart.set_actor_transform(unreal.Transform(location=rig.get_actor_location(), rotation=unreal.Rotator(yaw=180),
    scale=unreal.Vector(3.4, 3.4, 3.4)), False, False)
for wheel, (x, y, z) in zip(wheels, [(-37.62,-35.64,17.5),(-37.62,35.64,17.5),(36.63,-34.32,17.5),(36.63,34.32,17.5)]):
    wheel.set_actor_transform(unreal.Transform(location=unreal.Vector(START_X-x*3.4, LANE_Y-y*3.4, GROUND+RISE+z*3.4),
        rotation=unreal.Rotator(yaw=180), scale=unreal.Vector(3.4,3.4,3.4)), False, False)
for actor in [cart, upper] + wheels:
    actor.attach_to_actor(rig, '', unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD,
        unreal.AttachmentRule.KEEP_WORLD, False)
wheel_local = [unreal.MathLibrary.make_relative_transform(w.get_actor_transform(), rig.get_actor_transform()) for w in wheels]
controller.set_editor_property('CartUpperTransform', unreal.Transform(
    location=unreal.Vector(1271.6, LANE_Y, GROUND+RISE+31.9*3.4-43.75*7.5+3),
    rotation=unreal.Rotator(yaw=180), scale=unreal.Vector(7.5,7.5,7.5)))

# A single solid wedge with a level top: /--, resting ON the original stage.
# No foreground lane, support columns, or lower road are added.
geometry = ROOT / 'Geometry'
geometry.mkdir(exist_ok=True)
obj = geometry / 'SM_Ending_Cart_StartRamp.obj'
profile = [(RAMP_BOTTOM, 0), (PLATFORM_END, 0), (PLATFORM_END, RISE), (RAMP_TOP, RISE)]
vertices = [(x-RAMP_TOP, y, z) for y in (-160,160) for x,z in profile]
faces = [(2,3,4,1),(8,7,6,5),(5,6,2,1),(6,7,3,2),(7,8,4,3),(8,5,1,4)]
lines = ['o SM_Ending_Cart_StartRamp', 's off'] + ['v %g %g %g' % v for v in vertices]
# Separate planar UVs keep the existing stone material at approximately its usual scale.
for face in faces:
    points = [vertices[i-1] for i in face]
    for x,y,z in points:
        u,v = ((x,z) if all(abs(p[1]-points[0][1])<.01 for p in points) else (x,y))
        if all(abs(p[0]-points[0][0])<.01 for p in points): u,v=y,z
        lines.append('vt %g %g' % (u/100, v/100))
for index,face in enumerate(faces):
    lines.append('f ' + ' '.join('%d/%d' % (v,index*4+i+1) for i,v in enumerate(face)))
obj.write_text('\n'.join(lines)+'\n', encoding='utf8')
mesh_path = P + 'Geometry/SM_Ending_Cart_StartRamp'
if True:  # Reimport so slope dimensions follow RISE on every rebuild.
    task = unreal.AssetImportTask()
    task.set_editor_property('filename', str(obj))
    task.set_editor_property('destination_path', P+'Geometry')
    task.set_editor_property('destination_name', 'SM_Ending_Cart_StartRamp')
    task.set_editor_property('automated', True)
    task.set_editor_property('save', True)
    task.set_editor_property('replace_existing', True)
    options = unreal.FbxImportUI()
    options.set_editor_property('import_materials', False)
    options.set_editor_property('import_textures', False)
    options.static_mesh_import_data.set_editor_property('combine_meshes', True)
    task.set_editor_property('options', options)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
mesh = unreal.load_asset(mesh_path)
assert mesh, 'Ramp mesh import failed'
ramp = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(RAMP_TOP,LANE_Y,GROUND), unreal.Rotator())
ramp.set_actor_label('Ending_CartScene_StartRamp')
ramp.static_mesh_component.set_static_mesh(mesh)
ramp.static_mesh_component.set_material(0, unreal.load_asset('/Game/DirectorCut/Environment/M_Castle_Wall'))
ramp.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
ramp.set_actor_hidden_in_game(True)
# Accessories follow the selected model's visibility immediately, including the reveal.
# The ramp is deliberately not attached to the moving cart rig.
controller.set_editor_property('CartAccessories', wheels+[ramp])
assert ramp.get_attach_parent_actor() is None


def transform(binding, values):
    section = binding.add_track(unreal.MovieScene3DTransformTrack).add_section()
    section.set_range(0, END)
    section.set_completion_mode(unreal.MovieSceneCompletionMode.KEEP_STATE)
    for frame,pos,rot,scale in values:
        for ch,val in zip(section.get_all_channels(), list(pos)+[rot[2],rot[0],rot[1]]+list(scale)):
            ch.add_key(unreal.FrameNumber(frame),float(val),interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
    return section


def road_height(x):
    return GROUND + max(0, min(RISE, (x-RAMP_BOTTOM)*SLOPE))

RADIUS = 59.5
# Height of a wheel centre tangent to the road, including both corners of the ramp.
def wheel_height(x):
    heights=[]
    for left,right,m,b in [(-1e6,RAMP_BOTTOM,0,GROUND),
            (RAMP_BOTTOM,RAMP_TOP,SLOPE,GROUND-SLOPE*RAMP_BOTTOM),
            (RAMP_TOP,1e6,0,GROUND+RISE)]:
        hit=max(left,min(right,x+m*RADIUS/math.sqrt(1+m*m)))
        if abs(hit-x)<=RADIUS:
            heights.append(m*hit+b+math.sqrt(max(0,RADIUS**2-(hit-x)**2)))
    return max(heights)

front,rear=-36.63*3.4,37.62*3.4

def cart_pose(x):
    def root_z(axle,theta):
        wx=x+axle*math.cos(theta)-RADIUS*math.sin(theta)
        return wheel_height(wx)-axle*math.sin(theta)-RADIUS*math.cos(theta)
    lo,hi=0,math.atan(SLOPE)
    for _ in range(40):
        angle=(lo+hi)/2
        if root_z(front,angle)>root_z(rear,angle):hi=angle
        else:lo=angle
    angle=(lo+hi)/2
    return (x,LANE_Y,(root_z(front,angle)+root_z(rear,angle))/2), math.degrees(angle)

rig_keys=[]
wheel_keys=[[] for _ in wheels]
travel=0
previous=None
for frame in range(END):
    t=max(0,min(frame/FPS-.75,5.75))
    u=max(0,t-1.7)
    distance=100*min(t,1.7)+100*u+450*u*u
    pos,pitch=cart_pose(START_X-distance)
    if previous:travel+=math.hypot(pos[0]-previous[0],pos[2]-previous[2])
    previous=pos
    rig_keys.append((frame,pos,(pitch,0,0),(1,1,1)))
    for i,local in enumerate(wheel_local):
        r=local.rotation.rotator()
        wheel_keys[i].append((frame,local.translation.to_tuple(),(r.pitch+math.degrees(travel/RADIUS),r.yaw,r.roll),local.scale3d.to_tuple()))
transform(seq.add_possessable(rig),rig_keys)
for wheel,values in zip(wheels,wheel_keys):transform(seq.add_possessable(wheel),values)

hero=actors['Ending Hero'];p=hero.get_actor_location().to_tuple();r=hero.get_actor_rotation();scale=hero.get_actor_scale3d().to_tuple()
hb=seq.add_possessable(hero)
transform(hb,[(0,p,(r.pitch,r.yaw,r.roll),scale),(82,p,(r.pitch,r.yaw,r.roll),scale),
    (90,p,(r.pitch,r.yaw+90,r.roll),scale),(98,p,(r.pitch,r.yaw+180,r.roll),scale),(END-1,p,(r.pitch,r.yaw+180,r.roll),scale)])
an=hb.add_track(unreal.MovieSceneSkeletalAnimationTrack).add_section();an.set_range(0,END)
an.params.set_editor_property('animation',unreal.load_asset('/Game/Assets/Knight/Anim/Crouch_Idle'))
cam=seq.add_possessable(actors['Ending Camera'])
# Match the reveal's final close shot exactly, then follow the descent toward the hero.
# Tracking stops on the hero instead of returning to the dragon or widening first.
ZOOM=(1120.0,2000.0,650.0)
camera_keys=[]
for frame,pos,_,_ in rig_keys:
    x,y,z=pos
    blend=max(0,min(1,(500-x)/390))
    blend=blend*blend*(3-2*blend)
    camera_y=2000-1000*blend
    camera_x=max(110,x-45.85)
    target_z=(z+ZOOM[2]-math.tan(math.radians(4))*ZOOM[1]-GROUND-RISE)*(1-blend)+110*blend
    camera_z=target_z+math.tan(math.radians(4))*camera_y
    if frame<=18:camera_x,camera_y,camera_z=ZOOM
    camera_keys.append((frame,(camera_x,camera_y,camera_z),(-4,-90,0),(1,1,1)))
transform(cam,camera_keys)
# Retain the dragon close-up through the end of the reveal so there is no hero detour.
reveal=controller.get_editor_property('RevealSequenceActor').get_sequence()
for binding in reveal.get_bindings():
    if binding.get_name()!='Ending Camera':continue
    for track in binding.get_tracks():
        if not isinstance(track,unreal.MovieScene3DTransformTrack):continue
        for section in track.get_sections():
            channels=section.get_all_channels()
            for channel in channels:
                for key in list(channel.get_keys()):channel.remove_key(key)
            for frame,position,rotation in [(0,(390,1150,245),(-2,-90,0)),
                    (36,ZOOM,(-4,-90,0)),(71,ZOOM,(-4,-90,0))]:
                for ch,val in zip(channels,list(position)+[rotation[2],rotation[0],rotation[1]]+[1,1,1]):
                    ch.add_key(unreal.FrameNumber(frame),float(val),interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
reveal.set_playback_end(72)
for binding in reveal.get_bindings():
    for track in binding.get_tracks():
        for section in track.get_sections():section.set_end_frame(72)
for track in reveal.get_tracks():
    for section in track.get_sections():section.set_end_frame(72)
reveal.delete_marked_frames()
for frame,label in [(0,'Reveal starts'),(36,'Dragon close-up'),(71,'Continue directly into selected branch')]:
    reveal.add_marked_frame(unreal.MovieSceneMarkedFrame(frame_number=unreal.FrameNumber(frame),label=label))
assert lib.save_loaded_asset(reveal)
assert camera_keys[0][1]==ZOOM
assert all(camera_keys[i][1][0]>=camera_keys[i+1][1][0]-.001 for i in range(END-1))
cut=seq.add_track(unreal.MovieSceneCameraCutTrack).add_section();cut.set_range(0,END)
bid=unreal.MovieSceneObjectBindingID();bid.set_editor_property('guid',cam.get_id());cut.set_camera_binding_id(bid)
for frame,label in [(0,'Right-side /-- ramp; original bridge stays level'),(18,'Brakes line / start rolling'),
        (59,'Accelerate down the steep ramp'),(79,'Scream'),(108,'Pass hero on original flat stage'),(82,'Hero starts looking as dragon passes')]:
    seq.add_marked_frame(unreal.MovieSceneMarkedFrame(frame_number=unreal.FrameNumber(frame),label=label))
# Avoid saving the last scrubbed camera/hero pose into the opening map.
actors['Ending Camera'].set_actor_location(unreal.Vector(390,1150,245),False,False)
actors['Ending Camera'].set_actor_rotation(unreal.Rotator(pitch=-2,yaw=-90),False)
for row in baseline:
    actor=actors[row['label']]
    assert unreal.MathLibrary.vector_distance(actor.get_actor_location(),unreal.Vector(*row['pos']))<.01
    if 'Floor' in row['label'] or 'Slab' in row['label']:
        assert abs(actor.get_actor_rotation().pitch)<.001
assert not any('Floor' in b.get_name() or 'Slab' in b.get_name() or 'Collision' in b.get_name() for b in seq.get_bindings())
assert rig_keys[72][1][2]>rig_keys[96][1][2]+50
assert rig_keys[108][1][0]<110
assert rig_keys[END-1][1][0]<-2500
assert lib.save_loaded_asset(seq)
assert ed.save_current_level()
Path(unreal.Paths.project_saved_dir(),'cart_scene_build.json').write_text(json.dumps(dict(
    pass_checks=True,sequence=seq.get_path_name(),ramp=ramp.get_path_name(),stage_restored=len(baseline),
    ramp_bounds_x=[RAMP_BOTTOM,PLATFORM_END],ramp_lane_y=LANE_Y,rise=RISE,
    slope_degrees=math.degrees(math.atan(SLOPE)),existing_stage_tracks=0,
    ramp_visible_only_for_cart=True,camera_continuous_close_tracking=True,new_voice_tracks=2),indent=2),encoding='utf8')
unreal.log('CART_RIGHT_RAMP_BUILD_PASS')

voice_installer=ROOT/'install_cart_voices.py'
if voice_installer.exists():
    exec(compile(voice_installer.read_text(encoding='utf-8-sig'),str(voice_installer),'exec'))

fade_installer=Path(unreal.Paths.project_dir())/"SourceAssets"/"Ending"/"configure_branch_fades.py"
exec(compile(fade_installer.read_text(encoding="utf-8-sig"),str(fade_installer),"exec"))
