"""Import and install the supplied looping BGM in campaign gameplay maps."""
from pathlib import Path
import sys,shutil,subprocess,json,wave
ROOT=Path(__file__).resolve().parent
DIR=ROOT/'GameplayBGM';DIR.mkdir(exist_ok=True)
NAME='kf012604-processing-power.wav'
if '--import' not in sys.argv:
 src=Path.home()/'Downloads'/NAME
 shutil.copy2(src,DIR/NAME)
 subprocess.run(['D:/ffmpeg-8.0.1-full_build/bin/ffmpeg.exe','-v','error','-y','-i',str(src),'-ar','48000','-c:a','pcm_s16le',str(DIR/'S_Gameplay_ProcessingPower.wav')],check=True)
 with wave.open(str(DIR/'S_Gameplay_ProcessingPower.wav'),'rb') as w:
  print(dict(duration=w.getnframes()/w.getframerate(),channels=w.getnchannels(),sample_rate=w.getframerate()))
else:
 import unreal
 asset='/Game/DirectorCut/Audio/S_Gameplay_ProcessingPower'
 task=unreal.AssetImportTask();task.filename=str(DIR/'S_Gameplay_ProcessingPower.wav')
 task.destination_path='/Game/DirectorCut/Audio';task.destination_name='S_Gameplay_ProcessingPower'
 task.automated=True;task.replace_existing=True;task.save=True
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
 sound=unreal.load_asset(asset);assert sound
 sound.set_editor_property('looping',True)
 assert unreal.EditorAssetLibrary.save_loaded_asset(sound)
 editor=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 paths=['/Game/DirectorCut/Stage/'+m for m in ['Stage1','Stage2','Stage3_','Stage4']]
 report=[]
 for path in paths:
  assert editor.load_level(path)
  existing=[a for a in actors.get_all_level_actors() if a.get_actor_label()=='Gameplay_BGM_ProcessingPower']
  assert len(existing)<=1
  actor=existing[0] if existing else actors.spawn_actor_from_class(unreal.AmbientSound,unreal.Vector())
  actor.set_actor_label('Gameplay_BGM_ProcessingPower')
  component=actor.get_editor_property('audio_component')
  component.set_sound(sound)
  component.set_volume_multiplier(.22)
  component.set_editor_property('auto_activate',True)
  component.set_editor_property('allow_spatialization',False)
  component.set_editor_property('is_ui_sound',True)
  assert editor.save_current_level()
 # Reload from disk, checking saved actor, sound, looping and non-spatial playback.
 for path in reversed(paths):
  assert editor.load_level(path)
  found=[a for a in actors.get_all_level_actors() if a.get_actor_label()=='Gameplay_BGM_ProcessingPower']
  assert len(found)==1,path
  c=found[0].get_editor_property('audio_component')
  s=c.get_editor_property('sound')
  assert s.get_path_name().split('.')[0]==asset
  assert s.get_editor_property('looping')
  assert c.get_editor_property('auto_activate')
  assert not c.get_editor_property('allow_spatialization')
  assert abs(c.get_editor_property('volume_multiplier')-.22)<.001
  report.append(dict(map=path,sound=s.get_path_name(),looping=True,auto_activate=True,spatial=False,volume=.22,duration=s.get_editor_property('duration')))
 (DIR/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 unreal.log('GAMEPLAY_BGM_INSTALL_VERIFY_PASS: four maps, looping enabled')
