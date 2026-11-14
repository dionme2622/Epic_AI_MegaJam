"""Crossfade the final eight frames of the sword draw into crouch idle."""
import unreal
from pathlib import Path
seq=unreal.load_asset('/Game/DirectorCut/Prologue/LS_BossPrologue_Cinematic')
b=next(b for b in seq.get_bindings() if b.get_name()=='BossIntro_Hero')
track=next(t for t in b.get_tracks() if isinstance(t,unreal.MovieSceneSkeletalAnimationTrack))
draw=next(s for s in track.get_sections() if 'Withdrawing_Sword' in s.params.animation.get_name())
idle=next(s for s in track.get_sections() if 'Crouch_Idle' in s.params.animation.get_name() and s.get_start_frame()>0)
end=222
blend=8
draw.set_end_frame(end)
params=draw.params
params.set_editor_property('play_rate',unreal.MovieSceneTimeWarpVariant(params.animation.get_play_length()/((end-draw.get_start_frame())/24)))
draw.params=params
idle.set_start_frame(end-blend)
# Complementary weights avoid the full-weight pose jump at the section edge.
tick_rate=seq.get_tick_resolution()
blend_ticks=round(blend/24*tick_rate.numerator/tick_rate.denominator)
draw.set_ease_out_duration(blend_ticks)
idle.set_ease_in_duration(blend_ticks)
draw.set_blend_type(unreal.MovieSceneBlendType.ABSOLUTE)
idle.set_blend_type(unreal.MovieSceneBlendType.ABSOLUTE)
unreal.EditorAssetLibrary.save_loaded_asset(seq,False)
assert draw.get_end_frame()-idle.get_start_frame()==blend
assert draw.get_ease_out_duration()==idle.get_ease_in_duration()==blend_ticks
Path(unreal.Paths.project_saved_dir(),'hero_blend_applied.txt').write_text(f'draw={draw.get_start_frame()}..{draw.get_end_frame()} ease_out_ticks={draw.get_ease_out_duration()}\nidle={idle.get_start_frame()}..{idle.get_end_frame()} ease_in_ticks={idle.get_ease_in_duration()}\nblend_seconds={blend/24}\ntick_rate={tick_rate}')
