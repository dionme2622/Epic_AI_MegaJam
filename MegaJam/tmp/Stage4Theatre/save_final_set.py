import unreal as u
from pathlib import Path
a=u.get_editor_subsystem(u.EditorActorSubsystem)
l=u.get_editor_subsystem(u.LevelEditorSubsystem)
theatre=next(actor for actor in a.get_all_level_actors() if actor.get_actor_label()=="Shadow Rehearsal")
for key,x,z,scale in [("WestRig",360,138,402/421),("EastRig",1595,149,391/459)]:
    c=theatre.get_editor_property(key)
    c.set_relative_location(u.Vector(x,0,z),False,True)
    c.set_relative_scale3d(u.Vector(1,1,scale))
theatre.get_editor_property("EastMarker").set_relative_location(u.Vector(1605,-270,168),False,True)
theatre.get_editor_property("DisplayLight").set_intensity(90)
assert l.save_current_level()
eye=u.Vector(3090,3050,490)
target=u.Vector(3090,-15,160)
l.set_level_viewport_camera_info(eye,u.MathLibrary.find_look_at_rotation(eye,target),l.get_active_viewport_config_key())
l.editor_invalidate_viewports()
u.log("VAULT FINAL SET SAVED")
