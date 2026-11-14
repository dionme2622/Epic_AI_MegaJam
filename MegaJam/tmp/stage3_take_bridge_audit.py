import json
from pathlib import Path
import unreal as u

levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
paths = ['/Game/Stage3Integrated/Sections/L_Bloom', '/Game/Stage3Integrated/Sections/L_Resolution', '/Game/DirectorCut/Stage/Stage3_']
report = {}
for path in paths:
    assert levels.load_level(path)
    report[path] = []
    for actor in sorted(actors.get_all_level_actors(), key=lambda a: a.get_actor_label()):
        location = actor.get_actor_location().to_tuple()
        bounds = tuple(v.to_tuple() for v in actor.get_actor_bounds(False))
        report[path].append((actor.get_actor_label(), actor.get_class().get_name(), location, bounds))
Path(r'C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/stage3_take_bridge_actors.json').write_text(json.dumps(report), encoding='utf8')
u.log('STAGE3 TAKE BRIDGE AUDIT COMPLETE')
