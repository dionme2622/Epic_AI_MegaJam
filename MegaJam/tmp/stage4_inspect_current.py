import json
import unreal
from pathlib import Path
sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors=sub.get_all_level_actors()
result=[]
for a in actors:
    name=a.get_actor_label()
    loc=a.get_actor_location()
    origin, ext=a.get_actor_bounds(False)
    result.append([name,a.get_class().get_name(),tuple(loc.to_tuple()),tuple(origin.to_tuple()),tuple(ext.to_tuple()),a.get_path_name()])
Path(r'C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/stage4_current.json').write_text(json.dumps(result,indent=2))
