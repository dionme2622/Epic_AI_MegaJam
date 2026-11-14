import unreal as u
from pathlib import Path
a=u.get_editor_subsystem(u.EditorActorSubsystem)
l=u.get_editor_subsystem(u.LevelEditorSubsystem)
folder="/Game/Stage4Integrated/Theatre"
lib=u.EditorAssetLibrary
tools=u.AssetToolsHelpers.get_asset_tools()
edit=u.MaterialEditingLibrary
path=folder+"/M20_Silhouette"
m=lib.load_asset(path) if lib.does_asset_exist(path) else tools.create_asset("M20_Silhouette",folder,u.Material,u.MaterialFactoryNew())
m.set_editor_property("shading_model",u.MaterialShadingModel.MSM_UNLIT)
m.set_editor_property("blend_mode",u.BlendMode.BLEND_TRANSLUCENT)
m.set_editor_property("two_sided",False)
edit.delete_all_material_expressions(m)
c=edit.create_material_expression(m,u.MaterialExpressionConstant3Vector,-220,0)
c.set_editor_property("constant",u.LinearColor(.015,.008,.024,1))
edit.connect_material_property(c,"",u.MaterialProperty.MP_EMISSIVE_COLOR)
o=edit.create_material_expression(m,u.MaterialExpressionConstant,-210,130)
o.set_editor_property("r",.69)
edit.connect_material_property(o,"",u.MaterialProperty.MP_OPACITY)
edit.recompile_material(m)
assert lib.save_loaded_asset(m,only_if_is_dirty=False)

values={
"West_Silhouette_Key":1000,
"East_Silhouette_Key":910,
"West_WarmWing":95,
"West_WorkLight":90,
"Center_MarkLight":160,
"East_WorkLight":95,
"Exhibit_WarmWing":146,
"Understage_Fill":78,
}
theatre=None
for actor in a.get_all_level_actors():
    name=actor.get_actor_label()
    if name in values:
        comp=actor.get_component_by_class(u.LightComponent)
        comp.set_intensity(values[name])
        if isinstance(comp,u.SpotLightComponent):
            comp.set_inner_cone_angle(19)
            comp.set_outer_cone_angle(39)
    elif name=="Shadow Rehearsal":
        theatre=actor
        theatre.set_editor_property("SilhouetteMaterial",m)
        for key,x,z in [("WestMarker",757,173),("EastMarker",1482,146)]:
            comp=theatre.get_editor_property(key)
            comp.set_relative_location(u.Vector(x,-270,z),False,True)
        for key in ("WestRig","EastRig"):
            theatre.get_editor_property(key).set_cast_shadow(False)
        theatre.get_editor_property("DisplayLight").set_intensity(90)
assert theatre

# Keep the interior in frame even at the two extremes of the side-scrolling camera.
backdrop=u.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
slate=lib.load_asset(folder+"/M01_Bedrock")
for name,loc,dimensions in [
    ("CeilingBacking",(3080,-360,827),(4540,160,366)),
    ("UnderstageBacking",(3080,-397,-533),(4540,160,590)),
    ("RightWingBacking",(4960,-328,300),(496,128,1140)),
    ("LeftWingBacking",(1142,-328,430),(182,126,966)),
]:
    found=[actor for actor in a.get_all_level_actors() if actor.get_actor_label()==name]
    actor=found[0] if found else a.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*loc),u.Rotator())
    actor.set_actor_label(name)
    actor.set_folder_path("Stage4/Shadow Rehearsal/Environment")
    actor.set_actor_scale3d(u.Vector(*(v/100 for v in dimensions)))
    comp=actor.static_mesh_component
    comp.set_static_mesh(backdrop)
    comp.set_material(0,slate)
    comp.set_cast_shadow(False)
    comp.set_collision_profile_name("NoCollision")

assert l.save_current_level()
u.log("VAULT PROJECTION SAVED")
