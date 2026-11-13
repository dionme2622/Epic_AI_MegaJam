"""Hold a dark opening, then reveal the prologue within the first second."""
import unreal
from pathlib import Path

seq = unreal.load_asset('/Game/DirectorCut/Prologue/LS_BossPrologue_Cinematic')
fps = seq.get_display_rate()
duration = round(fps.numerator / fps.denominator)
track = next((t for t in seq.get_tracks() if isinstance(t, unreal.MovieSceneFadeTrack)), None)
if track is None:
    track = seq.add_track(unreal.MovieSceneFadeTrack)
    track.set_display_name('Opening Fade In')
for old in list(track.get_sections()):
    if old.get_start_frame() == 0 and old.get_end_frame() <= duration + 1:
        track.remove_section(old)
section = track.add_section()
section.set_range(0, duration + 1)
section.set_editor_property('fade_color', unreal.LinearColor(0, 0, 0, 1))
section.set_editor_property('fade_audio', False)
section.set_completion_mode(unreal.MovieSceneCompletionMode.RESTORE_STATE)
channel = section.get_all_channels()[0]
channel.set_default(0.0)
fade_keys = [(0, 1.0), (round(duration*.25), 1.0),
             (round(duration*.5), .94), (round(duration*2/3), .72),
             (round(duration*5/6), .34), (duration, 0.0)]
for frame, opacity in fade_keys:
    channel.add_key(unreal.FrameNumber(frame), opacity, interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
assert len(channel.get_keys()) == len(fade_keys)
assert channel.get_keys()[0].get_value() == 1.0
assert channel.get_keys()[-1].get_value() == 0.0
assert unreal.EditorAssetLibrary.save_loaded_asset(seq, False)
Path(unreal.Paths.project_saved_dir(), 'opening_fade_applied.txt').write_text(
    f'black_hold_frames=0..{round(duration*.25)}\nclear_frame={duration}\nsection_end={section.get_end_frame()}\n'
    f'fade_keys={[(k.get_time().frame_number.value, k.get_value()) for k in channel.get_keys()]}\n'
    f'fade_audio={section.get_editor_property("fade_audio")}\n')
