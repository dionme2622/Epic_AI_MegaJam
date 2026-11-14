import unreal as u
from pathlib import Path
rows=[]
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
    label=a.get_actor_label()
    if a.get_folder_path() and "Shadow Rehearsal" in str(a.get_folder_path()):
        p,d=a.get_actor_bounds(False)
        rows.append(f"{label} {a.get_actor_location()} BOUNDS {p} +/- {d}")
        if label=="Shadow Rehearsal":
            for c in a.get_components_by_class(u.StaticMeshComponent):
                mesh=c.get_editor_property("static_mesh")
                rows.append(f"  {c.get_name()} {c.get_world_location()} {mesh.get_bounding_box() if mesh else None}")
            for name in ["SM_Vault_KnightGreave","SM_Vault_BellJar","SM_Vault_PlatformFaces"]:
                mesh=u.load_asset(f"/Game/Stage4Integrated/Theatre/{name}")
                rows.append(f"  {name} {mesh.get_bounding_box()}")
l=u.get_editor_subsystem(u.LevelEditorSubsystem)
eye=u.Vector(3100,3105,515)
look=u.Vector(3100,-15,61)
l.set_level_viewport_camera_info(eye,u.MathLibrary.find_look_at_rotation(eye,look),l.get_active_viewport_config_key())
l.editor_invalidate_viewports()
Path(r'C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4Theatre/bounds.txt').write_text('\n'.join(rows), encoding='utf-8')
