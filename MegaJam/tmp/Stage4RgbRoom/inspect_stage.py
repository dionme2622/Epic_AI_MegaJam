import unreal as u
from pathlib import Path
sub=u.get_editor_subsystem(u.EditorActorSubsystem)
rows=[]
for a in sub.get_all_level_actors():
    loc=a.get_actor_location()
    label=a.get_actor_label()
    if loc.x>1280 and label not in ("Shadow Rehearsal","Retake_Deck_01"):
        continue
    p,d=a.get_actor_bounds(False)
    rows.append((label,a.get_class().get_name(),tuple(loc.to_tuple()),tuple(p.to_tuple()),tuple(d.to_tuple())))
    if label in ("Color_Controller","Color_ExitDoor"):
        for c in a.get_components_by_class(u.SceneComponent):
            row=(c.get_name(),tuple(c.get_world_location().to_tuple()),tuple(c.get_world_scale().to_tuple()))
            if isinstance(c,u.StaticMeshComponent):
                row+= (str(c.get_editor_property("static_mesh")),str(c.get_material(0)),str(c.get_collision_profile_name()))
            rows.append(row)
Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4RgbRoom/actors.txt").write_text("\n".join(map(str,rows)),encoding="utf8")
