"""Quiet opening music, cut exactly when the dragon starts 'Wait...'."""
import unreal
from pathlib import Path

SOURCE = r'C:/Users/서가은/Downloads/kf029206-rooftop-chase.wav'
FOLDER = '/Game/DirectorCut/Prologue/Cinematic/Audio/Music'
NAME = 'S_RooftopChase'
lib = unreal.EditorAssetLibrary
if not lib.does_asset_exist(FOLDER + '/' + NAME):
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
wait_sound = unreal.load_asset('/Game/DirectorCut/Prologue/Cinematic/03_Dragon_MissingLegs')
wait_section = next(s for t in seq.get_tracks() if isinstance(t, unreal.MovieSceneAudioTrack)
                    for s in t.get_sections() if s.get_sound() == wait_sound)
stop = wait_section.get_start_frame()
start = seq.get_playback_start()
track_name = 'Opening Rooftop Chase Music'
track = next((t for t in seq.get_tracks() if isinstance(t, unreal.MovieSceneAudioTrack)
              and str(t.get_display_name()) == track_name), None)
if track is None:
    track = seq.add_track(unreal.MovieSceneAudioTrack)
    track.set_display_name(track_name)
for old in list(track.get_sections()):
    track.remove_section(old)
section = track.add_section()
section.set_sound(sound)
section.set_range(start, stop)
volume = next(c for c in section.get_all_channels() if c.get_name().lower().startswith('volume'))
volume.set_default(0.12)
fps, ticks = seq.get_display_rate(), seq.get_tick_resolution()
tick_fps = ticks.numerator / ticks.denominator
section.set_ease_in_duration(round(.2 * tick_fps))
# A one-frame de-click ends at the dialogue boundary; no music under 'Wait'.
section.set_ease_out_duration(round(tick_fps * fps.denominator / fps.numerator))
assert section.get_end_frame() == wait_section.get_start_frame()
assert len(track.get_sections()) == 1
assert lib.save_loaded_asset(sound, False)
assert lib.save_loaded_asset(seq, False)
Path(unreal.Paths.project_saved_dir(), 'opening_music_applied.txt').write_text(
    f'sound={sound.get_path_name()}\nstart_frame={section.get_start_frame()}\n'
    f'stop_frame={section.get_end_frame()}\nwait_start_frame={wait_section.get_start_frame()}\n'
    f'volume={volume.get_default()}\nstop_seconds={stop * fps.denominator / fps.numerator}\n')
