"""Assemble the two-act shadow stage in the existing Stage4 world."""
import ast
import json
from pathlib import Path
import unreal as u

ROOT = Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam")
GEOMETRY = ROOT/"tmp/Stage4Theatre"
MESH_PATH = "/Game/Stage4Integrated/Theatre"
MAP = "/Game/DirectorCut/Stage/Stage4"
SOURCE = ROOT/"SourceAssets/Stage4ShadowTheatre/build_theatre.py"
PALETTE = ast.literal_eval(next(n.value for n in ast.parse(SOURCE.read_text(encoding="utf-8-sig")).body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=="PALETTE"))
NAMES = [
    "WestWall", "CenterWall", "EastWall", "Architecture", "PlatformFaces", "FlyRail",
    "WestFlyBar", "EastFlyBar", "Drapery", "Props", "Pedestal", "BellJar", "Cue", "WestWorkLines", "EastWorkLines",
    "KnightGreave",
]
REPORT = GEOMETRY/"assembly_report.json"
ASSETS = u.EditorAssetLibrary
MATERIAL = u.MaterialEditingLibrary
TOOLS = u.AssetToolsHelpers.get_asset_tools()
ACTORS = u.get_editor_subsystem(u.EditorActorSubsystem)
LEVEL = u.get_editor_subsystem(u.LevelEditorSubsystem)

def asset(name):
    return ASSETS.load_asset(f"{MESH_PATH}/{name}")

def vector(location):
    return u.Vector(*location)

def load_material(name, values):
    existing = asset(name) if ASSETS.does_asset_exist(f"{MESH_PATH}/{name}") else None
    if existing:
        return existing
    r,g,b,rough,metal = values
    m = TOOLS.create_asset(name, MESH_PATH, u.Material, u.MaterialFactoryNew())
    if name == "M15_Glass":
        m.set_editor_property("blend_mode",u.BlendMode.BLEND_TRANSLUCENT)
        m.set_editor_property("shading_model",u.MaterialShadingModel.MSM_UNLIT)
        m.set_editor_property("two_sided",True)
    c = MATERIAL.create_material_expression(m,u.MaterialExpressionConstant3Vector,-340,0)
    c.set_editor_property("constant",u.LinearColor(r,g,b,1))
    if name in ("M15_Glass","M14_Lamp","M16_Reflect"):
        multiply = MATERIAL.create_material_expression(m,u.MaterialExpressionMultiply,-120,0)
        MATERIAL.connect_material_expressions(c,"",multiply,"A")
        multiply.set_editor_property("const_b",2.15 if name=="M14_Lamp" else .52)
        MATERIAL.connect_material_property(multiply,"",u.MaterialProperty.MP_EMISSIVE_COLOR)
    if name == "M15_Glass":
        fresnel = MATERIAL.create_material_expression(m,u.MaterialExpressionFresnel,-350,240)
        fresnel.set_editor_property("exponent",3.8)
        opacity = MATERIAL.create_material_expression(m,u.MaterialExpressionMultiply,-120,230)
        MATERIAL.connect_material_expressions(fresnel,"",opacity,"A")
        opacity.set_editor_property("const_b",.30)
        MATERIAL.connect_material_property(opacity,"",u.MaterialProperty.MP_OPACITY)
    else:
        MATERIAL.connect_material_property(c,"",u.MaterialProperty.MP_BASE_COLOR)
        for i,(val,prop) in enumerate([(rough,u.MaterialProperty.MP_ROUGHNESS),(metal,u.MaterialProperty.MP_METALLIC)]):
            node = MATERIAL.create_material_expression(m,u.MaterialExpressionConstant,-250,160*(i+1))
            node.set_editor_property("r",val)
            MATERIAL.connect_material_property(node,"",prop)
    MATERIAL.layout_material_expressions(m)
    MATERIAL.recompile_material(m)
    ASSETS.save_loaded_asset(m,only_if_is_dirty=False)
    return m

def import_assets():
    # Save the actual slot names from the authored meshes. Material selection
    # stays in Unreal and can be adjusted without a geometry reimport.
    mats = {name:load_material(name,value) for name,value in PALETTE.items()}
    tasks = []
    for name in NAMES:
        n = f"SM_Vault_{name}"
        src = GEOMETRY/(n+".fbx")
        assert src.exists(), str(src)
        t = u.AssetImportTask()
        t.filename=str(src)
        t.destination_path=MESH_PATH
        t.destination_name=n
        t.automated=True
        t.replace_existing=True
        t.replace_existing_settings=True
        t.save=False
        options=u.FbxImportUI()
        options.import_as_skeletal=False
        options.import_materials=False
        options.import_textures=False
        options.static_mesh_import_data.combine_meshes=True
        options.static_mesh_import_data.auto_generate_collision=False
        t.options=options
        tasks.append(t)
    TOOLS.import_asset_tasks(tasks)
    for name in ("S_Vault_FlyRatchet","S_Vault_Recovery"):
        if not ASSETS.does_asset_exist(f"{MESH_PATH}/{name}"):
            task = u.AssetImportTask()
            task.filename = str(GEOMETRY/(name+".wav"))
            task.destination_path = MESH_PATH
            task.destination_name = name
            task.automated = True
            task.save = True
            TOOLS.import_asset_tasks([task])
            assert asset(name), name
    for name in NAMES:
        mesh=asset(f"SM_Vault_{name}")
        assert mesh, name
        slots=mesh.get_editor_property("static_materials")
        for k,slot in enumerate(slots):
            key=str(slot.get_editor_property("imported_material_slot_name"))
            if key not in mats:
                key=str(slot.get_editor_property("material_slot_name"))
            if key not in mats:
                raise RuntimeError(f"Unknown material in {name}: {key}")
            mesh.set_material(k,mats[key])
        ASSETS.save_loaded_asset(mesh,only_if_is_dirty=False)

def spawn(cls,name,location=(0,0,0),rotation=(0,0,0),folder="Environment"):
    a=ACTORS.spawn_actor_from_class(cls,vector(location),u.Rotator(*rotation))
    assert a, name
    a.set_actor_label(name)
    a.set_folder_path(f"Stage4/Shadow Rehearsal/{folder}")
    return a

def place(name,label=None,location=(1670,0,0),cast=True):
    a=spawn(u.StaticMeshActor,label or name,location)
    c=a.static_mesh_component
    c.set_static_mesh(asset(f"SM_Vault_{name}"))
    c.set_collision_profile_name("NoCollision")
    c.set_cast_shadow(cast)
    c.set_editor_property("affect_distance_field_lighting",False)
    return a

def cm(x,y,z):
    return (1670+x,y,z)

def accent(name,location,intensity,tone,range_):
    a=spawn(u.PointLight,name,cm(*location),folder="Lighting")
    light=a.get_component_by_class(u.PointLightComponent)
    light.set_mobility(u.ComponentMobility.MOVABLE)
    light.set_editor_property("intensity_units",u.LightUnits.CANDELAS)
    light.set_intensity(intensity)
    light.set_light_color(u.LinearColor(*tone,1))
    light.set_attenuation_radius(range_)
    light.set_cast_shadows(False)
    return a

def project(name,source,target,intensity):
    pos,aim=vector(cm(*source)),vector(cm(*target))
    rotation=u.MathLibrary.find_look_at_rotation(pos,aim)
    a=ACTORS.spawn_actor_from_class(u.SpotLight,pos,rotation)
    a.set_actor_label(name)
    a.set_folder_path("Stage4/Shadow Rehearsal/Lighting")
    light=a.get_component_by_class(u.SpotLightComponent)
    light.set_mobility(u.ComponentMobility.MOVABLE)
    light.set_editor_property("intensity_units",u.LightUnits.CANDELAS)
    light.set_intensity(intensity)
    light.set_light_color(u.LinearColor(1,.66,.37,1))
    light.set_attenuation_radius(1340)
    light.set_inner_cone_angle(24)
    light.set_outer_cone_angle(41)
    light.set_editor_property("source_radius",4.0)
    light.set_cast_shadows(True)
    return a

PLATFORMS=[(-475,350,0),(440,580,0),(680,820,22),(915,1080,37),(1190,1534,0),
           (1644,1799,35),(1900,2188,18),(2294,2455,0),(2560,3330,0)]

def collision(name,location,size):
    a=spawn(u.StaticMeshActor,name,cm(*location),folder="Collision")
    c=a.static_mesh_component
    c.set_static_mesh(ASSETS.load_asset("/Engine/BasicShapes/Cube"))
    a.set_actor_scale3d(vector(tuple(v/100 for v in size)))
    c.set_visibility(False)
    c.set_cast_shadow(False)
    c.set_collision_profile_name("BlockAll")
    return a

def show_level():
    eye=vector(cm(1410,3105,515))
    look=vector(cm(1410,-15,61))
    LEVEL.set_level_viewport_camera_info(eye,u.MathLibrary.find_look_at_rotation(eye,look),LEVEL.get_active_viewport_config_key())
    LEVEL.editor_invalidate_viewports()

def assemble():
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    assert world.get_path_name().split(".")[0]==MAP, world
    before=ACTORS.get_all_level_actors()
    old=[a for a in before if a.get_actor_label()=="Stage4_ShadowStage"]
    original=[a for a in before if a.get_actor_label()=="Color_ExitDoor"]
    assert len(old) <= 1 and len(original)==1, (old,original)
    cls=u.load_class(None,"/Script/MegaJam.Stage4ShadowTheatre")
    assert cls, "Stage4ShadowTheatre C++ class not loaded"
    assemble_staged=[]
    try:
        theatre=spawn(cls,"Shadow Rehearsal",cm(0,0,0),folder="Puzzle")
        assemble_staged.append(theatre)
        theatre.set_editor_property("EntranceDoor",original[0])
        theatre.set_editor_property("KnightGreave",asset("SM_Vault_KnightGreave"))
        theatre.set_editor_property("RailCue",asset("S_Vault_FlyRatchet"))
        theatre.set_editor_property("RecoveryCue",asset("S_Vault_Recovery"))
        components = {
            "WestRig":"WestFlyBar","EastRig":"EastFlyBar","WestMarker":"Cue","EastMarker":"Cue",
            "Glass":"BellJar","WestGuide":"WestWorkLines","EastGuide":"EastWorkLines"
        }
        for component,mesh in components.items():
            c=theatre.get_editor_property(component)
            c.set_static_mesh(asset("SM_Vault_"+mesh))
        theatre.get_editor_property("Exhibit").set_static_mesh(ASSETS.load_asset("/Game/DirectorCut/Dragon/SM_Dragon_Lower"))
        for name in ["WestWall","CenterWall","EastWall","Architecture","PlatformFaces","FlyRail","Drapery","Props","Pedestal"]:
            assemble_staged.append(place(name,cast=name in ("Drapery",)))
        for i,(a,b,z) in enumerate(PLATFORMS):
            assemble_staged.append(collision(f"Landing_{i+1:02}",((a+b)/2,0,z-15),(b-a,158,30)))
        assemble_staged.append(collision("EastBoundary",(3342,0,126),(25,213,260)))
        assemble_staged.append(project("West_Silhouette_Key",(280,580,309),(865,-276,184),29500))
        assemble_staged.append(project("East_Silhouette_Key",(2290,565,291),(1740,-276,158),28500))
        for key,loc,intensity,color,reach in [
            ("West_WarmWing",(4,178,232),610,(1,.54,.26),625),
            ("West_WorkLight",(612,92,177),550,(.47,.56,.89),495),
            ("Center_MarkLight",(1360,76,177),980,(1,.55,.24),570),
            ("East_WorkLight",(2061,112,164),630,(.50,.54,.86),560),
            ("Exhibit_WarmWing",(3030,158,210),1250,(1,.42,.26),690),
            ("Understage_Fill",(1460,138,-210),760,(.44,.36,.65),1660),
        ]:
            assemble_staged.append(accent(key,loc,intensity,color,reach))
        theatre.tags=["Stage4ShadowRehearsal"]
    except Exception:
        for a in reversed(assemble_staged):
            ACTORS.destroy_actor(a)
        raise
    if old:
        assert ACTORS.destroy_actor(old[0]), "Could not remove the old shadow section"
    assert LEVEL.save_current_level()
    show_level()
    REPORT.write_text(json.dumps({"world":world.get_path_name(),"actors":[a.get_actor_label() for a in assemble_staged]}, indent=2))

if (GEOMETRY/"assets_only.txt").exists():
    import_assets()
    u.log("SHADOW THEATRE ASSETS READY")
else:
    assemble()
    u.log("SHADOW THEATRE LEVEL SAVED")
