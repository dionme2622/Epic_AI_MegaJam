import unreal as u

levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
assert levels.load_level('/Game/Stage3Integrated/Sections/L_Resolution')
pit = next(a for a in actors.get_all_level_actors() if a.get_actor_label() == 'Resolution_NonblockingPit')
pit.set_actor_enable_collision(False)
pit.static_mesh_component.set_collision_profile_name('NoCollision')
assert levels.save_current_level()
assert levels.load_level('/Game/DirectorCut/Stage/Stage3_')
u.log('STAGE3 BRIDGE PIT COLLISION FIXED')
