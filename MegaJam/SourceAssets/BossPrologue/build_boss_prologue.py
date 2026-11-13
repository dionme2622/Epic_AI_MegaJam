"""Build the 25-second bilingual boss intro in the existing L_BossPrologue."""
from pathlib import Path
import wave
import unreal

ROOT = Path(__file__).resolve().parent
P = '/Game/DirectorCut/Prologue/'
LEVEL = P + 'L_BossPrologue'
SEQ = P + 'LS_BossPrologue_Cinematic'
ASSET = P + 'Cinematic/'
FPS = 24
END = 600

editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert editor.load_level(LEVEL)
tools = unreal.AssetToolsHelpers.get_asset_tools()
library = unreal.EditorAssetLibrary
actors = {a.get_actor_label(): a for a in unreal.EditorLevelLibrary.get_all_level_actors()}
camera = actors['Prologue Side Camera']
dragon = actors['Prologue Dragon']
player = actors['Player Dragon']
autoplay = actors['Prologue Sequence']
camera.set_actor_location(unreal.Vector(390, 1150, 245), False, False)
camera.set_actor_rotation(unreal.Rotator(0, -2, -90), False)
dragon.set_actor_location(unreal.Vector(1271.6, 3.5, 132.2), False, False)
dragon.set_actor_rotation(unreal.Rotator(0, -30, 180), False)
dragon.set_actor_scale3d(unreal.Vector(7.5, 7.5, 7.5))

for a in list(actors.values()):
    if a.get_actor_label().startswith('BossIntro_'):
        unreal.EditorLevelLibrary.destroy_actor(a)
if library.does_asset_exist(SEQ):
    assert library.delete_asset(SEQ)
seq = tools.create_asset('LS_BossPrologue_Cinematic', P, unreal.LevelSequence,
                         unreal.LevelSequenceFactoryNew())
assert seq
seq.set_display_rate(unreal.FrameRate(FPS, 1))
seq.set_playback_start(0)
seq.set_playback_end(END)

def import_file(path):
    task = unreal.AssetImportTask()
    task.filename = str(path)
    task.destination_path = ASSET
    task.automated = True
    task.save = True
    task.replace_existing = True
    tools.import_asset_tasks([task])
    paths = task.get_editor_property('imported_object_paths')
    assert paths, path
    asset = unreal.load_asset(paths[0])
    assert asset, paths[0]
    return asset

textures = {path.stem: import_file(path) for path in sorted((ROOT / 'Graphics').glob('*.png'))}
voices = {path.stem: import_file(path) for path in sorted((ROOT / 'Voice').glob('*.wav'))}
assert len(textures) == 7 and len(voices) == 4
base_mat = unreal.load_asset('/Game/Assets/Prologue/M_Bilingual_Subtitle')
assert base_mat

def material(name):
    mi_path = ASSET + 'MI_' + name
    if library.does_asset_exist(mi_path):
        mi = unreal.load_asset(mi_path)
    else:
        mi = tools.create_asset('MI_' + name, ASSET, unreal.MaterialInstanceConstant,
                                unreal.MaterialInstanceConstantFactoryNew())
    mi.set_editor_property('parent', base_mat)
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(mi, 'Caption', textures[name])
    library.save_loaded_asset(mi)
    return mi

materials = {name: material(name) for name in textures}
plane = unreal.load_asset('/Engine/BasicShapes/Plane')
cube = unreal.load_asset('/Engine/BasicShapes/Cube')
stone = unreal.load_asset('/Game/DirectorCut/Environment/M_Castle_Wall')
floor_tile = unreal.load_asset('/Game/DirectorCut/Environment/SM_Castle_Floor_Slab')
assert plane and cube and stone and floor_tile
shadow_path = ASSET + 'M_Storage_Shadow'
if library.does_asset_exist(shadow_path):
    shadow = unreal.load_asset(shadow_path)
else:
    shadow = tools.create_asset('M_Storage_Shadow', ASSET, unreal.Material,
                                unreal.MaterialFactoryNew())
    dark = unreal.MaterialEditingLibrary.create_material_expression(
        shadow, unreal.MaterialExpressionConstant3Vector, -200, 0)
    dark.set_editor_property('constant', unreal.LinearColor(.012, .018, .028, 1))
    unreal.MaterialEditingLibrary.connect_material_property(
        dark, '', unreal.MaterialProperty.MP_BASE_COLOR)
    unreal.MaterialEditingLibrary.recompile_material(shadow)
    library.save_loaded_asset(shadow)

def spawn_static(label, mesh, loc, scale, rot=(0, 0, 0), mat=None):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(*loc), unreal.Rotator(rot[2], rot[0], rot[1]))
    actor.set_actor_label('BossIntro_' + label)
    actor.static_mesh_component.set_static_mesh(mesh)
    actor.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    actor.set_actor_scale3d(unreal.Vector(*scale))
    if mat:
        actor.static_mesh_component.set_material(0, mat)
    return actor

# A dark opening framed by the same castle masonry, on the existing raised stage.
for row, y in enumerate((97, 162, 227), 1):
    for column, x in enumerate((1450, 1550, 1650, 1750), 1):
        spawn_static(f'Storage_Floor_{row}_{column}', floor_tile,
                     (x, y, 44), (1, 1, 1))
spawn_static('Storage_Door', cube, (1600, 60, 190), (1.6, .17, 2.9), mat=shadow)
spawn_static('Storage_LeftPost', cube, (1495, 100, 185), (.42, .55, 3.7), mat=stone)
spawn_static('Storage_RightPost', cube, (1705, 100, 185), (.42, .55, 3.7), mat=stone)
spawn_static('Storage_Lintel', cube, (1600, 100, 365), (2.6, .55, .48), mat=stone)
note = spawn_static('Developer_Note', plane, (1260, 430, 175), (3.0, 1.0, 1),
                    (0, 0, 90), materials['05_DevNote'])
sign = spawn_static('Storage_Sign', plane, (1600, 160, 415), (2.7, .63, 1),
                    (0, 0, 90), materials['06_Storage'])
flame = spawn_static('Dragon_Flame', plane, (420, 420, 335), (4.8, 1.7, 1),
                     (0, 0, 90), materials['07_Fire'])

knight_mesh = unreal.load_asset('/Game/Assets/Knight/tripo_convert_4b997851-a9fc-4243-9238-73b72c3eada4')
draw = unreal.load_asset('/Game/Assets/Knight/Anim/Withdrawing_Sword')
crouch = unreal.load_asset('/Game/Assets/Knight/Anim/Crouch_Idle')
assert knight_mesh and draw and crouch
hero = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.SkeletalMeshActor, unreal.Vector(110, 0, 80), unreal.Rotator(0, 0, 0))
hero.set_actor_label('BossIntro_Hero')
hero.skeletal_mesh_component.set_skeletal_mesh_asset(knight_mesh)
hero.skeletal_mesh_component.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
hero.skeletal_mesh_component.set_animation(crouch)
center, extent = hero.get_actor_bounds(False)
height = max(1.0, extent.z * 2)
hero.set_actor_scale3d(unreal.Vector(235 / height, 235 / height, 235 / height))
center, extent = hero.get_actor_bounds(False)
hero.set_actor_location(unreal.Vector(110, 0, 70 - (center.z - extent.z)), False, False)
player.set_actor_hidden_in_game(True)

def bind(actor):
    return seq.add_possessable(actor)

cam_bind = bind(camera)
dragon_bind = bind(dragon)
hero_bind = bind(hero)
note_bind = bind(note)
sign_bind = bind(sign)
flame_bind = bind(flame)

def transform(binding, keys, scale=1.0):
    track = binding.add_track(unreal.MovieScene3DTransformTrack)
    section = track.add_section()
    section.set_range(0, END)
    channels = section.get_all_channels()
    for frame, location, rotation in keys:
        # Transform channels are translation XYZ, then rotation roll/pitch/yaw.
        values = list(location) + [rotation[2], rotation[0], rotation[1]] + [scale] * 3
        for index, value in enumerate(values):
            channels[index].add_key(unreal.FrameNumber(frame), float(value))
    return section

transform(cam_bind, [
    (0, (390, 1150, 245), (-2, -90, 0)),
    (201, (390, 1150, 245), (-2, -90, 0)),
    (205, (402, 1150, 249), (-2, -90, 0)),
    (209, (376, 1150, 237), (-2, -90, 0)),
    (213, (410, 1150, 251), (-2, -90, 0)),
    (217, (382, 1150, 240), (-2, -90, 0)),
    (222, (450, 1150, 245), (-2, -90, 0)),
    (263, (1110, 1150, 245), (-2, -90, 0)),
    (474, (1110, 1150, 245), (-2, -90, 0)),
    (570, (1450, 1150, 245), (-2, -90, 0)),
    (600, (1550, 1150, 245), (-2, -90, 0)),
])
transform(dragon_bind, [
    (0, (1271.6, 3.5, 132.2), (-30, 180, 0)),
    (200, (1271.6, 3.5, 132.2), (-30, 180, 0)),
    (216, (1255, 3.5, 120), (-34, 180, 0)),
    (260, (1271.6, 3.5, 132.2), (-30, 180, 0)),
    (477, (1271.6, 3.5, 132.2), (-30, 180, 0)),
    (525, (1450, -40, 115), (-37, 180, 0)),
    (570, (1730, -110, 113), (-34, 180, 0)),
    (600, (1980, -170, 110), (-34, 180, 0)),
], scale=7.5)

cut_track = seq.add_track(unreal.MovieSceneCameraCutTrack)
cut = cut_track.add_section()
cut.set_range(0, END)
cam_id = unreal.MovieSceneObjectBindingID()
cam_id.set_editor_property('guid', cam_bind.get_id())
cut.set_camera_binding_id(cam_id)

anim_track = hero_bind.add_track(unreal.MovieSceneSkeletalAnimationTrack)
for start, end, animation in ((0, 171, crouch), (171, 222, draw), (222, END, crouch)):
    section = anim_track.add_section()
    section.set_range(start, end)
    section.params.set_editor_property('animation', animation)

def visibility(binding, start, end):
    track = binding.add_track(unreal.MovieSceneVisibilityTrack)
    section = track.add_section()
    section.set_range(0, END)
    channel = section.get_all_channels()[0]
    if start > 0:
        channel.add_key(unreal.FrameNumber(0), False)
    channel.add_key(unreal.FrameNumber(start), True)
    if end < END:
        channel.add_key(unreal.FrameNumber(end), False)

visibility(note_bind, 276, 420)
visibility(sign_bind, 485, END)
visibility(flame_bind, 200, 255)

caption_times = (
    ('01_Hero', 12, 75),
    ('02_Dragon', 76, 180),
    ('03_Missing', 282, 350),
    ('04_Protest', 405, 500),
)
for name, start, end in caption_times:
    actor = spawn_static('Subtitle_' + name, plane, (0, 0, 0), (1, 1, 1), mat=materials[name])
    actor.attach_to_actor(camera, '', unreal.AttachmentRule.KEEP_RELATIVE,
                          unreal.AttachmentRule.KEEP_RELATIVE,
                          unreal.AttachmentRule.KEEP_RELATIVE, False)
    actor.set_actor_relative_location(unreal.Vector(500, 0, -95), False, False)
    actor.set_actor_relative_rotation(unreal.Rotator(90, 0, -90), False, False)
    actor.set_actor_relative_scale3d(unreal.Vector(-4.4, .50, 1))
    visibility(bind(actor), start, end)

audio_track = seq.add_track(unreal.MovieSceneAudioTrack)
for filename, start in (( '01_Hero_Challenge', 12), ('02_Dragon_Threat', 76),
                        ('03_Dragon_MissingLegs', 282), ('04_Dragon_Protest', 405)):
    sound = voices[filename]
    section = audio_track.add_section()
    with wave.open(str(ROOT / 'Voice' / (filename + '.wav')), 'rb') as wav:
        duration = wav.getnframes() / wav.getframerate()
    section.set_range(start, min(END, start + int(duration * FPS) + 2))
    section.set_editor_property('sound', sound)

autoplay.set_sequence(seq)
settings = autoplay.get_editor_property('playback_settings')
settings.set_editor_property('auto_play', True)
settings.set_editor_property('pause_at_end', True)
autoplay.set_editor_property('playback_settings', settings)
library.save_loaded_asset(seq)
assert unreal.EditorLevelLibrary.save_current_level()
unreal.EditorLevelLibrary.set_level_viewport_camera_info(
    camera.get_actor_location(), camera.get_actor_rotation())
unreal.log('BOSS_PROLOGUE_BUILD_OK level=' + LEVEL + ' sequence=' + SEQ)
