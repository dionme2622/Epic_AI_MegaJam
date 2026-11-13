import unreal
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_actor_label().startswith('Subtitle_'):
        a.static_mesh_component.set_visibility(True)
unreal.EditorLevelLibrary.save_current_level()
unreal.log('SUBTITLE_MESHES_RESTORED')
