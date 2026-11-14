import unreal as u
from pathlib import Path
s=u.get_editor_subsystem(u.EditorActorSubsystem)
l=u.get_editor_subsystem(u.LevelEditorSubsystem)
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert w.get_path_name()=="/Game/DirectorCut/Stage/Stage4.Stage4"
a={x.get_actor_label():x for x in s.get_all_level_actors()}
manager=a["Shadow Stand-In"]
old=a["Shadow Rehearsal"]
xyz=old.get_editor_property("Exhibit").get_world_location()
assert abs(xyz.x-6920)<2,xyz
assert len(old.get_editor_property("DeckScenery"))==9
assert old.get_editor_property("StandInPuzzle")==manager
for name in ("Ferry","FerryArt","Bridge","BridgeArt"):
    assert manager.get_editor_property(name),name
assert len(manager.get_editor_property("SwitchLamps"))==3
wreport=Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4StandIn/map-verified.txt")
wreport.write_text("Shadow Retake 9 decks\nShadow Stand-In all 3 switch contacts and both rigs\nExhibit X=6920",encoding="utf8")
