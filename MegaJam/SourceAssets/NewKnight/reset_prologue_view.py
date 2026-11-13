import unreal
loc=unreal.Vector(-700,-1250,390)
rot=unreal.Rotator(-12,58,0)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(loc,rot)
camera=next(a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label()=='Prologue_Camera')
camera.set_actor_location(loc,False,False)
camera.set_actor_rotation(rot,False)
unreal.EditorLevelLibrary.save_current_level()
unreal.log('PROLOGUE_VIEW_RESET')
