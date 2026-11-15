import unreal,wave,math,json
from pathlib import Path
root=Path(unreal.Paths.project_dir())/'SourceAssets'/'Ending'/'Voice'
s=unreal.load_asset('/Game/DirectorCut/Ending/LS_BossEnding_OriginalLegs')
assert s
rows=[]
for name,start in [('S_OriginalLegs_Hero',156),('S_OriginalLegs_Dragon',243)]:
    file=root/(name+'.wav')
    with wave.open(str(file),'rb') as w: duration=w.getnframes()/w.getframerate()
    task=unreal.AssetImportTask();task.filename=str(file)
    task.destination_path='/Game/DirectorCut/Ending/Voice';task.destination_name=name
    task.automated=True;task.replace_existing=True;task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    sound=unreal.load_asset(task.destination_path+'/'+name);assert sound
    track=next((t for t in s.get_tracks() if isinstance(t,unreal.MovieSceneAudioTrack) and str(t.get_display_name())==name),None)
    if track is None: track=s.add_track(unreal.MovieSceneAudioTrack);track.set_display_name(name)
    for section in track.get_sections():track.remove_section(section)
    section=track.add_section();section.set_sound(sound)
    end=start+math.ceil(duration*24);section.set_range(start,end)
    rows.append({'name':name,'start':start,'end':end,'seconds':duration})
end_frame=372
s.set_playback_end(end_frame)
for t in s.get_tracks():
    if isinstance(t,unreal.MovieSceneCameraCutTrack):
        for section in t.get_sections():section.set_end_frame(end_frame)
for b in s.get_bindings():
    for t in b.get_tracks():
        for section in t.get_sections():
            if section.get_end_frame()==324: section.set_end_frame(end_frame)
assert rows[0]['end']<rows[1]['start'] and rows[1]['end']<end_frame
unreal.EditorAssetLibrary.set_metadata_tag(s,'Dialogue','KR + EN subtitles; Inworld Brick / Hades voices')
assert unreal.EditorAssetLibrary.save_loaded_asset(s)
(root/'original_legs_timing.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
unreal.log('ORIGINAL_VOICES_PASS '+str(rows))
