import unreal
P='/Game/Assets/Prologue/'
seq=unreal.load_asset(P+'LS_Prologue_LastBattle_v4')
assert seq
actors=unreal.EditorLevelLibrary.get_all_level_actors()
camera=next(a for a in actors if a.get_actor_label()=='Prologue_Camera')
existing=next((a for a in actors if isinstance(a,unreal.LevelSequenceActor) and a.get_actor_label()=='Prologue_Autoplay'),None)
player=existing or unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.LevelSequenceActor,unreal.Vector(0,0,0))
player.set_actor_label('Prologue_Autoplay')
player.set_sequence(seq)
settings=player.get_editor_property('playback_settings')
settings.set_editor_property('auto_play',True)
player.set_editor_property('playback_settings',settings)

captions=[('01_Victory',0,300),('02_Dragon_Rises',390,690),('03_Missing',720,900),
 ('04_Dev_Note',900,1050),('05_Dev_Note2',1050,1170),('06_Protest',1170,1380),
 ('07_Crawl',1380,1650),('08_Storage',1650,1800)]
for name,start,end in captions:
    actor=next(a for a in actors if a.get_actor_label()=='Subtitle_'+name)
    actor.set_actor_hidden_in_game(False)
    # The section controls visibility in the sequence; clear duplicate frame-zero keys.
    binding=next(b for b in seq.get_bindings() if b.get_name()=='Subtitle_'+name)
    track=next(t for t in binding.get_tracks() if isinstance(t,unreal.MovieSceneVisibilityTrack))
    channel=track.get_sections()[0].get_all_channels()[0]
    for key in list(channel.get_keys()):channel.remove_key(key)
    if start>0:channel.add_key(unreal.FrameNumber(0),False)
    channel.add_key(unreal.FrameNumber(start),True)
    if end<1800:channel.add_key(unreal.FrameNumber(end),False)

unreal.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
unreal.EditorAssetLibrary.save_loaded_asset(seq)
unreal.EditorLevelLibrary.save_current_level()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
unreal.log('PROLOGUE_PLAYBACK_FIXED')
