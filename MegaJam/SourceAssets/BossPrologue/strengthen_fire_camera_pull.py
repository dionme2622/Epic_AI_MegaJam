"""Give the fire shot a short windup, fast rightward pull, and damped recoil."""
import unreal
from pathlib import Path

seq = unreal.load_asset('/Game/DirectorCut/Prologue/LS_BossPrologue_Cinematic')
binding = next(b for b in seq.get_bindings() if b.get_name() == 'Prologue Side Camera')
track = next(t for t in binding.get_tracks() if isinstance(t, unreal.MovieScene3DTransformTrack))
section = track.get_sections()[0]
channels = {c.get_name().split('_')[0]: c for c in section.get_all_channels()}

# frame, X, Z, roll, pitch, yaw. Linear segments deliberately accelerate sharply
# after the anticipation, then lose speed and reverse briefly at the stop.
poses = [
    (201, 390, 245, 0, -2, -90),
    (205, 414, 252, .25, -2.2, -90),
    (209, 362, 235, -.35, -1.7, -90),
    (213, 430, 254, .4, -2.3, -90),
    (217, 364, 238, -.3, -1.8, -90),
    (221, 410, 248, .2, -2.1, -90),
    (224, 382, 244, 0, -2, -90.15),
    (226, 355, 243, .2, -2, -90.3),
    (228, 390, 244, -.15, -2, -89.8),
    (230, 510, 247, -.45, -2.1, -89.3),
    (232, 695, 250, -.8, -2.25, -88.9),
    (234, 905, 252, -1, -2.3, -88.8),
    (236, 1070, 249, -.7, -2.15, -89.2),
    (238, 1160, 246, -.3, -2, -89.65),
    (242, 1085, 242, .4, -1.85, -90.35),
    (246, 1120, 246, -.15, -2.05, -89.9),
    (252, 1110, 245, 0, -2, -90),
    (263, 1110, 245, 0, -2, -90),
]
properties = ['Location.X', 'Location.Z', 'Rotation.X', 'Rotation.Y', 'Rotation.Z']
untouched = {}
for prop in properties:
    channel = channels[prop]
    untouched[prop] = [(k.get_time().frame_number.value, k.get_value())
                       for k in channel.get_keys() if not 201 <= k.get_time().frame_number.value <= 263]
    for key in list(channel.get_keys()):
        if 201 <= key.get_time().frame_number.value <= 263:
            channel.remove_key(key)
    for pose in poses:
        value = pose[properties.index(prop) + 1]
        channel.add_key(unreal.FrameNumber(pose[0]), value,
                        interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
    assert [(k.get_time().frame_number.value, k.get_value())
            for k in channel.get_keys() if not 201 <= k.get_time().frame_number.value <= 263] == untouched[prop]

assert unreal.EditorAssetLibrary.save_loaded_asset(seq, False)
peak_speed = max(abs(b[1]-a[1])*24/(b[0]-a[0]) for a,b in zip(poses, poses[1:]))
Path(unreal.Paths.project_saved_dir(), 'camera_fire_pull_applied.txt').write_text(
    'windup=224..226\nfast_pull=226..238\nsettled_frame=252\n'
    f'peak_horizontal_speed_cm_s={peak_speed}\n'+str(poses))
