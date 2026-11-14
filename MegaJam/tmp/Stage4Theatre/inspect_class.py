import unreal as u
from pathlib import Path
a=u.get_editor_subsystem(u.EditorActorSubsystem)
cls=u.load_class(None,"/Script/MegaJam.Stage4ShadowTheatre")
ok=[]
if cls:
    c=u.get_default_object(cls)
    ok += [str(c), str(dir(c)), str([str(x) for x in c.get_components_by_class(u.StaticMeshComponent)])]
    for key in ["EntranceDoor","entrance_door","RailCue","rail_cue","WestRig","west_rig","KnightGreave","Checkpoint"]:
        try: ok.append(f"{key} => {c.get_editor_property(key)}")
        except Exception as e: ok.append(f"{key} ! {e}")
Path(r'C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4Theatre/class.txt').write_text('\n'.join(ok),encoding='utf-8')
