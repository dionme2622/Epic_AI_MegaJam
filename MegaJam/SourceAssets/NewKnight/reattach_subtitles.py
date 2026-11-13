import unreal
actors=unreal.EditorLevelLibrary.get_all_level_actors()
camera=next(a for a in actors if a.get_actor_label()=='Prologue_Camera')
count=0
for a in actors:
    if not a.get_actor_label().startswith('Subtitle_'):continue
    a.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    ok=a.attach_to_actor(camera,'',unreal.AttachmentRule.KEEP_WORLD,
                         unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
    assert ok,a.get_actor_label()
    a.set_actor_relative_location(unreal.Vector(500,0,-95),False,False)
    a.set_actor_relative_rotation(unreal.Rotator(0,90,90),False,False)
    a.set_actor_relative_scale3d(unreal.Vector(4.4,.44,1))
    assert a.get_attach_parent_actor()==camera
    count+=1
unreal.EditorLevelLibrary.save_current_level()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
unreal.log('SUBTITLES_ATTACHED '+str(count))
