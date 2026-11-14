"""Build the accelerating cart branch; keep the other ending branches intact."""
from pathlib import Path
import json, math
import unreal

P='/Game/DirectorCut/Ending/'
FPS=24
END=240
GROUND=20.07
ed=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert ed.load_level(P+'L_BossEnding')
sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lib=unreal.EditorAssetLibrary
actors={a.get_actor_label():a for a in sub.get_all_level_actors()}
controller=actors['Ending_Controller']
cart=actors['Ending_Cart']; upper=actors['Ending Dragon Upper']
wheels=[actors['Ending_Cart_Wheel_'+str(i)] for i in range(1,5)]
camera=actors['Ending Camera'];hero=actors['Ending Hero']
children=[cart,upper]+wheels
# Re-running this script never leaves nested rigs or duplicate ramps.
for a in children:
    if a.get_attach_parent_actor() and a.get_attach_parent_actor().get_actor_label()=='Ending_CartScene_Rig':
        a.detach_from_actor(unreal.DetachmentRule.KEEP_WORLD,unreal.DetachmentRule.KEEP_WORLD,unreal.DetachmentRule.KEEP_WORLD)
# A foreground lane descends ahead of the existing flat starting mark.
# This leaves the hero's original stage and all other model options in place.
LANE_Y=320.0
dy=LANE_Y-cart.get_actor_location().y
for a in [cart]+wheels:
    loc=a.get_actor_location();loc.y+=dy;a.set_actor_location(loc,False,False)
upper_cart=controller.get_editor_property('CartUpperTransform')
pos=upper_cart.translation;pos.y=LANE_Y;upper_cart.translation=pos
controller.set_editor_property('CartUpperTransform',upper_cart)
controller.set_editor_property('CartSequenceActor',None)
controller.set_editor_property('CartSceneActors',[])
for label,a in actors.items():
    if label.startswith('Ending_CartScene_'): sub.destroy_actor(a)
path=P+'LS_BossEnding_Cart'
if lib.does_asset_exist(path):assert lib.delete_asset(path)

rig=sub.spawn_actor_from_class(unreal.StaticMeshActor,cart.get_actor_location(),unreal.Rotator())
rig.set_actor_label('Ending_CartScene_Rig')
rig.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
rig.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
for a in children:
    a.attach_to_actor(rig,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
wheel_local=[unreal.MathLibrary.make_relative_transform(a.get_actor_transform(),rig.get_actor_transform()) for a in wheels]

cube=unreal.load_asset('/Engine/BasicShapes/Cube')
stone=unreal.load_asset('/Game/DirectorCut/Environment/M_Castle_Wall')
assert cube and stone
scenery=[]
slope=.3
angle=math.degrees(math.atan(slope))
def block(label,loc,scale,pitch=0):
    a=sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*loc),unreal.Rotator(pitch=pitch,yaw=0,roll=0))
    a.set_actor_label('Ending_CartScene_'+label)
    a.static_mesh_component.set_static_mesh(cube)
    a.static_mesh_component.set_material(0,stone)
    a.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    a.set_actor_scale3d(unreal.Vector(*scale))
    a.set_actor_hidden_in_game(False);a.set_is_temporarily_hidden_in_editor(False)
    scenery.append(a)
    return a

def road_height(x):return GROUND-slope*max(0,min(900-x,600))
# /-- in side view: flat on the right, downhill ahead to the left.
# Geometry is persistent from the opening, rather than appearing at the branch cut.
block('FlatStart',(1250,200,GROUND-9),(7,6,.18))
for i in range(6):
    x=350+i*100;height=road_height(x)
    block('Ramp_'+str(i+1),(x,LANE_Y,height-6/math.cos(math.atan(slope))),(1.07,3.6,.12),angle)
for i,x in enumerate([400,600,800,1100,1400],1):
    bottom=-220;top=road_height(x)-15
    block('Support_'+str(i),(x,LANE_Y,(bottom+top)/2),(.60,3.1,(top-bottom)/100))
for i in range(22):
    block('LowerRoad_'+str(i+1),(250-i*100,LANE_Y,road_height(300)-12),(1.01,3.6,.24))

seq=unreal.AssetToolsHelpers.get_asset_tools().create_asset('LS_BossEnding_Cart',P,unreal.LevelSequence,unreal.LevelSequenceFactoryNew())
seq.set_display_rate(unreal.FrameRate(FPS,1));seq.set_playback_start(0);seq.set_playback_end(END)
def transform(binding,keys):
    s=binding.add_track(unreal.MovieScene3DTransformTrack).add_section()
    s.set_range(0,END);s.set_completion_mode(unreal.MovieSceneCompletionMode.KEEP_STATE)
    for frame,pos,rot,scale in keys:
        values=list(pos)+[rot[2],rot[0],rot[1]]+list(scale)
        for ch,value in zip(s.get_all_channels(),values):
            ch.add_key(unreal.FrameNumber(frame),float(value),interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
    return s

rig_binding=seq.add_possessable(rig)
rig_keys=[];wheel_keys=[[] for _ in wheels]
radius=17.5*3.4
for frame in range(0,END,3):
    t=min(frame/FPS,7.25)
    flat_distance=cart.get_actor_location().x-900
    flat_speed=flat_distance/2.5
    distance=flat_speed*t if t<=2.5 else flat_distance+flat_speed*(t-2.5)+110*(t-2.5)**2
    x=cart.get_actor_location().x-distance
    z=road_height(x)
    pitch=angle*max(0,min((900-x)/70,(x-300)/70,1))
    rig_keys.append((frame,(x,LANE_Y,z),(pitch,0,0),(1,1,1)))
    wheel_angle=math.degrees(distance/radius)
    for i,local in enumerate(wheel_local):
        rot=local.rotation.rotator()
        wheel_keys[i].append((frame,local.translation.to_tuple(),(rot.pitch+wheel_angle,rot.yaw,rot.roll),local.scale3d.to_tuple()))
# Include the exclusive final hold frame explicitly.
rig_keys.append((END-1,rig_keys[-1][1],rig_keys[-1][2],(1,1,1)))
transform(rig_binding,rig_keys)
for a,keys in zip(wheels,wheel_keys):
    keys.append((END-1,keys[-1][1],keys[-1][2],keys[-1][3]))
    transform(seq.add_possessable(a),keys)

cam=seq.add_possessable(camera)
transform(cam,[(0,(760,2600,350),(-3,-90,0),(1,1,1)),
    (84,(760,2600,350),(-3,-90,0),(1,1,1)),
    (132,(300,2400,300),(-4,-90,0),(1,1,1)),
    (168,(110,850,165),(-5,-90,0),(1,1,1)),
    (239,(110,850,165),(-5,-90,0),(1,1,1))])
cut=seq.add_track(unreal.MovieSceneCameraCutTrack).add_section();cut.set_range(0,END)
bid=unreal.MovieSceneObjectBindingID();bid.set_editor_property('guid',cam.get_id());cut.set_camera_binding_id(bid)

hb=seq.add_possessable(hero)
p=hero.get_actor_location().to_tuple();r=hero.get_actor_rotation();scale=hero.get_actor_scale3d().to_tuple()
transform(hb,[(0,p,(r.pitch,r.yaw,r.roll),scale),(144,p,(r.pitch,r.yaw,r.roll),scale),
    (156,p,(r.pitch,r.yaw+90,r.roll),scale),(168,p,(r.pitch,r.yaw+180,r.roll),scale),
    (239,p,(r.pitch,r.yaw+180,r.roll),scale)])
s=hb.add_track(unreal.MovieSceneSkeletalAnimationTrack).add_section();s.set_range(0,END)
s.params.set_editor_property('animation',unreal.load_asset('/Game/Assets/Knight/Anim/Crouch_Idle'))
for f,label in [(0,'Cart only / downhill ramp'),(18,'Dragon: Wait. Where are the brakes on this—'),
    (79,'Dragon: Aaaah!!!'),(108,'Cart passes hero / increasing speed'),
    (144,'Hero turns AFTER cart passes'),(168,'Look back / hold reaction')]:
    seq.add_marked_frame(unreal.MovieSceneMarkedFrame(frame_number=unreal.FrameNumber(f),label=label))
sa=sub.spawn_actor_from_class(unreal.LevelSequenceActor,unreal.Vector())
sa.set_actor_label('Ending_CartScene_Sequence');sa.set_sequence(seq)
settings=sa.get_editor_property('playback_settings');settings.auto_play=False;settings.pause_at_end=False
settings.finish_completion_state_override=unreal.MovieSceneCompletionModeOverride.FORCE_KEEP_STATE
sa.set_editor_property('playback_settings',settings)
controller.set_editor_property('CartSequenceActor',sa)
controller.set_editor_property('CartSceneActors',[])
# The preview already shows the same flat-to-downhill road before the action starts.
reveal=controller.get_editor_property('RevealSequenceActor').get_sequence()
for b in reveal.get_bindings():
    if b.get_name()!='Ending Camera':continue
    for tr in b.get_tracks():
        if isinstance(tr,unreal.MovieScene3DTransformTrack):
            for sec in tr.get_sections():
                for i,ch in enumerate(sec.get_all_channels()):
                    for key in ch.get_keys():
                        if key.get_time().frame_number.value in (36,72):
                            if i<3:key.set_value(float((1055,2450,430)[i]))
assert lib.save_loaded_asset(reveal)
lib.set_metadata_tag(seq,'Dialogue','KR + EN subtitles only; no voice')
lib.set_metadata_tag(seq,'Branch','Cart / accelerating roll / hero turns after pass; no chase')
assert not any(isinstance(t,unreal.MovieSceneAudioTrack) for t in seq.get_tracks())
assert lib.save_loaded_asset(seq)
assert ed.save_current_level()
Path(unreal.Paths.project_saved_dir(),'cart_scene_build.json').write_text(json.dumps({'sequence':path,'duration':END/FPS,
    'rig':rig.get_path_name(),'ramp_actors':len(scenery),'slope_degrees':angle,'subtitle_windows':[[.75,3.3],[3.3,5.75]],'new_voice_tracks':0},indent=2),encoding='utf8')
unreal.log('CART_SCENE_BUILD_PASS')
mode_script=Path(unreal.Paths.project_dir())/'SourceAssets'/'Ending'/'configure_cinematic_mode.py'
exec(compile(mode_script.read_text(encoding='utf-8-sig'),str(mode_script),'exec'),{'__name__':'__main__'})
