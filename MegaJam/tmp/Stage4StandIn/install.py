import unreal as u
from pathlib import Path

BASE=Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4StandIn")
PATH="/Game/Stage4Integrated/Theatre"
ACTORS=u.get_editor_subsystem(u.EditorActorSubsystem)
LEVEL=u.get_editor_subsystem(u.LevelEditorSubsystem)
WORLD=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
LIB=u.EditorAssetLibrary
assert WORLD.get_path_name()=="/Game/DirectorCut/Stage/Stage4.Stage4"
cls=u.load_class(None,"/Script/MegaJam.Stage4ShadowStandIn")
assert cls
actors={a.get_actor_label():a for a in ACTORS.get_all_level_actors()}
old=actors["Shadow Rehearsal"]
assert old.get_editor_property("DeckScenery")
assert not old.get_editor_property("StandInPuzzle")
assert "Shadow Stand-In" not in actors
origin=4930.
exhibit=1990.
offset=origin+exhibit-(old.get_actor_location().x+2885.)
V=u.Vector

def asset(name):
    return LIB.load_asset(f"{PATH}/{name}")

def spawn(cls,label,x,y,z,category="Set"):
    a=ACTORS.spawn_actor_from_class(cls,V(origin+x,y,z),u.Rotator())
    assert a,label
    a.set_actor_label(label)
    a.set_folder_path("Stage4/Shadow Stand-In/"+category)
    made.append(a)
    return a

def geometry(label,name,x,y,z,s=(1,1,1),mat=None,collide=False,movable=False,hide=False,category="Set"):
    a=spawn(u.StaticMeshActor,label,x,y,z,category)
    c=a.static_mesh_component
    mesh=name if isinstance(name,u.StaticMesh) else asset(name)
    assert mesh,name
    c.set_mobility(u.ComponentMobility.MOVABLE if movable else u.ComponentMobility.STATIC)
    c.set_static_mesh(mesh)
    if mat:
        c.set_material(0,mat)
    a.set_actor_scale3d(V(*s))
    c.set_collision_profile_name("BlockAll" if collide else "NoCollision")
    c.set_cast_shadow(False)
    c.set_editor_property("affect_distance_field_lighting",False)
    c.set_visibility(not hide)
    return c

cube=LIB.load_asset("/Engine/BasicShapes/Cube")
cyl=LIB.load_asset("/Engine/BasicShapes/Cylinder")
brass=asset("M06_Gold")
dark=asset("M07_Tarnish")
metal=asset("M09_Iron")
stone=asset("M01_Bedrock")
slate=asset("M04_Porphyry")
glow=asset("M21_RetakeCue")
sheen=asset("M14_Lamp")

def beam(a,b,thick,material,label):
    delta=b-a
    mid=(a+b)*.5
    c=geometry(label,cube,mid.x,mid.y,mid.z,(delta.length()/100,thick/100,thick/100),material)
    c.get_owner().set_actor_rotation(delta.rotator(),False)
    return c

def deck(label,x,w,top,source="SM_Vault_RetakeDeck_06",moving=False):
    mesh=asset(source)
    bounds=mesh.get_bounding_box()
    center=(bounds.min.x+bounds.max.x)*.5
    factor=w/(bounds.max.x-bounds.min.x)
    art=geometry(label+" Stone",mesh,x-center*factor,0,top-bounds.max.z+2,(factor,1,1),
        movable=moving,category="Platforms")
    collider=geometry(label+" Collision",cube,x,0,top-13,(w/100,1.58,.26),
        collide=True,movable=moving,hide=True,category="Platforms")
    return collider,art

def plate(label,x,y,z,w,h,m):
    return geometry(label,cube,x,y,z,(w/100,.05,h/100),m,category="Switches")

def text(label,words,x,y,z,size):
    owner=spawn(u.TextRenderActor,label,x,y,z,"Labels")
    owner.set_actor_rotation(u.Rotator(0,0,90),False)
    c=owner.get_component_by_class(u.TextRenderComponent)
    c.set_text(words)
    c.set_world_size(size)
    c.set_horizontal_alignment(u.HorizTextAligment.EHTA_CENTER)
    c.set_text_render_color(u.Color(234,192,137,255))
    return owner

def point(label,x,y,z,color,intensity,radius):
    a=spawn(u.PointLight,label,x,y,z,"Lighting")
    c=a.get_component_by_class(u.PointLightComponent)
    c.set_mobility(u.ComponentMobility.MOVABLE)
    c.set_intensity(intensity)
    c.set_light_color(u.LinearColor(*color,1))
    c.set_attenuation_radius(radius)
    c.set_cast_shadows(False)

def cast(label,x,y,z,target,intensity):
    a=spawn(u.SpotLight,label,x,y,z,"Lighting")
    a.set_actor_rotation(u.MathLibrary.find_look_at_rotation(V(origin+x,y,z),V(origin+target[0],target[1],target[2])),False)
    c=a.get_component_by_class(u.SpotLightComponent)
    c.set_mobility(u.ComponentMobility.MOVABLE)
    c.set_intensity(intensity)
    c.set_light_color(u.LinearColor(1.,.67,.36,1))
    c.set_inner_cone_angle(22)
    c.set_outer_cone_angle(38)
    c.set_attenuation_radius(1050)
    c.set_cast_shadows(False)

def author_switch(label,x,z,width=45,height=57):
    plate(label+" Case",x,-265,z,width+10,height+10,dark)
    indicator=plate(label+" Contact",x,-259,z,width,height,metal)
    for side in [-1,1]:
        plate(label+" Trim",x+side*width*.5,-255,z,3,height,brass)
    return indicator

def floor_marker(label,x,z):
    geometry(label,cyl,x,0,z+1,(.33,.33,.025),brass,category="Switches")
    geometry(label+" Center",cyl,x,0,z+2.75,(.156,.156,.012),glow,category="Switches")

def import_curtain():
    name="SM_StandIn_ExhibitCurtains"
    mesh=asset(name)
    if not mesh:
        t=u.AssetImportTask()
        t.filename=str(BASE/(name+".fbx"))
        t.destination_path=PATH
        t.destination_name=name
        t.automated=True
        t.save=False
        fbx=u.FbxImportUI()
        fbx.import_as_skeletal=False
        fbx.import_materials=False
        fbx.import_textures=False
        fbx.static_mesh_import_data.auto_generate_collision=False
        t.options=fbx
        u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
        mesh=asset(name)
        assert mesh
    for i,s in enumerate(mesh.get_editor_property("static_materials")):
        m=asset(str(s.get_editor_property("imported_material_slot_name")))
        assert m
        mesh.set_material(i,m)
    assert LIB.save_loaded_asset(mesh,only_if_is_dirty=False)
    return mesh

made=[]
try:
    manager=spawn(cls,"Shadow Stand-In",0,0,0,"Puzzle")
    # Reuse the theatre's individual brick meshes and stone trim on the extension.
    for x in [660,1745]:
        geometry("Stand-In Brickwork","SM_Vault_CenterWall",x-1725,-5,35,(.94,1,1.05))
    for x in [92,492,923,1393,1700,2236]:
        geometry("Stand-In Pilaster",cube,x,-258,291,(.392,.429,6.42),slate)
        for z in [72,242,479,550]:
            geometry("Pilaster Cap",cube,x,-243,z,(.53,.504,.14),slate)
    geometry("Stand-In Ceiling",cube,1152,-249,550,(23.6,.85,.58),slate)
    geometry("Stand-In Wall Capping",cube,1152,-244,585,(23.6,.78,.18),stone)
    geometry("Stand-In Floor Line",cube,1152,-265,-266,(23.6,.7,.22),slate)
    geometry("Stand-In Understage",cube,1152,-392,-408,(23.6,1.1,4.2),stone)
    geometry("Stand-In Wing End Wall",cube,2270,-275,310,(1.5,1.4,9.7),stone)
    geometry("Stand-In Upper Backing",cube,1152,-393,850,(23.75,1.2,3.8),stone)
    geometry("Stand-In Theatre Rail","SM_Vault_FlyRail",1140-1402,0,0,(.82,1,1))
    deck("Ferry Call Ledge",174,205,0,"SM_Vault_RetakeDeck_03")
    deck("Ferry Exit Ledge",1041,282,0,"SM_Vault_RetakeDeck_07")
    deck("Raised Mark",1293,174,74,"SM_Vault_RetakeDeck_04")
    deck("Final Display Deck",1970,570,118,"SM_Vault_RetakeDeck_09")
    ferry,ferry_art=deck("Shadow Ferry",816,162,0,"SM_Vault_RetakeDeck_06",True)
    bridge,bridge_art=deck("Switch Bridge",1535,174,-176,"SM_Vault_RetakeDeck_08",True)
    for xx in [287,865]:
        for yy in [-75,75]:
            c=geometry("Ferry Stop",cube,xx,yy,-14,(.25,.20,.30),brass)
    for yy in [-56,56]:
        beam(V(278,yy,-77),V(913,yy,-77),10,metal,"Ferry Guide")
        beam(V(1456,yy,-185),V(1456,yy,76),9,metal,"Lift Guide")
    for xx in range(313,902,81):
        geometry("Guide Crossmember",cube,xx,0,-84,(.112,1.67,.085),metal)

    call=author_switch("Ferry Call",345,-24,320,64)
    low=author_switch("Low Switch",1275,-79,78,67)
    high=author_switch("High Switch",1435,25,83,73)
    for n,words,x,z in [("Ferry Label","FERRY CALL",347,32),
        ("Low Label","LOW",1275,-30),("High Label","HIGH",1435,78)]:
        text(n,words,x,-250,z,18)
    # Traces make the connection from each wall contact to its hardware readable.
    beam(V(520,-257,-24),V(623,-257,-24),5,brass,"Call Circuit")
    beam(V(623,-257,-24),V(623,-257,-120),5,brass,"Call Circuit Drop")
    beam(V(1316,-258,-79),V(1483,-258,-79),4,brass,"Low Circuit")
    beam(V(1477,-258,25),V(1525,-258,25),4,brass,"High Circuit")
    beam(V(1525,-258,25),V(1525,-258,-124),4,brass,"High Circuit Drop")
    floor_marker("Ferry Floor Mark",155,0)
    floor_marker("Low Test Mark",1155,0)
    floor_marker("High Floor Mark",1290,74)
    for name,x,y,z,col,intensity,reach in [
        ("Ferry Amber",140,160,213,(1,.51,.26),180,500),
        ("Ferry Far Fill",885,155,235,(.6,.50,.92),160,490),
        ("Switch Fill",1250,110,191,(1,.55,.27),135,460),
        ("Display Fill",2035,141,322,(1,.51,.26),183,610)]:
        point(name,x,y,z,col,intensity,reach)
    cast("Ferry Projector",95,490,192,(385,-271,30),805)
    cast("Bridge Projector",1050,470,254,(1410,-271,8),830)

    geometry("Display Curtains",import_curtain(),exhibit-2885,0,118)
    manager.set_editor_property("Ferry",ferry)
    manager.set_editor_property("FerryArt",ferry_art)
    manager.set_editor_property("Bridge",bridge)
    manager.set_editor_property("BridgeArt",bridge_art)
    manager.set_editor_property("SwitchLamps",[call,low,high])
    manager.set_editor_property("ShadowMaterial",asset("M20_Silhouette"))
    manager.set_editor_property("LampOnMaterial",glow)

    old.modify()
    old.set_editor_property("StandInPuzzle",manager)
    old.set_editor_property("ExhibitOffset",V(offset,0,118))
    for key in ("Glass","Exhibit","DisplayLight"):
        c=old.get_editor_property(key)
        p=c.get_relative_location() if hasattr(c,"get_relative_location") else c.get_editor_property("relative_location")
        if p.x<3500:
            c.set_relative_location(p+V(offset,0,118),False,True)
    for label in ("Pedestal","Exhibit_WarmWing"):
        a=actors[label]
        a.modify()
        a.set_actor_location(a.get_actor_location()+V(offset,0,118),False,True)
        a.set_folder_path("Stage4/Shadow Stand-In/Exhibit")
    boundary=actors["EastBoundary"]
    boundary.modify()
    boundary.set_actor_location(V(origin+2250,0,237),False,True)
    assert LEVEL.save_current_level()
except Exception:
    for a in reversed(made):
        ACTORS.destroy_actor(a)
    raise
u.log("SHADOW STAND-IN SAVED")
