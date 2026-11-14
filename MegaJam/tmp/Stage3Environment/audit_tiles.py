import unreal as u,json
from pathlib import Path
e=u.get_editor_subsystem(u.UnrealEditorSubsystem)
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assert e.get_editor_world().get_path_name()=="/Game/DirectorCut/Stage/Stage3_.Stage3_"
assert levels.load_level("/Game/Stage3Integrated/Sections/L_Resolution")
assert e.get_editor_world().get_path_name()=="/Game/Stage3Integrated/Sections/L_Resolution.L_Resolution"
rows=[]
for a in actors.get_all_level_actors():
 if "ResolutionTile" in a.get_class().get_name() or "Resolution Tile" in a.get_actor_label():
  p=a.get_actor_location()
  mesh=a.get_editor_property("Mesh")
  rows.append({"label":a.get_actor_label(),"x":p.x,"safe":a.get_editor_property("bSafe"),"order":a.get_editor_property("SafeOrder"),"component":mesh.get_name(),"collision":str(mesh.get_collision_enabled())})
Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage3Environment/tile-report.json").write_text(json.dumps(rows,indent=2))
assert levels.load_level("/Game/DirectorCut/Stage/Stage3_")
