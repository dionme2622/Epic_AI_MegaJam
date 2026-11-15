import unreal,json
from pathlib import Path
root=Path(__file__).resolve().parent
rows=json.loads((root/'SFX/installation.json').read_text())
report=[]
for seqname in sorted(set(r['sequence'] for r in rows)):
 seq=unreal.load_asset('/Game/DirectorCut/Ending/'+seqname)
 expected=[r for r in rows if r['sequence']==seqname]
 sections=[];voices=[]
 for track in seq.get_tracks():
  if not isinstance(track,unreal.MovieSceneAudioTrack):continue
  for section in track.get_sections():
   sound=section.get_sound();assert sound
   if str(track.get_display_name()).startswith('Ending SFX / '):
    matches=[r for r in expected if r['frame']==section.get_start_frame() and sound.get_name()=='S_'+r['sound']]
    assert len(matches)==1
    volume=[ch.get_default() for ch in section.get_all_channels() if 'volume' in str(ch.channel_name).lower()]
    assert volume and abs(volume[0]-matches[0]['volume'])<.001,volume
    assert section.get_end_frame()==matches[0]['end']
    sections.append(matches[0])
   else:voices.append(sound.get_name())
 assert len(sections)==len(expected)
 required={'LS_BossEnding_OriginalLegs':['S_OriginalLegs_Hero','S_OriginalLegs_Dragon'],
           'LS_BossEnding_HeroLegs':['S_HeroLegs_Hero'],
           'LS_BossEnding_Cart':['S_Ending_Cart_Brakes','S_Ending_Cart_Scream']}.get(seqname,[])
 assert all(n in voices for n in required),(seqname,voices)
 report.append(dict(sequence=seqname,sfx_sections=len(sections),voices_preserved=voices,passed=True))
(root/'SFX/verification.json').write_text(json.dumps(report,indent=2),encoding='utf8')
unreal.log('ENDING_SFX_DISK_VERIFICATION_PASS')
