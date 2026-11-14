import ast
from pathlib import Path
import unreal as u

ROOT=Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam")
D="/Game/Stage4Integrated/Theatre"
MAP="/Game/DirectorCut/Stage/Stage4.Stage4"
lib=u.EditorAssetLibrary
sub=u.get_editor_subsystem(u.EditorActorSubsystem)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()==MAP
existing={a.get_actor_label():a for a in sub.get_all_level_actors()}
manager=existing["Shadow Rehearsal"]
assert manager.get_editor_property("EntranceDoor")
for i in range(1,10):
    assert lib.load_asset(f"{D}/SM_Vault_RetakeDeck_{i:02}")
    assert f"Landing_{i:02}" in existing

asset_name="M21_RetakeCue"
path=f"{D}/{asset_name}"
m=lib.load_asset(path) if lib.does_asset_exist(path) else u.AssetToolsHelpers.get_asset_tools().create_asset(asset_name,D,u.Material,u.MaterialFactoryNew())
m.set_editor_property("shading_model",u.MaterialShadingModel.MSM_UNLIT)
edit=u.MaterialEditingLibrary
edit.delete_all_material_expressions(m)
color=edit.create_material_expression(m,u.MaterialExpressionConstant3Vector,-230,0)
color.set_editor_property("constant",u.LinearColor(.95,.56,.14,1))
edit.connect_material_property(color,"",u.MaterialProperty.MP_EMISSIVE_COLOR)
edit.recompile_material(m)
assert lib.save_loaded_asset(m,only_if_is_dirty=False)

origin=manager.get_actor_location()
static_decks={1,5,7,9}
scenery=[]
collisions=[]
spawned=[]
try:
    manager.modify()
    for idx in range(1,10):
        label=f"Retake_Deck_{idx:02}"
        actor=existing.get(label)
        if not actor:
            actor=sub.spawn_actor_from_class(u.StaticMeshActor,origin,u.Rotator())
            spawned.append(actor)
            actor.set_actor_label(label)
            actor.set_folder_path("Stage4/Shadow Rehearsal/Environment")
        mesh=actor.static_mesh_component
        mesh.set_mobility(u.ComponentMobility.MOVABLE if idx not in static_decks else u.ComponentMobility.STATIC)
        mesh.set_static_mesh(lib.load_asset(f"{D}/SM_Vault_RetakeDeck_{idx:02}"))
        mesh.set_collision_profile_name("NoCollision")
        mesh.set_cast_shadow(False)
        mesh.set_editor_property("affect_distance_field_lighting",False)
        mesh.set_visibility(True)
        scenery.append(mesh)
        actor=existing[f"Landing_{idx:02}"]
        collision=actor.static_mesh_component
        if idx not in static_decks:
            collision.modify()
            collision.set_mobility(u.ComponentMobility.MOVABLE)
            collision.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
        collisions.append(collision)
    manager.set_editor_property("DeckScenery",scenery)
    manager.set_editor_property("DeckCollision",collisions)
    manager.set_editor_property("PreviewMaterial",m)
    for key,label,relative_x,aim_x,aim_z,y,z in [
        ("WestLamp","West_Silhouette_Key",655,792,280,580,309),
        ("EastLamp","East_Silhouette_Key",2040,1878,280,565,291),
    ]:
        a=existing[label]
        lamp=a.get_component_by_class(u.SpotLightComponent)
        p=origin+u.Vector(relative_x,y,z)
        rot=u.MathLibrary.find_look_at_rotation(p,origin+u.Vector(aim_x,-273,aim_z))
        a.set_actor_location_and_rotation(p,rot,False,True)
        manager.set_editor_property(key,lamp)

    for key,x,z,stretch in [("WestRig",748,198,342/421),("EastRig",1930,200,340/459)]:
        mesh=manager.get_editor_property(key)
        mesh.set_relative_location(u.Vector(x,0,z),False,True)
        mesh.set_relative_scale3d(u.Vector(1,1,stretch))
    for key,x,z in [("WestMarker",791.8,267.2),("EastMarker",1876.9,268.5)]:
        comp=manager.get_editor_property(key)
        comp.set_relative_location(u.Vector(x,-268,z),False,True)
        comp.set_relative_scale3d(u.Vector(.71,.71,.71))
    if "PlatformFaces" in existing:
        assert sub.destroy_actor(existing["PlatformFaces"])
    assert level.save_current_level()
except Exception:
    for actor in reversed(spawned):
        sub.destroy_actor(actor)
    raise
u.log("SHADOW RETAKE SAVED")
