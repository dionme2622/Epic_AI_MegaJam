import unreal
count=0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if not a.get_actor_label().startswith('Subtitle_'):continue
    a.set_actor_relative_location(unreal.Vector(500,0,-25),False,False)
    count+=1
unreal.EditorLevelLibrary.save_current_level()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
unreal.log('SUBTITLES_RAISED '+str(count))
