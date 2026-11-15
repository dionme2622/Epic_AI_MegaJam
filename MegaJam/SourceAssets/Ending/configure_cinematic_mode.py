import unreal
ed=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert ed.load_level('/Game/DirectorCut/Ending/L_BossEnding')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
cls=unreal.load_class(None,'/Script/MegaJam.DirectorCutEndingMode')
assert cls
assert unreal.get_default_object(cls).get_editor_property('default_pawn_class') is None
world.get_world_settings().set_editor_property('default_game_mode',cls)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.log('ENDING_NATIVE_NO_PAWN_MODE_SAVED')
