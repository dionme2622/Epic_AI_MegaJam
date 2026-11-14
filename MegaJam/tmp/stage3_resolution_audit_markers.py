import json
from pathlib import Path
import unreal as u

world = u.get_editor_subsystem(u.UnrealEditorSubsystem)
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
assert world.get_editor_world().get_path_name() == "/Game/DirectorCut/Stage/Stage3_.Stage3_"
assert levels.load_level("/Game/Stage3Integrated/Sections/L_Resolution")
rows = []
for actor in actors.get_all_level_actors():
    if "Resolution Choice" not in actor.get_actor_label() and "Dots" not in actor.get_actor_label() and "Guide" not in actor.get_actor_label():
        continue
    center, extent = actor.get_actor_bounds(False)
    row = {
        "label": actor.get_actor_label(),
        "location": actor.get_actor_location().to_tuple(),
        "rotation": actor.get_actor_rotation().to_tuple(),
        "bounds": [center.to_tuple(), extent.to_tuple()],
    }
    text = actor.get_component_by_class(u.TextRenderComponent)
    if text:
        row["text"] = str(text.text)
        row["world_size"] = text.get_editor_property("world_size")
        row["horizontal_alignment"] = str(text.get_editor_property("horizontal_alignment"))
        row["vertical_alignment"] = str(text.get_editor_property("vertical_alignment"))
    rows.append(row)
Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/stage3_resolution_check/marker_audit.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
assert levels.load_level("/Game/DirectorCut/Stage/Stage3_")
