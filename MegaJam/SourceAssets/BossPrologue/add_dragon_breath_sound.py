"""Sync the supplied airy dragon fire wave with the existing Niagara shot."""
import unreal
from pathlib import Path

SOURCE = r'C:/Users/서가은/Downloads/creature-whoosh-dragon-airy-fire-wave-long-02.wav'
FOLDER = '/Game/DirectorCut/Prologue/Cinematic/Audio/SFX'
NAME = 'S_DragonBreath_AiryFireWave'
# Measured from the 24-bit PCM waveform in 20 ms windows: the main attack
# crosses -20 dB relative RMS at 1.18 s, then rises sharply over the next 20 ms.
SOUND_ONSET_SECONDS = 1.18
lib = unreal.EditorAssetLibrary
sound = unreal.load_asset(FOLDER + '/' + NAME) if lib.does_asset_exist(FOLDER + '/' + NAME) else None
if not sound:
    task = unreal.AssetImportTask()
    task.filename = SOURCE
    task.destination_path = FOLDER
    task.destination_name = NAME
    task.automated = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    sound = unreal.load_asset(FOLDER + '/' + NAME)
assert isinstance(sound, unreal.SoundWave)
sound.set_editor_property('looping', False)

seq = unreal.load_asset('/Game/DirectorCut/Prologue/LS_BossPrologue_Cinematic')
fire = next(s for b in seq.get_bindings() for t in b.get_tracks()
            if isinstance(t, unreal.MovieSceneNiagaraSystemTrack) for s in t.get_sections())
start, fire_end = fire.get_start_frame(), fire.get_end_frame()
fade_frames = 8
track_name = 'Dragon Fire Breath SFX'
track = next((t for t in seq.get_tracks() if isinstance(t, unreal.MovieSceneAudioTrack)
              and str(t.get_display_name()) == track_name), None)
if track is None:
    track = seq.add_track(unreal.MovieSceneAudioTrack)
    track.set_display_name(track_name)
for section in list(track.get_sections()):
    track.remove_section(section)
section = track.add_section()
section.set_sound(sound)
section.set_range(start, fire_end + fade_frames)

display_rate, tick_rate = seq.get_display_rate(), seq.get_tick_resolution()
ticks_per_frame = (tick_rate.numerator / tick_rate.denominator) / (display_rate.numerator / display_rate.denominator)
tick_fps = tick_rate.numerator / tick_rate.denominator
source_offset = round(SOUND_ONSET_SECONDS * tick_fps)
section.set_start_offset(unreal.FrameNumber(source_offset))
# A 5 ms fade prevents a trim click without softening the audible attack.
section.set_ease_in_duration(round(0.005 * tick_fps))
section.set_ease_out_duration(round(fade_frames * ticks_per_frame))
volume = next(c for c in section.get_all_channels() if c.get_name().lower().startswith('volume'))
volume.set_default(0.85)

assert section.get_start_frame() == start
assert section.get_end_frame() == fire_end + fade_frames
assert section.get_sound() == sound
assert section.get_start_offset().value == source_offset
assert lib.save_loaded_asset(sound, False)
assert lib.save_loaded_asset(seq, False)
Path(unreal.Paths.project_saved_dir(), 'dragon_breath_sound_applied.txt').write_text(
    f'sound={sound.get_path_name()}\nfire={start}..{fire_end}\n'
    f'audio={section.get_start_frame()}..{section.get_end_frame()}\n'
    f'source_offset_seconds={section.get_start_offset().value / tick_fps}\n'
    f'fade_out_ticks={section.get_ease_out_duration()}\nvolume={volume.get_default()}\n')
