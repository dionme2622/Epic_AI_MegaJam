import json
import sys
from pathlib import Path
import unreal as u

world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=="/Game/DirectorCut/Stage/Stage4.Stage4"
actor_api=u.get_editor_subsystem(u.EditorActorSubsystem)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
lights=[a for a in actor_api.get_all_level_actors() if isinstance(a,u.DirectionalLight)]
assert len(lights)==1
actor=lights[0]
light=actor.get_component_by_class(u.DirectionalLightComponent)
with u.ScopedEditorTransaction("Stage4 Directional Light grade"):
    actor.modify()
    light.modify()
    actor.set_actor_rotation(u.Rotator(0,-38,-116),False)
    light.set_intensity(1.35)
    light.set_editor_property("use_temperature",True)
    light.set_editor_property("temperature",7900.0)
    light.set_editor_property("light_source_angle",2.2)
    light.set_editor_property("light_source_soft_angle",.6)
    light.set_editor_property("indirect_lighting_intensity",.55)
    light.set_editor_property("volumetric_scattering_intensity",.15)
level.editor_invalidate_viewports()
if "save" in sys.argv:
    assert level.save_current_level()
report={"intensity":light.get_editor_property("intensity"),"temperature":light.get_editor_property("temperature"),
        "rotation":actor.get_actor_rotation().to_tuple(),"source_angle":light.get_editor_property("light_source_angle")}
Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4Lighting/applied.json").write_text(json.dumps(report,indent=2))
u.log("STAGE4 DIRECTIONAL LIGHT TUNED "+str(report))
