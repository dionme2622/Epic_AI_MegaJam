import unreal as u

actor_subsystem = u.get_editor_subsystem(u.EditorActorSubsystem)
level_subsystem = u.get_editor_subsystem(u.LevelEditorSubsystem)
world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name() == '/Game/DirectorCut/Stage/Stage2.Stage2'
director_class = u.EditorAssetLibrary.load_blueprint_class('/Game/Stage2Workshop/BP_Stage2WorkshopDirector')
assert director_class
old = next(a for a in actor_subsystem.get_all_level_actors() if a.get_actor_label() == 'Stage1_PuzzleDirector')
if old.get_class() != director_class:
    replacement = actor_subsystem.spawn_actor_from_class(director_class, old.get_actor_location(), old.get_actor_rotation())
    assert replacement
    replacement.set_folder_path(old.get_folder_path())
    replacement.set_editor_property('tags', old.get_editor_property('tags'))
    assert actor_subsystem.destroy_actor(old)
    replacement.set_actor_label('Stage1_PuzzleDirector')
assert level_subsystem.save_current_level()
u.log('STAGE2 WORKSHOP DIRECTOR SAVED')
