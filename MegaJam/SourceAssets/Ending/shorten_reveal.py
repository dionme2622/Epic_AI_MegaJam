import unreal
s=unreal.load_asset('/Game/DirectorCut/Ending/LS_BossEnding_Reveal')
assert s
mapping={0:0,48:36,120:72,192:132,215:155}
for b in s.get_bindings():
    for t in b.get_tracks():
        for section in t.get_sections():
            if isinstance(section,unreal.MovieScene3DTransformSection):
                for channel in section.get_all_channels():
                    for key in channel.get_keys():
                        frame=key.get_time().frame_number.value
                        if frame in mapping:key.set_time(unreal.FrameNumber(mapping[frame]))
            section.set_end_frame(156)
for track in s.get_tracks():
    for section in track.get_sections():section.set_end_frame(156)
s.set_playback_end(156)
s.delete_marked_frames()
for f,label in [(0,'Reveal starts'),(36,'Selected lower body'),(72,'Return to opening shot'),(132,'Opening shot restored'),(155,'Continue')]:
    s.add_marked_frame(unreal.MovieSceneMarkedFrame(frame_number=unreal.FrameNumber(f),label=label))
assert unreal.EditorAssetLibrary.save_loaded_asset(s)
assert s.get_playback_end()==156
unreal.log('ENDING_REVEAL_SHORTENED_6_5_SECONDS')
