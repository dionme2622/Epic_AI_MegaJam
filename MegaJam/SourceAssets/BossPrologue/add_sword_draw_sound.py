"""Add the supplied sword sound at the knight's draw in the boss prologue."""
from pathlib import Path
import unreal

source = Path(unreal.Paths.project_dir()) / 'SourceAssets/BossPrologue/Audio/weapons-sword-sword-slash-soft-03.wav'
folder = '/Game/DirectorCut/Prologue/Cinematic/Audio/SFX'
name = 'S_KnightSwordDraw'
lib = unreal.EditorAssetLibrary
sound = unreal.load_asset(folder + '/' + name) if lib.does_asset_exist(folder + '/' + name) else None
if sound is None:
    task = unreal.AssetImportTask()
    task.filename = str(source)
    task.destination_path = folder
    task.destination_name = name
    task.automated = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    sound = unreal.load_asset(folder + '/' + name)
assert isinstance(sound, unreal.SoundWave), 'Sword sound import failed'
sound.set_editor_property('looping', False)

seq = unreal.load_asset('/Game/DirectorCut/Prologue/LS_BossPrologue_Cinematic')
hero = next(b for b in seq.get_bindings() if b.get_name() == 'BossIntro_Hero')
anim_track = next(t for t in hero.get_tracks() if isinstance(t, unreal.MovieSceneSkeletalAnimationTrack))
draw = next(s for s in anim_track.get_sections()
            if s.params.animation and s.params.animation.get_name() == 'Withdrawing_Sword')
start = draw.get_start_frame()
rate = seq.get_display_rate().numerator / seq.get_display_rate().denominator
duration = sound.get_editor_property('duration')
end = start + round(duration * rate)

track_name = 'Knight Sword Draw SFX'
track = next((t for t in seq.get_tracks() if isinstance(t, unreal.MovieSceneAudioTrack)
              and str(t.get_display_name()) == track_name), None)
if track is None:
    track = seq.add_track(unreal.MovieSceneAudioTrack)
    track.set_display_name(track_name)
for old in list(track.get_sections()):
    track.remove_section(old)
section = track.add_section()
section.set_sound(sound)
section.set_range(start, end)

assert section.get_sound() == sound
assert section.get_start_frame() == start
assert lib.save_loaded_asset(sound, False)
assert lib.save_loaded_asset(seq, False)
Path(unreal.Paths.project_saved_dir(), 'sword_draw_sound_applied.txt').write_text(
    f'sound={sound.get_path_name()}\nstart_frame={start}\nend_frame={end}\n'
    f'duration_seconds={duration}\n')
