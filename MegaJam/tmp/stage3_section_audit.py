import unreal as u,json
from pathlib import Path
l=u.get_editor_subsystem(u.LevelEditorSubsystem)
a=u.get_editor_subsystem(u.EditorActorSubsystem)
o={}
for path in ["/Game/Stage3Integrated/Sections/L_Bloom","/Game/Stage3Integrated/Sections/L_Resolution"]:
 assert l.load_level(path)
 rows=[]
 for x in a.get_all_level_actors():
  n=x.get_actor_label()
  p=x.get_actor_location()
  if any(k in n.lower() for k in ["bloom","resolution","sign","tile","guidance","arrow","door"]):
   d={"name":n,"type":x.get_class().get_name(),"x":p.x,"y":p.y,"z":p.z,"path":x.get_path_name()}
   for k in ["bSafe","SafeOrder","GuidanceArrows","bUseLocalCheckpoint","LocalCheckpointOffset","FilmSources","FilmScenes","ExitDoor"]:
    try:d[k]=str(x.get_editor_property(k))
    except:pass
   rows.append(d)
 o[path]=rows
Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/stage3_section_audit.json").write_text(json.dumps(o,indent=2))
assert l.load_level("/Game/DirectorCut/Stage/Stage3_")
