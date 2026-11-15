"""Continue original-legs camera from the shared reveal without a second zoom-in."""
import unreal
lib=unreal.EditorAssetLibrary
reveal=unreal.load_asset('/Game/DirectorCut/Ending/LS_BossEnding_Reveal')
seq=unreal.load_asset('/Game/DirectorCut/Ending/LS_BossEnding_OriginalLegs')
def camera_section(asset):
    for b in asset.get_bindings():
        if b.get_name()=='Ending Camera':
            for t in b.get_tracks():
                if isinstance(t,unreal.MovieScene3DTransformTrack):return t.get_sections()[0]
    raise AssertionError('Camera track missing')
r=camera_section(reveal)
start=[float(ch.get_keys()[-1].get_value()) for ch in r.get_all_channels()]
s=camera_section(seq)
channels=s.get_all_channels()
for ch in channels:
    for key in list(ch.get_keys()):ch.remove_key(key)
for frame,values in [(0,start),(30,[760,2450,470,0,-3,-90,1,1,1]),(144,[710,2450,470,0,-3,-90,1,1,1]),(seq.get_playback_end()-1,[710,2450,470,0,-3,-90,1,1,1])]:
    for ch,val in zip(channels,values):ch.add_key(unreal.FrameNumber(frame),val,interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
assert all(abs(float(ch.get_keys()[0].get_value())-v)<.001 for ch,v in zip(channels,start))
assert lib.save_loaded_asset(seq)
unreal.log('ORIGINAL_LEGS_SINGLE_ZOOM_PASS '+str(start))
