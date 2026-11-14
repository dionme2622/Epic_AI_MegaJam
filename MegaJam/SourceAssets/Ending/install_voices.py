"""Import the supplied Inworld voices and align audio and bilingual subtitle timing."""
from pathlib import Path
import math, wave, json
import unreal

root=Path(unreal.Paths.project_dir())/'SourceAssets'/'Ending'
seq=unreal.load_asset('/Game/DirectorCut/Ending/LS_BossEnding_Dialogue')
assert seq
rows=[]
starts=[14,130]
for name,start in zip(['S_Ending_Hero','S_Ending_Dragon'],starts):
    path=root/'Voice'/(name+'.wav')
    with wave.open(str(path),'rb') as w: duration=w.getnframes()/w.getframerate()
    task=unreal.AssetImportTask()
    task.filename=str(path); task.destination_path='/Game/DirectorCut/Ending/Voice'
    task.destination_name=name; task.automated=True; task.replace_existing=True; task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    sound=unreal.load_asset('/Game/DirectorCut/Ending/Voice/'+name)
    assert sound
    track=next((t for t in seq.get_tracks() if isinstance(t,unreal.MovieSceneAudioTrack) and str(t.get_display_name())==name),None)
    if track is None:
        track=seq.add_track(unreal.MovieSceneAudioTrack); track.set_display_name(name)
    for s in track.get_sections(): track.remove_section(s)
    section=track.add_section(); section.set_sound(sound)
    end=start+math.ceil(duration*24)
    section.set_range(start,end)
    rows.append({'name':name,'start_frame':start,'end_frame':end,'duration':duration})
end=rows[-1]['end_frame']+10
seq.set_playback_end(end)
for t in seq.get_tracks():
    if isinstance(t,unreal.MovieSceneCameraCutTrack):
        for s in t.get_sections(): s.set_end_frame(end)
for b in seq.get_bindings():
    for t in b.get_tracks():
        for s in t.get_sections():
            if s.get_end_frame()==240: s.set_end_frame(end)
controller=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='Ending_Controller')
for prop,val in {'HeroSubtitleStart':14/24,'HeroSubtitleEnd':rows[0]['end_frame']/24,'DragonSubtitleStart':130/24,'DragonSubtitleEnd':rows[1]['end_frame']/24}.items(): controller.set_editor_property(prop,val)
assert rows[0]['end_frame']<130
assert rows[-1]['end_frame']<end
assert unreal.EditorAssetLibrary.save_loaded_asset(seq)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(root/'Voice'/'timing.json').write_text(json.dumps({'fps':24,'dialogue_end_frame':end,'voices':rows},indent=2),encoding='utf8')
unreal.log('ENDING_VOICES_INSTALLED '+str(rows))
