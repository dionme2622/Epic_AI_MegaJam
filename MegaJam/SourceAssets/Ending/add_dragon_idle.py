"""Update the existing dialogue sequence without rebuilding the ending map."""
import unreal
ed=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert ed.load_level('/Game/DirectorCut/Ending/L_BossEnding')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
upper=next(a for a in actors if a.get_actor_label()=='Ending Dragon Upper')
seq=unreal.load_asset('/Game/DirectorCut/Ending/LS_BossEnding_Dialogue')
idle=unreal.load_asset('/Game/DirectorCut/Stage1/RideCart/A_Dragon_Cart_Breathe')
assert seq and idle
binding=next((b for b in seq.get_bindings() if b.get_name()==upper.get_actor_label()),None)
if binding is None: binding=seq.add_possessable(upper)
for track in binding.get_tracks():
    if isinstance(track,unreal.MovieSceneSkeletalAnimationTrack): binding.remove_track(track)
section=binding.add_track(unreal.MovieSceneSkeletalAnimationTrack).add_section()
section.set_range(0,seq.get_playback_end())
section.params.set_editor_property('animation',idle)
section.set_completion_mode(unreal.MovieSceneCompletionMode.RESTORE_STATE)
assert unreal.EditorAssetLibrary.save_loaded_asset(seq)
assert section.params.animation==idle
assert section.get_start_frame()==0 and section.get_end_frame()==240
unreal.log('ENDING_IDLE_UPDATE_PASS')

