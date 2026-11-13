import unreal
from pathlib import Path

P='/Game/Assets/Prologue/'
level_path=P+'L_Prologue_LastBattle'
seq_path=P+'LS_Prologue_LastBattle_v4'
assets=unreal.AssetToolsHelpers.get_asset_tools()
editor=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not unreal.EditorAssetLibrary.does_asset_exist(level_path):
    assert editor.new_level(level_path)
else:
    assert editor.load_level(level_path)
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    unreal.EditorLevelLibrary.destroy_actor(actor)

castle=unreal.load_asset(P+'SM_Prologue_Castle')
knight_mesh=unreal.load_asset('/Game/Assets/Knight_Combat_New/Knight_New_Combat_Idle')
knight_anim=unreal.load_asset('/Game/Assets/Knight_Combat_New/Knight_New_Combat_Idle_Anim')
cube=unreal.load_asset('/Engine/BasicShapes/Cube')
plane=unreal.load_asset('/Engine/BasicShapes/Plane')
assert all((castle,knight_mesh,knight_anim,cube,plane))

def static(label,mesh,loc,scale=(1,1,1),rot=(0,0,0)):
    a=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*loc),unreal.Rotator(*rot))
    a.set_actor_label(label);a.static_mesh_component.set_static_mesh(mesh)
    a.set_actor_scale3d(unreal.Vector(*scale));return a

stage=static('Toy_Castle_Stage',castle,(0,0,0))
hero=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector(-240,-170,0),unreal.Rotator(0,20,0))
hero.set_actor_label('Hero_Victor');hc=hero.skeletal_mesh_component;hc.set_skeletal_mesh_asset(knight_mesh)
hc.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE);hc.set_animation(knight_anim)
dragon=static('Dragon_Upper_Body_Cube',cube,(180,40,90),(2.5,2.1,1.8))
dragon.set_actor_rotation(unreal.Rotator(0,180,0),False)
note=static('Developer_Note',cube,(390,80,95),(.12,1.8,1.3))
storage=static('Lower_Body_Storage_Sign',cube,(480,580,300),(.1,2.6,.8))
light=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,500),unreal.Rotator(-45,-30,0))
light.set_actor_label('Warm_Stage_Light')
fill=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,300))
fill.set_actor_label('Castle_Fill_Light')

camera=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CineCameraActor,unreal.Vector(-700,-1250,390),unreal.Rotator(-12,58,0))
camera.set_actor_label('Prologue_Camera')
camera.get_cine_camera_component().set_editor_property('current_focal_length',35.0)

seq=assets.create_asset('LS_Prologue_LastBattle_v4',P,unreal.LevelSequence,unreal.LevelSequenceFactoryNew())
seq.set_display_rate(unreal.FrameRate(30,1));seq.set_playback_start(0);seq.set_playback_end(1800)

def binding(actor): return seq.add_possessable(actor)
cb=binding(camera);hb=binding(hero);db=binding(dragon)
binding(stage);binding(note);binding(storage)
cam_track=cb.add_track(unreal.MovieScene3DTransformTrack)
cam_section=cam_track.add_section();cam_section.set_range(0,1800)
def key_transform(section,frame,loc=None,rot=None):
    channels=section.get_all_channels()
    values=list(loc or (0,0,0))+list(rot or (0,0,0))
    for i,v in enumerate(values):channels[i].add_key(unreal.FrameNumber(frame),float(v))
for f,loc,rot in [
    (0,(-700,-1250,390),(-12,58,0)),
    (360,(-500,-1100,350),(-10,65,0)),
    (720,(-350,-850,310),(-9,78,0)),
    (1050,(-60,-770,300),(-8,89,0)),
    (1450,(150,-550,260),(-8,110,0)),
    (1800,(220,-280,240),(-7,125,0))]:key_transform(cam_section,f,loc,rot)

def actor_transform_track(bind,frames):
    t=bind.add_track(unreal.MovieScene3DTransformTrack);s=t.add_section();s.set_range(0,1800)
    for f,loc,rot in frames:key_transform(s,f,loc,rot)
actor_transform_track(hb,[(0,(-240,-170,0),(0,20,0)),(210,(-140,-170,0),(0,20,0)),(390,(-700,-150,0),(0,20,0)),(1800,(-700,-150,0),(0,20,0))])
actor_transform_track(db,[(0,(180,40,90),(0,180,0)),(390,(180,40,90),(0,180,0)),(530,(180,40,90),(-20,180,0)),(1300,(180,40,90),(-20,180,0)),(1800,(330,480,90),(-20,140,0))])

cam_cut=seq.add_track(unreal.MovieSceneCameraCutTrack)
cut=cam_cut.add_section();cut.set_range(0,1800)
bid=unreal.MovieSceneObjectBindingID();bid.set_editor_property('guid',cb.get_id())
cut.set_camera_binding_id(bid)

anim_track=hb.add_track(unreal.MovieSceneSkeletalAnimationTrack)
anim_section=anim_track.add_section();anim_section.set_range(0,390)
anim_section.params.set_editor_property('animation',knight_anim)

unreal.EditorAssetLibrary.save_loaded_asset(seq)
unreal.EditorLevelLibrary.save_current_level()
unreal.log('PROLOGUE_BASE_OK '+level_path+' '+seq_path)
