import json
from pathlib import Path
import unreal as u

base=Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4RgbRoom")
lib=u.EditorAssetLibrary
actor_api=u.get_editor_subsystem(u.EditorActorSubsystem)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=="/Game/DirectorCut/Stage/Stage4.Stage4", world
actors={a.get_actor_label():a for a in actor_api.get_all_level_actors()}
controller=actors["Color_Controller"]
door=actors["Color_ExitDoor"]
assert controller.get_editor_property("bUseRgbCalibration")
assert controller.get_editor_property("ExitDoor")==door
assert "Shadow Stand-In" in actors and "Shadow Rehearsal" in actors
theatre="/Game/Stage4Integrated/Theatre"
dest="/Game/Stage4Integrated/LightingGallery"
tools=u.AssetToolsHelpers.get_asset_tools()
edit=u.MaterialEditingLibrary

def asset(name,path=theatre):
    full=f"{path}/{name}"
    return lib.load_asset(full) if lib.does_asset_exist(full) else None

def create_lens(name,color):
    m=asset(name,dest)
    if m:
        return m
    m=tools.create_asset(name,dest,u.Material,u.MaterialFactoryNew())
    m.set_editor_property("shading_model",u.MaterialShadingModel.MSM_UNLIT)
    c=edit.create_material_expression(m,u.MaterialExpressionConstant3Vector,-200,0)
    c.set_editor_property("constant",u.LinearColor(*color,1))
    edit.connect_material_property(c,"",u.MaterialProperty.MP_EMISSIVE_COLOR)
    edit.recompile_material(m)
    assert lib.save_loaded_asset(m,only_if_is_dirty=False)
    return m

mats={n.rsplit("/",1)[-1].split(".")[0]:lib.load_asset(n) for n in lib.list_assets(theatre,False)
      if n.rsplit("/",1)[-1].startswith("M")}
for n,c in {"M22_RGB_Red":(1.3,.035,.055),"M23_RGB_Green":(.045,.93,.16),"M24_RGB_Blue":(.035,.25,1.42)}.items():
    mats[n]=create_lens(n,c)

names=("StoneGallery","GalleryFloor","Curtains","LightConsole","WallProps","GateFrame","Gate")
tasks=[]
for n in names:
    name="SM_RGB_"+n
    if asset(name,dest) and n not in ("GalleryFloor","GateFrame"):
        continue
    f=base/(name+".fbx")
    assert f.is_file(), f
    t=u.AssetImportTask()
    t.filename=str(f)
    t.destination_name=name
    t.destination_path=dest
    t.automated=True
    t.save=False
    t.replace_existing=True
    t.replace_existing_settings=True
    options=u.FbxImportUI()
    options.import_as_skeletal=False
    options.import_materials=False
    options.import_textures=False
    options.static_mesh_import_data.auto_generate_collision=False
    options.static_mesh_import_data.combine_meshes=True
    t.options=options
    tasks.append(t)
if tasks:
    tools.import_asset_tasks(tasks)
meshes={}
for n in names:
    m=asset("SM_RGB_"+n,dest)
    assert m,n
    for i,s in enumerate(m.get_editor_property("static_materials")):
        key=str(s.get_editor_property("imported_material_slot_name"))
        assert key in mats,(n,key)
        m.set_material(i,mats[key])
    assert lib.save_loaded_asset(m,only_if_is_dirty=False)
    meshes[n]=m

def actor(cls,name,location=(0,0,0)):
    a=actors.get(name)
    if not a:
        a=actor_api.spawn_actor_from_class(cls,u.Vector(*location),u.Rotator())
        assert a,name
        a.set_actor_label(name)
        a.set_folder_path("Stage4/Vault Lighting Gallery")
        actors[name]=a
    return a

for n in names[:-1]:
    a=actor(u.StaticMeshActor,"Vault Gallery "+n)
    c=a.static_mesh_component
    c.set_static_mesh(meshes[n])
    c.set_collision_profile_name("NoCollision")
    c.set_cast_shadow(False)
    c.set_editor_property("affect_distance_field_lighting",False)

for name,(x,y,z),color,intensity,range_ in [
    ("Console Key",(3,112,229),(1,.68,.37),72,536),
    ("West Fill",(-355,164,326),(.49,.44,.75),68,600),
    ("Reel Cabinet",(483,125,188),(1,.58,.32),71,500),
    ("Reel Spill",(648,115,304),(.52,.38,.77),60,550),
    ("Gate Key",(1094,140,239),(1,.6,.27),66,585),
]:
    a=actor(u.PointLight,"Vault Gallery "+name,(x,y,z))
    c=a.get_component_by_class(u.PointLightComponent)
    c.set_mobility(u.ComponentMobility.MOVABLE)
    c.set_editor_property("intensity_units",u.LightUnits.CANDELAS)
    c.set_intensity(intensity)
    c.set_light_color(u.LinearColor(*color,1))
    c.set_attenuation_radius(range_)
    c.set_cast_shadows(False)

# Keep the interaction, solved state and moving collision on the original actors.
# The visible grate rides the original moving door via attachment.
gate=actor(u.StaticMeshActor,"Vault Gallery Moving Gate",(1150,0,150))
gate.static_mesh_component.set_mobility(u.ComponentMobility.MOVABLE)
gate.static_mesh_component.set_static_mesh(meshes["Gate"])
gate.static_mesh_component.set_collision_profile_name("NoCollision")
gate.static_mesh_component.set_cast_shadow(False)
gate.detach_from_actor(u.DetachmentRule.KEEP_WORLD,u.DetachmentRule.KEEP_WORLD,u.DetachmentRule.KEEP_WORLD)
gate.set_actor_location(u.Vector(1150,0,150),False,True)
gate.attach_to_actor(door,"",u.AttachmentRule.KEEP_WORLD,u.AttachmentRule.KEEP_WORLD,u.AttachmentRule.KEEP_WORLD,False)
door.get_editor_property("Mesh").set_visibility(False)
floor=actors["Color_Floor"].static_mesh_component
floor.set_visibility(False)
floor.set_cast_shadow(False)
for name in ("Color_Backdrop","Color_Set_Wood","Color_Set_Brass","Color_Set_Curtain"):
    if name in actors:
        assert actor_api.destroy_actor(actors[name]),name
for component in ("Frame","SignalPanel","RecordBackground","Dial1","Dial2","Dial3","Dial4"):
    controller.get_editor_property(component).set_static_mesh(None)
placard=controller.get_editor_property("RestoredRecord")
placard.set_relative_location(u.Vector(0,-125,232),False,True)
placard.set_world_size(14.5)
placard.set_text_render_color(u.Color(238,194,112,255))
controller.get_editor_property("PuzzleCamera").set_relative_location(u.Vector(0,545,223),False,True)
camera=controller.get_editor_property("PuzzleCamera")
camera.set_field_of_view(53)
camera.set_relative_rotation(u.Rotator(0,-6,-90),False,True)

a=actors["Color_Instructions"]
a.set_actor_location_and_rotation(u.Vector(0,-167,279),u.Rotator(0,0,90),False,True)
c=a.get_component_by_class(u.TextRenderComponent)
c.set_text("E   INTERACT")
c.set_world_size(13)
c.set_horizontal_alignment(u.HorizTextAligment.EHTA_CENTER)
c.set_text_render_color(u.Color(245,216,156,255))
a.set_folder_path("Stage4/Vault Lighting Gallery")
cube=lib.load_asset("/Engine/BasicShapes/Cube")
for name,location,scale,collision in [
    ("West Return",(-603,-32,176),(1.05,5.20,7.0),False),
    ("Lower Backing",(405,-318,-270),(20,.85,4.65),False),
    ("End Stop",(-449,0,75),(.18,1.8,1.55),True),
]:
    a=actor(u.StaticMeshActor,"Vault Gallery "+name,location)
    c=a.static_mesh_component
    c.set_static_mesh(cube)
    a.set_actor_scale3d(u.Vector(*scale))
    c.set_material(0,mats["M01_Bedrock"])
    c.set_cast_shadow(False)
    c.set_visibility(not collision)
    c.set_collision_profile_name("BlockAll" if collision else "NoCollision")

assert level.save_current_level()
eye=u.Vector(438,1610,370)
aim=u.Vector(438,-80,155)
level.set_level_viewport_camera_info(eye,u.MathLibrary.find_look_at_rotation(eye,aim),level.get_active_viewport_config_key())
level.editor_invalidate_viewports()
u.log("STAGE4 RGB GALLERY SAVED")


