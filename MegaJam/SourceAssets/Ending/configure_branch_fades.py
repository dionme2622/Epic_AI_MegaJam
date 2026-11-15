"""Fade in once before the first line; fade out only at each branch ending."""
from pathlib import Path
import unreal,json
P='/Game/DirectorCut/Ending/'
report=[]
intro=unreal.load_asset(P+'LS_BossEnding_Dialogue');assert intro
for old in list(intro.get_tracks()):
    if isinstance(old,unreal.MovieSceneFadeTrack):intro.remove_track(old)
track=intro.add_track(unreal.MovieSceneFadeTrack);track.set_display_name('Opening Fade In / Before Hero Dialogue')
section=track.add_section();section.set_range(0,13)
section.set_editor_property('fade_color',unreal.LinearColor(0,0,0,1));section.set_editor_property('fade_audio',False)
section.set_completion_mode(unreal.MovieSceneCompletionMode.RESTORE_STATE)
channel=section.get_all_channels()[0];channel.set_default(0.0)
for frame,value in [(0,1.0),(12,0.0)]:
    channel.add_key(unreal.FrameNumber(frame),value,interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
hero_audio=next(t for t in intro.get_tracks() if isinstance(t,unreal.MovieSceneAudioTrack) and str(t.get_display_name())=='S_Ending_Hero')
assert min(s.get_start_frame() for s in hero_audio.get_sections())>12
assert unreal.EditorAssetLibrary.save_loaded_asset(intro)
report.append(dict(sequence='LS_BossEnding_Dialogue',fade_in_frames=[0,12],before_hero_frame=14))
for name in ['LS_BossEnding_OriginalLegs','LS_BossEnding_Cart','LS_BossEnding_HeroLegs']:
    seq=unreal.load_asset(P+name);assert seq
    start,end=seq.get_playback_start(),seq.get_playback_end()
    for old in list(seq.get_tracks()):
        if isinstance(old,unreal.MovieSceneFadeTrack):seq.remove_track(old)
    track=seq.add_track(unreal.MovieSceneFadeTrack);track.set_display_name('Ending Fade Out Only')
    section=track.add_section();section.set_range(end-19,end)
    section.set_editor_property('fade_color',unreal.LinearColor(0,0,0,1));section.set_editor_property('fade_audio',False)
    section.set_completion_mode(unreal.MovieSceneCompletionMode.KEEP_STATE)
    channel=section.get_all_channels()[0];channel.set_default(0.0)
    keys=[(end-19,0.0),(end-1,1.0)]
    for f,v in keys:channel.add_key(unreal.FrameNumber(f),v,interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
    assert section.get_start_frame()>start
    assert channel.get_keys()[0].get_value()==0 and channel.get_keys()[-1].get_value()==1
    assert unreal.EditorAssetLibrary.save_loaded_asset(seq)
    report.append(dict(sequence=name,fade_out_keys=keys,branch_fade_in=False))
Path(unreal.Paths.project_saved_dir(),'ending_branch_fades.json').write_text(json.dumps(report,indent=2),encoding='utf8')
unreal.log('ENDING_FADE_IN_MOVED_BEFORE_FIRST_HERO_LINE')
