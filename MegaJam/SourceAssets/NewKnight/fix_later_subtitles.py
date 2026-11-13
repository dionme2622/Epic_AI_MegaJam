import unreal
count=0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_actor_label().startswith('Subtitle_'):
        a.set_actor_hidden_in_game(False)
        a.static_mesh_component.set_visibility(True)
        count+=1
unreal.EditorLevelLibrary.save_current_level()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
unreal.log('LATER_SUBTITLES_UNHIDDEN '+str(count))
