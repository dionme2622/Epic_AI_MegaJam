import unreal as u, json
from pathlib import Path
sub=u.get_editor_subsystem(u.EditorActorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=="/Game/DirectorCut/Stage/Stage2.Stage2"
rows=[]
for a in sub.get_all_level_actors():
 p,e=a.get_actor_bounds(False)
 row={"label":a.get_actor_label(),"class":a.get_class().get_name(),"path":a.get_path_name(),"location":a.get_actor_location().to_tuple(),"bounds":p.to_tuple(),"extent":e.to_tuple(),"folder":str(a.get_folder_path()),"tags":[str(t) for t in a.tags]}
 comps=[]
 for c in a.get_components_by_class(u.StaticMeshComponent):
  mesh=c.get_editor_property("static_mesh")
  comps.append({"name":c.get_name(),"mesh":mesh.get_path_name() if mesh else None,"loc":c.get_world_location().to_tuple(),"scale":c.get_world_scale().to_tuple(),"visible":c.get_editor_property("visible"),"collision":str(c.get_collision_profile_name()),"materials":[str(c.get_material(i).get_path_name()) if c.get_material(i) else None for i in range(c.get_num_materials())]})
 row["meshes"]=comps
 rows.append(row)
Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage2Workshop/audit.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2))

