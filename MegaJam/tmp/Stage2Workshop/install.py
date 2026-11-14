import unreal as u
from pathlib import Path
ROOT=Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam")
OUT=ROOT/"tmp/Stage2Workshop"
DEST="/Game/Stage2Workshop"
lib=u.EditorAssetLibrary
a=u.get_editor_subsystem(u.EditorActorSubsystem)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=="/Game/DirectorCut/Stage/Stage2.Stage2"
actors={x.get_actor_label():x for x in a.get_all_level_actors()}
for name in ["Stage1_Ground","Stage1_Backdrop","Stage1_Player","Stage1_PuzzleDirector","Stage1_WheelHigh","Stage1_WheelLow","Stage1_GearHigh","Stage1_GearLow","Stage1_Lift","Stage1_LiftCollider","Stage1_GateBarrier"]:
 assert name in actors,name
tools=u.AssetToolsHelpers.get_asset_tools()
edit=u.MaterialEditingLibrary
mats={}
for item in lib.list_assets("/Game/Stage4Integrated/Theatre",False):
 name=item.rsplit("/",1)[-1].split(".")[0]
 if name.startswith("M"):mats[name]=lib.load_asset(item)
for name,color,emissive in [
 ("WorkshopTeal",(.014,.13,.17),.0),
 ("WorkshopDeep",(.009,.045,.065),.0),
 ("WorkshopWire",(.17,.69,.73),.55),
 ("WorkshopCanvas",(.52,.35,.23),.0),
]:
 path=DEST+"/M_"+name
 mat=lib.load_asset(path) if lib.does_asset_exist(path) else tools.create_asset("M_"+name,DEST,u.Material,u.MaterialFactoryNew())
 if not mat:raise RuntimeError(name)
 edit.delete_all_material_expressions(mat)
 node=edit.create_material_expression(mat,u.MaterialExpressionConstant3Vector,-250,0)
 node.set_editor_property("constant",u.LinearColor(*color,1))
 edit.connect_material_property(node,"",u.MaterialProperty.MP_BASE_COLOR)
 if emissive:
  multi=edit.create_material_expression(mat,u.MaterialExpressionMultiply,-80,150)
  multi.set_editor_property("const_b",emissive)
  edit.connect_material_expressions(node,"",multi,"A")
  edit.connect_material_property(multi,"",u.MaterialProperty.MP_EMISSIVE_COLOR)
 edit.recompile_material(mat)
 assert lib.save_loaded_asset(mat,only_if_is_dirty=False)
 mats[name]=mat

names=[f"SM_Workshop_Background_{i:02}" for i in range(1,5)]+["SM_Workshop_WheelHall","SM_Workshop_Production","SM_Workshop_LiftHall","SM_Workshop_Trim","SM_Workshop_DragonWheelchair"]
tasks=[]
for name in names:
 file=OUT/(name+".fbx")
 assert file.is_file(),str(file)
 if lib.does_asset_exist(DEST+"/"+name):continue
 task=u.AssetImportTask()
 task.filename=str(file);task.destination_path=DEST;task.destination_name=name;task.automated=True;task.save=False
 cfg=u.FbxImportUI();cfg.import_as_skeletal=False;cfg.import_materials=False;cfg.import_textures=False
 cfg.static_mesh_import_data.combine_meshes=True;cfg.static_mesh_import_data.auto_generate_collision=False
 task.options=cfg
 tasks.append(task)
if tasks:tools.import_asset_tasks(tasks)
meshes={}
for name in names:
 mesh=lib.load_asset(DEST+"/"+name)
 assert mesh,name
 for i,slot in enumerate(mesh.get_editor_property("static_materials")):
  key=str(slot.get_editor_property("imported_material_slot_name"))
  assert key in mats,(name,key)
  mesh.set_material(i,mats[key])
 assert lib.save_loaded_asset(mesh,only_if_is_dirty=False),name
 meshes[name]=mesh

created=[]
try:
 with u.ScopedEditorTransaction("Stage2 workshop scenery"):
  for name in names[:-1]:
   label=name.replace("SM_","")
   assert label not in actors,label
   actor=a.spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,0,0),u.Rotator())
   assert actor,label
   actor.set_actor_label(label);actor.set_folder_path("Stage2/Workshop/Scenery");created.append(actor)
   c=actor.static_mesh_component
   c.set_static_mesh(meshes[name]);c.set_collision_profile_name("NoCollision")
   c.set_cast_shadow(False);c.set_editor_property("affect_distance_field_lighting",False)
  # Keep the collision from the original backdrop while replacing its visuals.
  actors["Stage1_Backdrop"].static_mesh_component.set_visibility(False)
  actors["Stage1_Backdrop"].static_mesh_component.set_cast_shadow(False)
  # Palette overrides apply only to the placed mesh, preserving other levels.
  ground=actors["Stage1_Ground"].static_mesh_component
  for i,name in enumerate(["M03_Slate","M02_Basalt","M04_Porphyry","M05_Capstone","M02_Basalt","M07_Tarnish"]):
   ground.set_material(i,mats[name])
  fill=actors["Stage1_BackgroundFill"].static_mesh_component
  fill.set_material(0,mats["WorkshopDeep"])
  # The separate box remains the lift's character movement base.
  actors["Stage1_LiftCollider"].static_mesh_component.set_visibility(False)
  # Attach the costume to this stage's placed pawn; it travels with the lift.
  player=actors["Stage1_Player"]
  chair=a.spawn_actor_from_class(u.StaticMeshActor,player.get_actor_location(),u.Rotator())
  assert chair
  chair.set_actor_label("Workshop_DragonWheelchair");chair.set_folder_path("Stage2/Workshop/Player");created.append(chair)
  c=chair.static_mesh_component
  c.set_mobility(u.ComponentMobility.MOVABLE);c.set_static_mesh(meshes["SM_Workshop_DragonWheelchair"])
  c.set_collision_profile_name("NoCollision");c.set_cast_shadow(False)
  chair.attach_to_actor(player,"",u.AttachmentRule.KEEP_WORLD,u.AttachmentRule.KEEP_WORLD,u.AttachmentRule.KEEP_WORLD,False)
  for x in [-760,75,850,1300,2370,4000,5480,6900,8180,8950,9560]:
   light=a.spawn_actor_from_class(u.PointLight,u.Vector(x,20,260),u.Rotator())
   assert light
   light.set_actor_label(f"Workshop_Lantern_{x:+05}");light.set_folder_path("Stage2/Workshop/Lighting");created.append(light)
   c=light.get_component_by_class(u.PointLightComponent)
   c.set_mobility(u.ComponentMobility.MOVABLE);c.set_editor_property("intensity_units",u.LightUnits.CANDELAS)
   c.set_intensity(115);c.set_light_color(u.LinearColor(1,.52,.20,1));c.set_attenuation_radius(400);c.set_cast_shadows(False)
  sun=actors["DirectionalLight"];sun.modify()
  light=sun.get_component_by_class(u.DirectionalLightComponent);light.modify()
  sun.set_actor_rotation(u.Rotator(0,-42,-120),False)
  light.set_intensity(1.4);light.set_editor_property("use_temperature",True)
  light.set_editor_property("temperature",7600.0);light.set_editor_property("light_source_angle",2.1)
  light.set_editor_property("indirect_lighting_intensity",.6)
 assert level.save_current_level()
except Exception:
 for item in reversed(created):a.destroy_actor(item)
 raise
u.log("STAGE2 WORKSHOP SAVED")
