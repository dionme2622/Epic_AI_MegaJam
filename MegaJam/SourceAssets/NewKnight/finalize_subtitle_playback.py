import unreal
actors=unreal.EditorLevelLibrary.get_all_level_actors()
for a in actors:
    if a.get_actor_label().startswith('Subtitle_'):
        a.set_actor_relative_location(unreal.Vector(500,0,-55),False,False)
if not any(isinstance(a,unreal.PlayerStart) for a in actors):
    start=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(-4000,-4000,150),unreal.Rotator(roll=0,pitch=0,yaw=0))
    start.set_actor_label('Offstage_Player_Start')
unreal.EditorLevelLibrary.save_current_level()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
unreal.log('SUBTITLE_PLAYBACK_FINALIZED')
