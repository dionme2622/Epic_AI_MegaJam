import unreal
P='/Game/Assets/Prologue/'
seq=unreal.load_asset(P+'LS_Prologue_LastBattle_v4')
actors={a.get_actor_label():a for a in unreal.EditorLevelLibrary.get_all_level_actors()}
camera=actors['Prologue_Camera']
camera.set_actor_rotation(unreal.Rotator(roll=0,pitch=-12,yaw=58),False)
actors['Hero_Victor'].set_actor_rotation(unreal.Rotator(roll=0,pitch=0,yaw=20),False)

angles={
 'Prologue_Camera':[(0,0,-12,58),(360,0,-10,65),(720,0,-9,78),(1050,0,-8,89),(1450,0,-8,110),(1800,0,-7,125)],
 'Hero_Victor':[(0,0,0,20),(210,0,0,20),(390,0,0,20),(1800,0,0,20)],
 'Dragon_Upper_Body_Cube':[(0,0,0,180),(90,0,78,180),(390,0,78,180),(530,0,-20,180),(1800,0,-20,140)]
}
for b in seq.get_bindings():
    if b.get_name() not in angles:continue
    t=next(t for t in b.get_tracks() if isinstance(t,unreal.MovieScene3DTransformTrack))
    ch=t.get_sections()[0].get_all_channels()
    for i in (3,4,5):
        for k in list(ch[i].get_keys()):ch[i].remove_key(k)
    for frame,roll,pitch,yaw in angles[b.get_name()]:
        for index,value in ((3,roll),(4,pitch),(5,yaw)):
            ch[index].add_key(unreal.FrameNumber(frame),float(value))

for a in actors.values():
    if a.get_actor_label().startswith('Subtitle_'):
        a.set_actor_relative_location(unreal.Vector(500,0,-95),False,False)
        a.set_actor_relative_rotation(unreal.Rotator(roll=90,pitch=0,yaw=90),False,False)
        a.set_actor_relative_scale3d(unreal.Vector(4.4,.44,1))
unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(-700,-1250,390),unreal.Rotator(roll=0,pitch=-12,yaw=58))
unreal.EditorAssetLibrary.save_loaded_asset(seq)
unreal.EditorLevelLibrary.save_current_level()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
unreal.log('PROLOGUE_ROTATIONS_FIXED')
