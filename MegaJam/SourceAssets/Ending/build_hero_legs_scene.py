"""Hero's legs branch: a rapid little-leg entrance, then the hero's question."""
from pathlib import Path
import unreal, math, json
P='/Game/DirectorCut/Ending/'
FPS,END=24,168
lib=unreal.EditorAssetLibrary
ed=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if world.get_name()!='L_BossEnding':assert ed.load_level(P+'L_BossEnding')
actors={a.get_actor_label():a for a in sub.get_all_level_actors()}
ctrl=actors['Ending_Controller'];legs=actors['Ending_Hero_Legs'];hero=actors['Ending Hero'];camera=actors['Ending Camera']
assert hasattr(unreal.DirectorCutEnding,'build_hero_legs_scurry_animation'), 'Compile the updated ending controller first'
walk=unreal.DirectorCutEnding.build_hero_legs_scurry_animation()
assert walk
walk.set_editor_property('rate_scale',1.2)
assert lib.save_loaded_asset(walk)
path=P+'LS_BossEnding_HeroLegs'
seq=unreal.load_asset(path)
if not seq:seq=unreal.AssetToolsHelpers.get_asset_tools().create_asset('LS_BossEnding_HeroLegs',P,unreal.LevelSequence,unreal.LevelSequenceFactoryNew())
for b in list(seq.get_bindings()):b.remove()
for t in list(seq.get_tracks()):seq.remove_track(t)
seq.set_display_rate(unreal.FrameRate(FPS,1));seq.set_playback_start(0);seq.set_playback_end(END);seq.delete_marked_frames()
# Only the small legs are attached in the saved map. The controller attaches the
# upper body to the selected model's rig when the player makes the choice.
rig=actors.get('Ending_HeroLegs_Rig')
if not rig:
    rig=sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(1165.85,3.5,20.07),unreal.Rotator())
    rig.set_actor_label('Ending_HeroLegs_Rig')
rig.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
rig.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
rig.set_actor_transform(unreal.Transform(location=unreal.Vector(1165.85,3.5,20.07)),False,False)
legs.detach_from_actor(unreal.DetachmentRule.KEEP_WORLD,unreal.DetachmentRule.KEEP_WORLD,unreal.DetachmentRule.KEEP_WORLD)
legs.set_actor_transform(unreal.Transform(location=rig.get_actor_location(),rotation=unreal.Rotator(yaw=90),scale=unreal.Vector(4.1,4.1,4.1)),False,False)
legs.attach_to_actor(rig,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
legs.skeletal_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
legs.skeletal_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
legs.set_actor_hidden_in_game(True)
ctrl.set_editor_property('HeroUpperTransform',unreal.Transform(location=unreal.Vector(1271.6,3.5,20.07+40.5*4.1-43.75*7.5+3),rotation=unreal.Rotator(yaw=180),scale=unreal.Vector(7.5,7.5,7.5)))

def transform(binding,keys):
    section=binding.add_track(unreal.MovieScene3DTransformTrack).add_section()
    section.set_range(0,END);section.set_completion_mode(unreal.MovieSceneCompletionMode.KEEP_STATE)
    for f,pos,rot,scale in keys:
        for ch,v in zip(section.get_all_channels(),list(pos)+[rot[2],rot[0],rot[1]]+list(scale)):
            ch.add_key(unreal.FrameNumber(f),float(v),interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
    return section

keys=[]
for frame in range(END):
    progress=max(0,min(1,(frame-12)/60))
    moving=12<frame<72
    bob=0.0  # Footfall motion comes from the legs, not whole-body shaking.
    keys.append((frame,(1165.85-515.85*progress,3.5,20.07+bob),(0,0,0),(1,1,1)))
transform(seq.add_possessable(rig),keys)
lb=seq.add_possessable(legs)
track=lb.add_track(unreal.MovieSceneSkeletalAnimationTrack)
for start,end,hold in [(0,12,True),(12,72,False),(72,END,True)]:
    section=track.add_section();section.set_range(start,end)
    section.set_completion_mode(unreal.MovieSceneCompletionMode.KEEP_STATE)
    params=section.get_editor_property('params');params.animation=walk
    if hold:
        # Freeze the full animation at time zero; never loop a one-frame slice.
        params.play_rate=unreal.MovieSceneTimeWarpExtensions.make_time_warp(0.0)
    section.set_editor_property('params',params)
hb=seq.add_possessable(hero)
an=hb.add_track(unreal.MovieSceneSkeletalAnimationTrack).add_section();an.set_range(0,END)
an.params.set_editor_property('animation',unreal.load_asset('/Game/Assets/Knight/Anim/Crouch_Idle'))
# Stay on the tiny legs during the walk, then include the hero's baffled reaction.
cam=seq.add_possessable(camera)
transform(cam,[(0,(1120,2000,650),(-4,-90,0),(1,1,1)),(12,(1120,2000,650),(-4,-90,0),(1,1,1)),
    (48,(800,1850,450),(-4,-90,0),(1,1,1)),(72,(490,1700,340),(-4,-90,0),(1,1,1)),
    (84,(400,1500,290),(-3,-90,0),(1,1,1)),(167,(400,1500,290),(-3,-90,0),(1,1,1))])
cut=seq.add_track(unreal.MovieSceneCameraCutTrack).add_section();cut.set_range(0,END)
bid=unreal.MovieSceneObjectBindingID();bid.set_editor_property('guid',cam.get_id());cut.set_camera_binding_id(bid)
for frame,label in [(0,"Hero's legs only"),(12,'Smooth walk / 1.2x playback'),(72,'Stop beside hero'),
    (84,'Hero: 왜 내 다리가 저기 있는거야? / Why are my legs over there?'),(156,'Reaction hold')]:
    seq.add_marked_frame(unreal.MovieSceneMarkedFrame(frame_number=unreal.FrameNumber(frame),label=label))
sa=ctrl.get_editor_property('HeroLegsSequenceActor')
if not sa:
    sa=sub.spawn_actor_from_class(unreal.LevelSequenceActor,unreal.Vector());sa.set_actor_label('Ending_HeroLegs_Sequence')
sa.set_sequence(seq)
settings=sa.get_editor_property('playback_settings');settings.auto_play=False;settings.pause_at_end=False
settings.finish_completion_state_override=unreal.MovieSceneCompletionModeOverride.FORCE_KEEP_STATE
sa.set_editor_property('playback_settings',settings)
ctrl.set_editor_property('HeroLegsSequenceActor',sa)
lib.set_metadata_tag(seq,'Branch',"Hero's Legs / rapid little-leg walk / hero reaction")
lib.set_metadata_tag(seq,'Dialogue','왜 내 다리가 저기 있는거야? / Why are my legs over there?')
assert not any(isinstance(t,unreal.MovieSceneAudioTrack) for t in seq.get_tracks())
assert lib.save_loaded_asset(seq)
assert ed.save_current_level()
Path(unreal.Paths.project_saved_dir(),'hero_legs_build.json').write_text(json.dumps(dict(sequence=path,frames=END,walk_frames=[12,72],
    subtitle_frames=[84,156],animation=walk.get_path_name(),rig=rig.get_path_name(),new_voice_tracks=0),indent=2),encoding='utf8')
unreal.log('HERO_LEGS_BUILD_PASS')

voice_installer=Path(unreal.Paths.project_dir())/"SourceAssets"/"Ending"/"install_hero_legs_voices.py"
if voice_installer.exists() and (voice_installer.parent/"Voice"/"S_HeroLegs_Hero.wav").exists():
    exec(compile(voice_installer.read_text(encoding="utf-8-sig"),str(voice_installer),"exec"))

fade_installer=Path(unreal.Paths.project_dir())/"SourceAssets"/"Ending"/"configure_branch_fades.py"
exec(compile(fade_installer.read_text(encoding="utf-8-sig"),str(fade_installer),"exec"))
