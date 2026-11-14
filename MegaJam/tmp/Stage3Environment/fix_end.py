import unreal as u
e=u.get_editor_subsystem(u.UnrealEditorSubsystem)
le=u.get_editor_subsystem(u.LevelEditorSubsystem)
api=u.get_editor_subsystem(u.EditorActorSubsystem)
lib=u.EditorAssetLibrary
assert e.get_editor_world().get_path_name()=="/Game/DirectorCut/Stage/Stage3_.Stage3_"
assert le.load_level("/Game/Stage3Integrated/Sections/L_Resolution")
allactors=api.get_all_level_actors()
boxes=[a for a in allactors if a.get_actor_label()=="Cube" and abs(a.get_actor_location().x-1870)<1]
assert len(boxes)==1,boxes
box=boxes[0]
wood=lib.load_asset("/Game/Stage4Integrated/Theatre/M10_Plank")
gold=lib.load_asset("/Game/Stage4Integrated/Theatre/M07_Tarnish")
cube=lib.load_asset("/Engine/BasicShapes/Cube")
assert wood and gold and cube
box.static_mesh_component.set_material(0,wood)
box.set_actor_label("Archive Transport Crate")
box.set_folder_path("Stage3/Resolution Archive")
for label,location,scale in [
 ("Archive Crate Front Band",(1870,41,50),(1.02,.025,.075)),
 ("Archive Crate Left Band",(1835,41,50),(.065,.025,1.02)),
 ("Archive Crate Right Band",(1905,41,50),(.065,.025,1.02)),
 ("Archive Crate Lid Band A",(1835,-10,101),(.065,1.02,.025)),
 ("Archive Crate Lid Band B",(1905,-10,101),(.065,1.02,.025)),
]:
 a=api.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*location),u.Rotator())
 assert a
 a.set_actor_label(label);a.set_folder_path("Stage3/Resolution Archive")
 c=a.static_mesh_component;c.set_static_mesh(cube);c.set_material(0,gold);c.set_collision_profile_name("NoCollision");c.set_cast_shadow(False)
 a.set_actor_scale3d(u.Vector(*scale))
assert le.save_current_level()
assert le.load_level("/Game/DirectorCut/Stage/Stage3_")
assert e.get_editor_world().get_path_name()=="/Game/DirectorCut/Stage/Stage3_.Stage3_"
wall=lib.load_asset("/Game/Stage4Integrated/Theatre/SM_Vault_CenterWall")
assert wall
existing=[a for a in api.get_all_level_actors() if a.get_actor_label()=="Archive Wall 7"]
if existing:
 a=existing[0]
else:
 a=api.spawn_actor_from_class(u.StaticMeshActor,u.Vector(6045,5,0),u.Rotator())
 a.set_actor_label("Archive Wall 7");a.set_folder_path("Stage3/Film Archive/Architecture")
 c=a.static_mesh_component;c.set_static_mesh(wall);c.set_collision_profile_name("NoCollision");c.set_cast_shadow(False);c.set_editor_property("affect_distance_field_lighting",False)
assert le.save_current_level()
u.log("STAGE3 END ARCHIVE WALL AND CRATE SAVED")
