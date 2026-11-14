"""Crossfade opening idle into sword draw without moving the draw or grip keys."""
import unreal
from pathlib import Path

seq = unreal.load_asset('/Game/DirectorCut/Prologue/LS_BossPrologue_Cinematic')
binding = next(b for b in seq.get_bindings() if b.get_name() == 'BossIntro_Hero')
track = next(t for t in binding.get_tracks() if isinstance(t, unreal.MovieSceneSkeletalAnimationTrack))
draw = next(s for s in track.get_sections() if s.params.animation and s.params.animation.get_name() == 'Withdrawing_Sword')
opening_idle = next(s for s in track.get_sections() if s.params.animation and s.params.animation.get_name() == 'Crouch_Idle' and s.get_start_frame() == 0)

blend_frames = 8
start = draw.get_start_frame()
display_rate = seq.get_display_rate()
tick_rate = seq.get_tick_resolution()
blend_seconds = blend_frames * display_rate.denominator / display_rate.numerator
blend_ticks = round(blend_seconds * tick_rate.numerator / tick_rate.denominator)

# Keep the draw's start, playback rate, and sword handoff fixed. Let the idle
# continue underneath its first eight frames while their weights crossfade.
opening_idle.set_end_frame(start + blend_frames)
opening_idle.set_ease_out_duration(blend_ticks)
draw.set_ease_in_duration(blend_ticks)
opening_idle.set_blend_type(unreal.MovieSceneBlendType.ABSOLUTE)
draw.set_blend_type(unreal.MovieSceneBlendType.ABSOLUTE)

assert opening_idle.get_end_frame() - draw.get_start_frame() == blend_frames
assert opening_idle.get_ease_out_duration() == draw.get_ease_in_duration() == blend_ticks
assert unreal.EditorAssetLibrary.save_loaded_asset(seq, False)
Path(unreal.Paths.project_saved_dir(), 'hero_draw_entry_blend_applied.txt').write_text(
    f'opening_idle={opening_idle.get_start_frame()}..{opening_idle.get_end_frame()}\n'
    f'draw={draw.get_start_frame()}..{draw.get_end_frame()}\n'
    f'blend_seconds={blend_seconds}\nblend_ticks={blend_ticks}\n'
    f'existing_draw_exit_ease_ticks={draw.get_ease_out_duration()}\n')
