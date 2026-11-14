import unreal as u,json
from pathlib import Path
e=u.get_editor_subsystem(u.UnrealEditorSubsystem);le=u.get_editor_subsystem(u.LevelEditorSubsystem);sub=u.get_editor_subsystem(u.EditorActorSubsystem)
assert e.get_editor_world().get_path_name()=="/Game/DirectorCut/Stage/Stage3_.Stage3_"
assert le.load_level("/Game/Stage3Integrated/Sections/L_Resolution")
cube=u.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
mat=u.EditorAssetLibrary.load_asset("/Game/Stage4Integrated/Theatre/M04_Porphyry")
tiles=[a for a in sub.get_all_level_actors() if a.get_actor_label() in ("Resolution_Tile_2","Resolution_Tile_4")]
assert len(tiles)==2
for a in tiles:
 p=a.get_actor_location();center,extent=a.get_actor_bounds(False)
 m=a.get_editor_property("Mesh")
 print("TILE",a.get_actor_label(),p,center,extent)
 m.set_collision_enabled(u.CollisionEnabled.NO_COLLISION);a.set_actor_hidden_in_game(True)
 b=sub.spawn_actor_from_class(u.StaticMeshActor,u.Vector(center.x,center.y,center.z),u.Rotator());b.set_actor_label("Archive Walkway "+a.get_actor_label());b.set_folder_path("Stage3/Resolution")
 c=b.static_mesh_component;c.set_static_mesh(cube);c.set_material(0,mat);c.set_collision_profile_name("BlockAll")
 b.set_actor_scale3d(u.Vector(extent.x*2/100,extent.y*2/100,extent.z*2/100))
assert le.save_current_level()
assert le.load_level("/Game/DirectorCut/Stage/Stage3_")
u.log("STAGE3 RESOLUTION WALKWAY SAVED")
