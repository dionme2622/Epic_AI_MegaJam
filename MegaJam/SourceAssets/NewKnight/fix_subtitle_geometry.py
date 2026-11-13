import unreal
actors=unreal.EditorLevelLibrary.get_all_level_actors()
panels=[a for a in actors if a.get_actor_label().startswith('Subtitle_')]
assert len(panels)==8
for a in panels:
    a.set_actor_relative_location(unreal.Vector(500,0,-95),False,False)
    a.set_actor_relative_rotation(unreal.Rotator(0,90,90),False,False)
    a.set_actor_relative_scale3d(unreal.Vector(4.4,.44,1))
    a.set_actor_hidden_in_game(a.get_actor_label()!='Subtitle_01_Victory')
unreal.EditorLevelLibrary.save_current_level()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
unreal.log('SUBTITLE_GEOMETRY_FIXED '+str(len(panels)))
