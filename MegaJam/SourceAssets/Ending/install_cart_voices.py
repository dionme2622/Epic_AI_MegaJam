"""Install supplied Hades cart dialogue and scream, preserving existing subtitles."""
import unreal, wave, math, json
from pathlib import Path
root=Path(unreal.Paths.project_dir())/'SourceAssets'/'Ending'
seq=unreal.load_asset('/Game/DirectorCut/Ending/LS_BossEnding_Cart')
rows=[]
for name,start in [('S_Ending_Cart_Brakes',18),('S_Ending_Cart_Scream',79)]:
    path=root/'Voice'/(name+'.wav')
    with wave.open(str(path),'rb') as wav:duration=wav.getnframes()/wav.getframerate()
    task=unreal.AssetImportTask()
    task.filename=str(path);task.destination_path='/Game/DirectorCut/Ending/Voice'
    task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    sound=unreal.load_asset('/Game/DirectorCut/Ending/Voice/'+name)
    assert sound
    track=next((t for t in seq.get_tracks() if isinstance(t,unreal.MovieSceneAudioTrack) and str(t.get_display_name())==name),None)
    if track is None:track=seq.add_track(unreal.MovieSceneAudioTrack);track.set_display_name(name)
    for section in list(track.get_sections()):track.remove_section(section)
    section=track.add_section();section.set_sound(sound)
    end=start+math.ceil(duration*24)
    section.set_range(start,end)
    assert end<=seq.get_playback_end()
    assert section.get_sound()==sound
    rows.append(dict(name=name,start_frame=start,end_frame=end,duration=duration))
assert rows[0]['end_frame']<=rows[1]['start_frame']
assert len([t for t in seq.get_tracks() if isinstance(t,unreal.MovieSceneAudioTrack)])==2
assert unreal.EditorAssetLibrary.save_loaded_asset(seq)
(root/'Voice'/'cart_timing.json').write_text(json.dumps(dict(fps=24,voices=rows,subtitles='Existing subtitles preserved; none added'),indent=2),encoding='utf8')
unreal.log('CART_HADES_VOICES_INSTALLED '+str(rows))
