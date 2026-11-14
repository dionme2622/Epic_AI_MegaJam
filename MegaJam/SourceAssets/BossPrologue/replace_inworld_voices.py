"""Replace only the four existing prologue voice assets and audio section lengths."""
import json
import math
import wave
from pathlib import Path

import unreal

root = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
voice_dir = root / "SourceAssets/BossPrologue/Voice"
asset_dir = "/Game/DirectorCut/Prologue/Cinematic"
sequence_path = "/Game/DirectorCut/Prologue/LS_BossPrologue_Cinematic"
names = (
    "01_Hero_Challenge",
    "02_Dragon_Threat",
    "03_Dragon_MissingLegs",
    "04_Dragon_Protest",
)
voice_names = ("Brick", "Hades", "Hades", "Hades")

durations = {}
tasks = []
for name in names:
    source = voice_dir / (name + ".wav")
    with wave.open(str(source), "rb") as audio:
        assert audio.getnchannels() == 1 and audio.getframerate() == 48000
        durations[name] = audio.getnframes() / audio.getframerate()
    task = unreal.AssetImportTask()
    task.filename = str(source)
    task.destination_path = asset_dir
    task.destination_name = name
    task.automated = True
    task.replace_existing = True
    task.replace_existing_settings = False
    task.save = True
    tasks.append(task)

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
library = unreal.EditorAssetLibrary
sounds = {}
for name in names:
    path = asset_dir + "/" + name
    sounds[name] = unreal.load_asset(path)
    assert sounds[name], path

sequence = unreal.load_asset(sequence_path)
assert sequence, sequence_path
updated = set()
for track in sequence.get_tracks():
    if not isinstance(track, unreal.MovieSceneAudioTrack):
        continue
    for section in track.get_sections():
        sound = section.get_sound()
        if not sound:
            continue
        name = sound.get_name()
        if name not in sounds:
            continue
        section.set_editor_property("sound", sounds[name])
        start = section.get_start_frame()
        end = start + math.ceil(durations[name] * 24) + 2
        section.set_end_frame(end)
        updated.add(name)
        unreal.log(f"INWORLD_VOICE_REPLACED {name} {start}-{end} {durations[name]:.3f}s")

assert updated == set(names), f"Expected {names}, updated {sorted(updated)}"
assert library.save_loaded_asset(sequence)

manifest_path = voice_dir / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
for row in manifest:
    if row["name"] in names:
        index = names.index(row["name"])
        row["voice"] = f"Inworld TTS 2 / {voice_names[index]}"
        row["duration_seconds"] = round(durations[row["name"]], 3)
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
unreal.log("INWORLD_VOICE_REPLACEMENT_OK")
