import unreal as u,json
from pathlib import Path
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
items=[]
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 label=a.get_actor_label()
 if any(k in label.lower() for k in ["resolution","tile","bloom","scene","levelinstance","archive","door","floor"]):
  loc=a.get_actor_location()
  row={"label":label,"type":a.get_class().get_name(),"path":a.get_path_name(),"loc":loc.to_tuple(),"tags":[str(t) for t in a.tags]}
  if "tile" in label.lower():
   for k in ["bSafe","SafeOrder"]:
    try:row[k]=a.get_editor_property(k)
    except:pass
  items.append(row)
Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/stage3_actors.json").write_text(json.dumps(items,indent=2))
