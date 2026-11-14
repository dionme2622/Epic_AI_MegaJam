import unreal as u
from pathlib import Path
actor=u.get_editor_subsystem(u.EditorActorSubsystem)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
asset=u.EditorAssetLibrary
def index():
 return {a.get_actor_label():a for a in actor.get_all_level_actors()}
assert level.load_level("/Game/Stage3Integrated/Sections/L_Bloom")
a=index()
p=a["Bloom_Controller"]
p.set_editor_property("bUseFilmEditing",True)
p.set_editor_property("FilmSources",[a["Bloom_Sign_Star"],a["Bloom_Sign_Moon"],a["Bloom_Sign_Sun"]])
scenes=[]
for i,x in enumerate((350,900,1450),1):
 name=f"Stage3 Film Scene {i}"
 scene=a.get(name)
 if not scene:
  scene=actor.spawn_actor_from_class(u.StaticMeshActor,u.Vector(x,-100,343),u.Rotator())
  scene.set_actor_label(name)
  scene.static_mesh_component.set_static_mesh(asset.load_asset(f"/Game/Stage3Integrated/Archive/SM_Stage3_FilmScene_{i:02}"))
  scene.static_mesh_component.set_collision_profile_name("NoCollision")
  scene.static_mesh_component.set_cast_shadow(False)
  scene.set_actor_scale3d(u.Vector(.77,1,.77))
  scene.tags=[u.Name(f"Stage3FilmScene{i}")]
 scene.set_actor_hidden_in_game(True)
 scenes.append(scene)
p.set_editor_property("FilmScenes",scenes)
if "Bloom_Instructions" in a:
 a["Bloom_Instructions"].get_component_by_class(u.TextRenderComponent).set_text("B  BLOOM   |   E  COLLECT FILM")
if "Bloom_ConsoleLabel" in a:
 a["Bloom_ConsoleLabel"].get_component_by_class(u.TextRenderComponent).set_text("E  EDIT FILM")
assert level.save_current_level()
assert level.load_level("/Game/Stage3Integrated/Sections/L_Resolution")
a=index()
p=a["Resolution_Controller"]
p.set_editor_property("bUseStationChoices",True)
p.set_editor_property("StationAnswers",[1,2,3])
p.set_editor_property("StationCheckpointOffsets",[u.Vector(210,0,55),u.Vector(400,0,55),u.Vector(720,0,55)])
p.set_editor_property("StationInteractionDistance",140.)
guides=[]
for i,(x,answer) in enumerate(((400,"1"),(720,"2"),(1040,"3")),1):
 label=f"Archive Resolution Choice {i}"
 marker=a.get(label)
 if not marker:
  marker=actor.spawn_actor_from_class(u.TextRenderActor,u.Vector(x,-210,186),u.Rotator(0,0,90))
  marker.set_actor_label(label)
  comp=marker.get_component_by_class(u.TextRenderComponent)
  comp.set_text(answer)
  comp.set_world_size(56)
  comp.set_text_render_color(u.Color(255,237,126,255))
  comp.set_horizontal_alignment(u.HorizTextAligment.EHTA_CENTER)
 guides.append(marker)
p.set_editor_property("GuidanceArrows",guides)
for i in range(1,4):
 if f"Resolution_Guide_{i}" in a:a[f"Resolution_Guide_{i}"].set_actor_hidden_in_game(True)
assert level.save_current_level()
assert level.load_level("/Game/DirectorCut/Stage/Stage3_")
a=index()
for i in range(1,4):
 if f"Stage3 Film Scene {i}" in a:
  assert actor.destroy_actor(a[f"Stage3 Film Scene {i}"])
crate=a.get("Archive Empty Crate")
if not crate:
 cls=u.load_class(None,"/Script/MegaJam.Stage3StorageCrate")
 assert cls
 crate=actor.spawn_actor_from_class(cls,u.Vector(6860,0,0),u.Rotator())
 crate.set_actor_label("Archive Empty Crate")
 crate.set_folder_path("Stage3/Film Archive/Story")
assert level.save_current_level()
print("STAGE3 PUZZLES CONFIGURED")
