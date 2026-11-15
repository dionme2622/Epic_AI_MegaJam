"""Prepare supplied audio, then --import adds only owned SFX tracks to sequences."""
from pathlib import Path
import sys,json,subprocess,wave,array,math,shutil
ROOT=Path(__file__).resolve().parent
DIR=ROOT/'SFX';DIR.mkdir(exist_ok=True)
P='/Game/DirectorCut/Ending/'
sources={
 'UI_Select':'ui-classic-hover-high-tonal-08.wav',
 'Original_Footstep':'foley-step-giant-footsteps-05.wav',
 'Cart_Roll':'object-shopping-cart-modern-drive-sequence-inhouse-03.wav',
 'Hero_Footstep':'foley-step-ice-quick-foot-scrape-single-01.wav'}
if '--import' not in sys.argv:
 report={}
 for name,file in sources.items():
  src=Path.home()/'Downloads'/file
  shutil.copy2(src,DIR/file)
  decoded=DIR/(name+'_decoded.wav')
  subprocess.run(['D:/ffmpeg-8.0.1-full_build/bin/ffmpeg.exe','-v','error','-y','-i',str(src),'-ar','48000','-ac','1','-c:a','pcm_s16le',str(decoded)],check=True)
  with wave.open(str(decoded),'rb') as w: pcm=array.array('h',w.readframes(w.getnframes()))
  block=240
  energy=[sum(v*v for v in pcm[i:i+block])/block for i in range(0,len(pcm),block)]
  threshold=max(energy)*.015
  onset=next(i for i,v in enumerate(energy) if v>threshold)*block
  start=max(0,onset-48)
  cap={'Original_Footstep':.48,'Hero_Footstep':.25,'UI_Select':1.5,'Cart_Roll':5.25}[name]
  end=min(len(pcm),start+round(cap*48000))
  out=pcm[start:end]
  fade_in=48;fade_out=min(2400,len(out)//4) if name=='Cart_Roll' else min(480,len(out)//4)
  for i in range(fade_in): out[i]=int(out[i]*i/fade_in)
  for i in range(fade_out): out[-1-i]=int(out[-1-i]*i/fade_out)
  with wave.open(str(DIR/('S_'+name+'.wav')),'wb') as w:
   w.setparams((1,2,48000,0,'NONE','not compressed'));w.writeframes(out.tobytes())
  report[name]=dict(source=file,source_onset_seconds=onset/48000,duration=len(out)/48000)
 (DIR/'sources.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 print(report)
else:
 import unreal
 assets={}
 for name in sources:
  task=unreal.AssetImportTask();task.filename=str(DIR/('S_'+name+'.wav'))
  task.destination_path=P+'SFX';task.destination_name='S_'+name
  task.automated=True;task.save=True;task.replace_existing=True
  unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
  assets[name]=unreal.load_asset(P+'SFX/S_'+name);assert assets[name]
 report=[]
 def install(seqname,kind,frames,volume,end_limit):
  seq=unreal.load_asset(P+seqname);assert seq
  # Track prefix is exclusive to this installer. Voice, camera and motion tracks stay intact.
  label='Ending SFX / '+kind
  tracks=[t for t in seq.get_tracks() if str(t.get_display_name())==label]
  track=tracks[0] if tracks else seq.add_track(unreal.MovieSceneAudioTrack)
  track.set_display_name(label)
  for section in list(track.get_sections()):track.remove_section(section)
  duration=assets[kind].get_editor_property('duration')
  for i,frame in enumerate(frames):
   section=track.add_section();section.set_sound(assets[kind])
   end=min(end_limit,frame+math.ceil(duration*24))
   section.set_range(frame,end)
   section.set_row_index(i%2)
   for ch in section.get_all_channels():
    if 'volume' in str(ch.channel_name).lower(): ch.set_default(volume)
   assert section.get_sound()==assets[kind]
   assert section.get_start_frame()==frame and section.get_end_frame()==end
   report.append(dict(sequence=seqname,sound=kind,frame=frame,end=end,seconds=frame/24,volume=volume))
  assert len(track.get_sections())==len(frames)
  assert unreal.EditorAssetLibrary.save_loaded_asset(seq)
 install('LS_BossEnding_Reveal','UI_Select',[0],.45,72)
 # Animation local foot minima/arrival on held pose: cycle frames 22,34,41.
 # Each awkward cycle is 48 frames, begins at sequence frame 36.
 install('LS_BossEnding_OriginalLegs','Original_Footstep',[58,70,77,106,118,125],.45,144)
 # Toe support minima begin at source frames 4/16; 1.2x yields 10-frame spacing.
 install('LS_BossEnding_HeroLegs','Hero_Footstep',[15,25,35,45,55,65],.45,72)
 install('LS_BossEnding_Cart','Cart_Roll',[18],.22,144)
 (DIR/'installation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 unreal.log('ENDING_SFX_INSTALL_VERIFIED: 4 sounds, 14 sections')
