import unreal as u
from pathlib import Path

a=u.get_editor_subsystem(u.EditorActorSubsystem)
l=u.get_editor_subsystem(u.LevelEditorSubsystem)
tuning={
"West_Silhouette_Key":5900,
"East_Silhouette_Key":5650,
"West_WarmWing":160,
"West_WorkLight":140,
"Center_MarkLight":255,
"East_WorkLight":155,
"Exhibit_WarmWing":300,
"Understage_Fill":165,
}
for actor in a.get_all_level_actors():
    name=actor.get_actor_label()
    if name in tuning:
        c=actor.get_component_by_class(u.LightComponent)
        c.set_intensity(tuning[name])
        if isinstance(c,u.SpotLightComponent):
            c.set_inner_cone_angle(25)
            c.set_outer_cone_angle(36)
            c.set_editor_property("source_radius",2.0)

eye=u.Vector(3100,3105,455)
target=u.Vector(3100,-15,94)
l.set_level_viewport_camera_info(eye,u.MathLibrary.find_look_at_rotation(eye,target),l.get_active_viewport_config_key())
l.editor_invalidate_viewports()
assert l.save_current_level()
u.log("VAULT LIGHTING SAVED")
