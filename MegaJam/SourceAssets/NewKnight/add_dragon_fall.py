import unreal
seq=unreal.load_asset('/Game/Assets/Prologue/LS_Prologue_LastBattle_v4')
assert seq
for b in seq.get_bindings():
    if 'Dragon_Upper_Body_Cube' not in b.get_name():continue
    for t in b.get_tracks():
        if not isinstance(t,unreal.MovieScene3DTransformTrack):continue
        s=t.get_sections()[0]
        ch=s.get_all_channels()
        for f,pitch in ((0,0),(90,78),(390,78),(530,-20)):
            ch[3].add_key(unreal.FrameNumber(f),float(pitch))
        unreal.EditorAssetLibrary.save_loaded_asset(seq)
        unreal.log('DRAGON_FALL_OK')
        break
