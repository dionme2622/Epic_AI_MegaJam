import unreal as u
from pathlib import Path
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
a=next(x for x in actors if x.get_actor_label()=="Stage1_Player")
lines=[str(a.get_actor_location()),str(a.get_actor_scale3d())]
for c in a.get_components_by_class(u.SceneComponent):
 lines.append(str((c.get_name(),c.get_class().get_name(),str(c.get_world_location()),str(c.get_world_scale()),str(c.get_relative_transform()))))
Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage2Workshop/player.txt").write_text("\n".join(lines))
