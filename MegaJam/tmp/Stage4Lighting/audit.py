import json
from pathlib import Path
import unreal as u
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert w.get_path_name()=="/Game/DirectorCut/Stage/Stage4.Stage4"
sub=u.get_editor_subsystem(u.EditorActorSubsystem)
report={}
for a in sub.get_all_level_actors():
    c=a.get_component_by_class(u.LightComponent)
    if not c and not isinstance(a,u.PostProcessVolume):
        continue
    name=a.get_actor_label()
    row={"type":a.get_class().get_name(),"location":a.get_actor_location().to_tuple(),"rotation":a.get_actor_rotation().to_tuple()}
    if c:
        keys=["intensity","light_color","use_temperature","temperature","cast_shadows","indirect_lighting_intensity","volumetric_scattering_intensity"]
        if isinstance(c,u.DirectionalLightComponent):
            keys+=["light_source_angle","light_source_soft_angle","atmosphere_sun_light","mobility"]
        for k in keys:
            try: row[k]=str(c.get_editor_property(k))
            except Exception: pass
    else:
        row["settings"]=str(a.get_editor_property("settings"))[:1100]
    report[name]=row
Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4Lighting/before.json").write_text(json.dumps(report,indent=2))
