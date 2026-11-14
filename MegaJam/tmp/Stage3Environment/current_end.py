import unreal as u,json
from pathlib import Path
s=u.get_editor_subsystem(u.EditorActorSubsystem)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name()=="/Game/DirectorCut/Stage/Stage3_.Stage3_"
rows=[]
for a in s.get_all_level_actors():
 p=a.get_actor_location()
 if p.x>6200:
  center,extent=a.get_actor_bounds(False)
  rows.append((a.get_actor_label(),a.get_class().get_name(),a.get_path_name(),p.to_tuple(),center.to_tuple(),extent.to_tuple()))
Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage3Environment/end_current.json").write_text(json.dumps(rows,indent=1))
