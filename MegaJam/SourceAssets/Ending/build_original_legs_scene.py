"""Append the original-legs gag without rebuilding the existing choice, voices or models."""
from pathlib import Path
import json
import unreal

P='/Game/DirectorCut/Ending/'
lib=unreal.EditorAssetLibrary
ed=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert ed.load_level(P+'L_BossEnding')
sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors={a.get_actor_label():a for a in sub.get_all_level_actors()}
controller=actors['Ending_Controller']; dragon=actors['Ending_Dragon_Original']
camera=actors['Ending Camera']; hero=actors['Ending Hero']
old=controller.get_editor_property('OriginalLegsSequenceActor')
if old:
    controller.set_editor_property('OriginalLegsSequenceActor',None)
    sub.destroy_actor(old)
path=P+'LS_BossEnding_OriginalLegs'
if lib.does_asset_exist(path): assert lib.delete_asset(path)
walk=unreal.DirectorCutEnding.build_awkward_walk_animation()
assert walk
assert lib.save_loaded_asset(walk)
seq=unreal.AssetToolsHelpers.get_asset_tools().create_asset('LS_BossEnding_OriginalLegs',P,unreal.LevelSequence,unreal.LevelSequenceFactoryNew())
seq.set_display_rate(unreal.FrameRate(24,1)); seq.set_playback_start(0);seq.set_playback_end(324)

def transform(binding,keys):
    section=binding.add_track(unreal.MovieScene3DTransformTrack).add_section()
    section.set_range(0,324); section.set_completion_mode(unreal.MovieSceneCompletionMode.KEEP_STATE)
    channels=section.get_all_channels()
    for frame,loc,rot,scale in keys:
        for ch,val in zip(channels,list(loc)+[rot[2],rot[0],rot[1]]+[scale]*3):
            ch.add_key(unreal.FrameNumber(frame),float(val),interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)

cam=seq.add_possessable(camera)
transform(cam,[(0,(390,1150,245),(-2,-90,0),1),
    (30,(760,2450,470),(-3,-90,0),1), (144,(710,2450,470),(-3,-90,0),1),
    (323,(710,2450,470),(-3,-90,0),1)])
cut=seq.add_track(unreal.MovieSceneCameraCutTrack).add_section(); cut.set_range(0,324)
bid=unreal.MovieSceneObjectBindingID();bid.set_editor_property('guid',cam.get_id());cut.set_camera_binding_id(bid)
db=seq.add_possessable(dragon)
keys=[(0,(1271.6,3.5,20.07),(0,180,0),7.5),(36,(1271.6,3.5,20.07),(0,180,0),7.5)]
# Short shuffles separated by conspicuous holds; the rig's knees stay rigid.
for f,x,z,roll in [(45,1271.6,20.07,0),(50,1200,24,1),(62,1200,24,1),
    (69,1140,20.07,-1),(80,1140,20.07,-1),(89,1050,25,1.2),
    (102,1050,25,1.2),(109,1000,20.07,-1),(123,1000,20.07,-1),
    (130,915,24,.8),(139,915,24,.8),(144,870,20.07,0),(323,870,20.07,0)]:
    keys.append((f,(x,3.5,z),(0,180,roll),7.5))
transform(db,keys)
animtrack=db.add_track(unreal.MovieSceneSkeletalAnimationTrack)
for start,end,hold in [(0,36,True),(36,144,False),(144,324,True)]:
    s=animtrack.add_section();s.set_range(start,end);s.set_completion_mode(unreal.MovieSceneCompletionMode.KEEP_STATE)
    params=s.get_editor_property('params');params.animation=walk
    if hold:
        rate=seq.get_tick_resolution()
        params.end_frame_offset=unreal.FrameNumber(round(47/24*rate.numerator/rate.denominator))
    s.set_editor_property('params',params)
hb=seq.add_possessable(hero)
s=hb.add_track(unreal.MovieSceneSkeletalAnimationTrack).add_section();s.set_range(0,324)
s.params.set_editor_property('animation',unreal.load_asset('/Game/Assets/Knight/Anim/Crouch_Idle'))
for frame,label in [(0,'Original dragon legs only / NO VOICE'),(36,'Stiff knees / uneven shuffles'),
    (144,'Stop / awkward pause'),(156,'Hero: ...Have you always walked like that?'),
    (228,"Dragon: Sigh... What's wrong with the animation now?"),(300,'Hold for future scene')]:
    seq.add_marked_frame(unreal.MovieSceneMarkedFrame(frame_number=unreal.FrameNumber(frame),label=label))
sa=sub.spawn_actor_from_class(unreal.LevelSequenceActor,unreal.Vector())
sa.set_actor_label('Ending_OriginalLegs_Sequence');sa.set_sequence(seq)
settings=sa.get_editor_property('playback_settings');settings.auto_play=False;settings.pause_at_end=False
settings.finish_completion_state_override=unreal.MovieSceneCompletionModeOverride.FORCE_KEEP_STATE
sa.set_editor_property('playback_settings',settings)
controller.set_editor_property('OriginalLegsSequenceActor',sa)
lib.set_metadata_tag(seq,'Branch','Original Dragon Legs only')
lib.set_metadata_tag(seq,'Dialogue','KR + EN subtitles only; audio reserved for later')
assert lib.save_loaded_asset(seq)
assert ed.save_current_level()
Path(unreal.Paths.project_saved_dir(),'original_legs_build.json').write_text(json.dumps({'sequence':path,'animation':walk.get_path_name(),'frames':324,'fps':24,'hero_subtitle':[156,216],'dragon_subtitle':[228,300],'new_voice_tracks':0},indent=2),encoding='utf8')
unreal.log('ORIGINAL_LEGS_BUILD_PASS')
voice_script=Path(unreal.Paths.project_dir())/'SourceAssets'/'Ending'/'install_original_legs_voices.py'
if voice_script.exists() and (voice_script.parent/'Voice'/'S_OriginalLegs_Hero.wav').exists():
    exec(compile(voice_script.read_text(encoding='utf-8-sig'),str(voice_script),'exec'),{'__name__':'__main__'})

fade_installer=Path(unreal.Paths.project_dir())/"SourceAssets"/"Ending"/"configure_branch_fades.py"
exec(compile(fade_installer.read_text(encoding="utf-8-sig"),str(fade_installer),"exec"))
