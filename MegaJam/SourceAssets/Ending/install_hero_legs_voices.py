"""Connect the supplied Brick voice to the hero-leg reaction line."""
import unreal,math,wave,json
from pathlib import Path
root=Path(unreal.Paths.project_dir())/'SourceAssets'/'Ending'
seq=unreal.load_asset('/Game/DirectorCut/Ending/LS_BossEnding_HeroLegs')
name='S_HeroLegs_Hero';path=root/'Voice'/(name+'.wav')
with wave.open(str(path),'rb') as wav:duration=wav.getnframes()/wav.getframerate()
task=unreal.AssetImportTask();task.filename=str(path)
task.destination_path='/Game/DirectorCut/Ending/Voice';task.destination_name=name
task.automated=True;task.replace_existing=True;task.save=True
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
sound=unreal.load_asset('/Game/DirectorCut/Ending/Voice/'+name);assert sound
track=next((t for t in seq.get_tracks() if isinstance(t,unreal.MovieSceneAudioTrack) and str(t.get_display_name())==name),None)
if not track:track=seq.add_track(unreal.MovieSceneAudioTrack);track.set_display_name(name)
for section in list(track.get_sections()):track.remove_section(section)
section=track.add_section();section.set_sound(sound)
start=84;end=start+math.ceil(duration*24);assert end<=seq.get_playback_end()
section.set_range(start,end)
assert section.get_sound()==sound
assert unreal.EditorAssetLibrary.save_loaded_asset(seq)
(root/'Voice'/'hero_legs_timing.json').write_text(json.dumps(dict(start_frame=start,end_frame=end,duration=duration),indent=2),encoding='utf8')
unreal.log('HERO_LEGS_BRICK_VOICE_INSTALLED')
