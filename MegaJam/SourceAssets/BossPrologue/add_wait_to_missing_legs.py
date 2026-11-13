"""Update only the missing-legs caption and voice in the existing prologue."""
import unreal,asyncio,sys,subprocess,wave,json,math
from pathlib import Path
root=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
sys.path.insert(0,str(root/'Saved/PythonPackages'))
import edge_tts
folder=root/'SourceAssets/BossPrologue'
voice=folder/'Voice/03_Dragon_MissingLegs.wav'
mp3=root/'Saved/03_Dragon_MissingLegs_Wait.mp3'
text='Wait... Where did my legs go?'
async def make_line():
 await edge_tts.Communicate(text,'en-US-ChristopherNeural',rate='-10%',pitch='-18Hz').save(str(mp3))
asyncio.run(make_line())
subprocess.run([r'D:/ffmpeg-8.0.1-full_build/bin/ffmpeg.exe','-y','-hide_banner','-loglevel','error','-i',str(mp3),'-ar','48000','-ac','1','-c:a','pcm_s16le',str(voice)],check=True)
with wave.open(str(voice),'rb') as w:duration=w.getnframes()/w.getframerate()
manifest_path=folder/'Voice/manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8-sig'))
for row in manifest:
 if row['name']=='03_Dragon_MissingLegs':row['text']=text;row['duration_seconds']=round(duration,3)
manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
tasks=[]
for source,name in [(folder/'Graphics/03_Missing.png','03_Missing'),(voice,'03_Dragon_MissingLegs')]:
 task=unreal.AssetImportTask();task.filename=str(source);task.destination_path='/Game/DirectorCut/Prologue/Cinematic';task.destination_name=name;task.automated=True;task.replace_existing=True;task.replace_existing_settings=False;task.save=True;tasks.append(task)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
lib=unreal.EditorAssetLibrary
sound=unreal.load_asset('/Game/DirectorCut/Prologue/Cinematic/03_Dragon_MissingLegs')
seq=unreal.load_asset('/Game/DirectorCut/Prologue/LS_BossPrologue_Cinematic')
audio_end=None
for track in seq.get_tracks():
 if isinstance(track,unreal.MovieSceneAudioTrack):
  for section in track.get_sections():
   if section.get_sound()==sound:
    audio_end=section.get_start_frame()+math.ceil(duration*24)
    section.set_end_frame(audio_end)
assert audio_end is not None
caption_end=max(350,audio_end+4)
assert caption_end<405
for binding in seq.get_bindings():
 if binding.get_name()=='BossIntro_Subtitle_03_Missing':
  for track in binding.get_tracks():
   if isinstance(track,unreal.MovieSceneVisibilityTrack):
    for section in track.get_sections():
     channel=section.get_all_channels()[0]
     for key in list(channel.get_keys()):
      if key.get_time().frame_number.value>282 and not key.get_value():channel.remove_key(key)
     channel.add_key(unreal.FrameNumber(caption_end),False)
assert lib.save_loaded_asset(seq,False)
(root/'Saved/missing_legs_wait_applied.txt').write_text(f'text={text}\nvoice_duration={duration}\naudio_end={audio_end}\ncaption_end={caption_end}\n')
