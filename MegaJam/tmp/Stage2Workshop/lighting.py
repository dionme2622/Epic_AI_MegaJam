import unreal as u
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=="/Game/DirectorCut/Stage/Stage2.Stage2"
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
for a in actors:
 name=a.get_actor_label()
 if name.startswith("Workshop_Lantern_"):
  a.get_component_by_class(u.PointLightComponent).set_intensity(38.0)
 if name=="DirectionalLight":
  a.get_component_by_class(u.DirectionalLightComponent).set_intensity(.72)
 if name=="SkyLight":
  a.get_component_by_class(u.SkyLightComponent).set_intensity(.5)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log("STAGE2 WORKSHOP LIGHTS BALANCED")
