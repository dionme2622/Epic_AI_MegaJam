import unreal as u
from pathlib import Path
D="/Game/Stage2Workshop"
lib=u.EditorAssetLibrary
asset_tools=u.AssetToolsHelpers.get_asset_tools()
edit=u.MaterialEditingLibrary
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=="/Game/DirectorCut/Stage/Stage2.Stage2"
mats={}
for name,c in [("WorkshopFloorA",(.095,.065,.12)),("WorkshopFloorB",(.13,.095,.155)),("WorkshopFloorC",(.075,.055,.10))]:
 m=asset_tools.create_asset("M_"+name,D,u.Material,u.MaterialFactoryNew())
 assert m
 color=edit.create_material_expression(m,u.MaterialExpressionConstant3Vector,-200,0)
 color.set_editor_property("constant",u.LinearColor(*c,1))
 edit.connect_material_property(color,"",u.MaterialProperty.MP_BASE_COLOR)
 rough=edit.create_material_expression(m,u.MaterialExpressionConstant,-200,160)
 rough.set_editor_property("r",.85)
 edit.connect_material_property(rough,"",u.MaterialProperty.MP_ROUGHNESS)
 edit.recompile_material(m)
 assert lib.save_loaded_asset(m,only_if_is_dirty=False)
 mats[name]=m
tasks=[]
for i in range(1,5):
 name=f"SM_Workshop_StoneFloor_{i:02}"
 task=u.AssetImportTask()
 task.filename=f"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage2Workshop/{name}.fbx"
 task.destination_path=D;task.destination_name=name;task.automated=True;task.save=False
 cfg=u.FbxImportUI()
 cfg.import_as_skeletal=False;cfg.import_materials=False;cfg.import_textures=False
 cfg.static_mesh_import_data.auto_generate_collision=False
 cfg.static_mesh_import_data.combine_meshes=True
 task.options=cfg;tasks.append(task)
asset_tools.import_asset_tasks(tasks)
for i in range(1,5):
 name=f"SM_Workshop_StoneFloor_{i:02}"
 mesh=lib.load_asset(f"{D}/{name}")
 assert mesh
 for k,slot in enumerate(mesh.get_editor_property("static_materials")):
  key=str(slot.get_editor_property("imported_material_slot_name"))
  assert key in mats,(name,key)
  mesh.set_material(k,mats[key])
 assert lib.save_loaded_asset(mesh,only_if_is_dirty=False)
 a=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,0,0),u.Rotator())
 a.set_actor_label(name.replace("SM_",""));a.set_folder_path("Stage2/Workshop/Scenery")
 c=a.static_mesh_component
 c.set_static_mesh(mesh);c.set_collision_profile_name("NoCollision");c.set_cast_shadow(False)
 c.set_editor_property("affect_distance_field_lighting",False)
assert level.save_current_level()
u.log("STAGE2 STONE FLOOR SAVED")
