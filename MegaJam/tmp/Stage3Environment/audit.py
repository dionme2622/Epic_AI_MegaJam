import unreal as u,json
from pathlib import Path
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=="/Game/DirectorCut/Stage/Stage3_.Stage3_"
results=[]
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 p=a.get_actor_location();b,e=a.get_actor_bounds(False)
 results.append({"label":a.get_actor_label(),"class":a.get_class().get_name(),"path":a.get_path_name(),"loc":p.to_tuple(),"center":b.to_tuple(),"ext":e.to_tuple()})
Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage3Environment/actors.json").write_text(json.dumps(results,indent=2),encoding="utf8")
