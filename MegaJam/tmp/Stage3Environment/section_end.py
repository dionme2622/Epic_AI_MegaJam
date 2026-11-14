import unreal as u,json
from pathlib import Path
e=u.get_editor_subsystem(u.UnrealEditorSubsystem);le=u.get_editor_subsystem(u.LevelEditorSubsystem);sub=u.get_editor_subsystem(u.EditorActorSubsystem)
assert e.get_editor_world().get_path_name()=="/Game/DirectorCut/Stage/Stage3_.Stage3_"
assert le.load_level("/Game/Stage3Integrated/Sections/L_Resolution")
rows=[]
for a in sub.get_all_level_actors():
 p=a.get_actor_location()
 if p.x>1200:
  center,extent=a.get_actor_bounds(False)
  meshes=[]
  for c in a.get_components_by_class(u.StaticMeshComponent):
   meshes.append((c.get_name(),str(c.get_editor_property("static_mesh")),str(c.get_material(0)),str(c.get_collision_profile_name())))
  rows.append((a.get_actor_label(),a.get_class().get_name(),p.to_tuple(),center.to_tuple(),extent.to_tuple(),meshes))
Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage3Environment/section_end.json").write_text(json.dumps(rows,indent=1))
assert le.load_level("/Game/DirectorCut/Stage/Stage3_")
