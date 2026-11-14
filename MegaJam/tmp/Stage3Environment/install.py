import unreal as u,json
from pathlib import Path
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert w.get_path_name()=="/Game/DirectorCut/Stage/Stage3_.Stage3_"
api=u.get_editor_subsystem(u.EditorActorSubsystem)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
assets=u.EditorAssetLibrary
tool=u.AssetToolsHelpers.get_asset_tools()
folder="/Game/Stage3Integrated/Archive"
source=Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage3Environment")
mats={n.rsplit("/",1)[-1].split(".")[0]:assets.load_asset(n) for n in assets.list_assets("/Game/Stage4Integrated/Theatre",False) if n.rsplit("/",1)[-1].startswith("M")}
names=[f"SM_Stage3_FilmScene_{i:02}" for i in range(1,4)]
tasks=[]
for name in names:
 if not assets.does_asset_exist(folder+"/"+name):
  t=u.AssetImportTask()
  t.filename=str(source/(name+".fbx"));t.destination_path=folder;t.destination_name=name;t.automated=True;t.save=False
  opt=u.FbxImportUI();opt.import_as_skeletal=False;opt.import_materials=False;opt.import_textures=False
  opt.static_mesh_import_data.auto_generate_collision=False;opt.static_mesh_import_data.combine_meshes=True;t.options=opt;tasks.append(t)
if tasks:tool.import_asset_tasks(tasks)
for name in names:
 m=assets.load_asset(folder+"/"+name);assert m,name
 for i,slot in enumerate(m.get_editor_property("static_materials")):
  key=str(slot.get_editor_property("imported_material_slot_name"));assert key in mats,(name,key)
  m.set_material(i,mats[key])
 assert assets.save_loaded_asset(m,only_if_is_dirty=False)
existing={a.get_actor_label():a for a in api.get_all_level_actors()}
created=[]
def spawn_mesh(label,meshpath,loc,scale=(1,1,1),foldername="Architecture"):
 a=existing.get(label)
 if not a:
  a=api.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*loc),u.Rotator());assert a,label
  a.set_actor_label(label);a.set_folder_path("Stage3/Film Archive/"+foldername);created.append(a)
 c=a.static_mesh_component;c.set_static_mesh(assets.load_asset(meshpath));assert c.get_editor_property("static_mesh"),meshpath
 a.set_actor_location(u.Vector(*loc),False,True);a.set_actor_scale3d(u.Vector(*scale))
 c.set_cast_shadow(False);c.set_collision_profile_name("NoCollision");c.set_editor_property("affect_distance_field_lighting",False)
 return a
def light(label,xyz,color,intensity,radius):
 a=existing.get(label)
 if not a:
  a=api.spawn_actor_from_class(u.PointLight,u.Vector(*xyz),u.Rotator());assert a,label
  a.set_actor_label(label);a.set_folder_path("Stage3/Film Archive/Lighting");created.append(a)
 c=a.get_component_by_class(u.PointLightComponent)
 c.set_mobility(u.ComponentMobility.MOVABLE);c.set_intensity(intensity);c.set_light_color(u.LinearColor(*color,1));c.set_attenuation_radius(radius);c.set_cast_shadows(False)
 return a
try:
 wall="/Game/Stage4Integrated/Theatre/SM_Vault_CenterWall"
 for i,mid in enumerate([150,1420,2690,3960,5230,6500]):
  spawn_mesh(f"Archive Wall {i+1}",wall,(mid-1725,5,0))
 arch="/Game/Stage4Integrated/Theatre/SM_Vault_Architecture"
 # The pillars stand behind camera controls and signs.
 for i,x in enumerate([-450,3270]):
  spawn_mesh(f"Archive Masonry {i+1}",arch,(x,-8,0),(1,1,1))
 floor="/Game/Stage4Integrated/LightingGallery/SM_RGB_GalleryFloor"
 for i,x in enumerate([0,1800,3300,4650,7000]):
  spawn_mesh(f"Archive Stone Floor {i+1}",floor,(x,0,-.8))
 # The final interval contains five moving collision tiles. Hide all overlapping floor surfaces.
 # The fourth floor is clipped after importing below, so there is no visual bridge over those tiles.
 a=existing.get("Archive Stone Floor 4")
 if not a:a=next((x for x in created if x.get_actor_label()=="Archive Stone Floor 4"),None)
 if a:
  a.set_actor_scale3d(u.Vector(.45,1,1))
  a.set_actor_location(u.Vector(4700,0,-.8),False,True)
 curtain="/Game/Stage4Integrated/LightingGallery/SM_RGB_Curtains"
 spawn_mesh("Archive Focus Curtains",curtain,(10,-12,24))
 props="/Game/Stage4Integrated/LightingGallery/SM_RGB_WallProps"
 spawn_mesh("Archive Prop Shelves",props,(920,-4,-4))
 spawn_mesh("Archive Film Shelves",props,(3680,-4,-4))
 # Third scene is intentionally disjoint from the playable path and switch hardware.
 for i,x in enumerate([2250,2800,3350],1):
  a=spawn_mesh(f"Stage3 Film Scene {i}",f"{folder}/SM_Stage3_FilmScene_{i:02}",(x,-100,343),(.77,1,.77),"Puzzle art")
  a.tags=[u.Name(f"Stage3FilmScene{i}")]
  a.set_actor_hidden_in_game(True)
 for n,pos,color,intensity in [
  ("Focus Work Light",(360,120,260),(1,.57,.32),75),
  ("Reel Stage Fill",(2450,150,290),(1,.52,.34),65),
  ("Film Stage Fill",(3350,120,300),(.60,.45,1.),60),
  ("Mosaic Corridor Fill",(5750,140,245),(.54,.47,.93),55),
  ("Archive Exit Fill",(6850,155,270),(1,.58,.31),75),
 ]:light(n,pos,color,intensity,590)
 assert level.save_current_level()
 print("STAGE3 ARCHIVE BACKGROUND SAVED",len(created))
except Exception:
 for a in reversed(created):
  api.destroy_actor(a)
 raise
