import runpy
from pathlib import Path

import unreal as u

PROJECT = Path(r'C:/LHH/Epic_AI_MegaJam/MegaJam')
MAIN = '/Game/DirectorCut/Stage/Stage3_'
TAKE = '/Game/Stage3Integrated/Sections/L_Bloom'
BRIDGE = '/Game/Stage3Integrated/Sections/L_Resolution'
ARCHIVE = '/Game/Stage3Integrated/Archive'
THEATRE = '/Game/Stage4Integrated/Theatre'
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
lib = u.EditorAssetLibrary
tools = u.AssetToolsHelpers.get_asset_tools()
edit = u.MaterialEditingLibrary


def load(path):
    assert levels.load_level(path), path
    return {actor.get_actor_label(): actor for actor in actors.get_all_level_actors()}


def asset(path):
    result = lib.load_asset(path)
    assert result, path
    return result


def place(existing, label, cls, position, rotation=None):
    location = u.Vector(*position)
    rotation = rotation or u.Rotator()
    item = existing.get(label)
    if item is None:
        item = actors.spawn_actor_from_class(cls, location, rotation)
        assert item, label
        item.set_actor_label(label)
        existing[label] = item
    else:
        item.set_actor_location_and_rotation(location, rotation, False, True)
    item.set_folder_path('Stage3/Two Takes and Projected Bridge')
    return item


def mesh(existing, label, model, position, scale=(1, 1, 1), material=None, movable=False, blocking=False):
    item = place(existing, label, u.StaticMeshActor, position)
    component = item.static_mesh_component
    component.set_mobility(u.ComponentMobility.MOVABLE if movable else u.ComponentMobility.STATIC)
    component.set_static_mesh(model)
    component.set_collision_profile_name('BlockAll' if blocking else 'NoCollision')
    component.set_cast_shadow(not blocking)
    item.set_actor_scale3d(u.Vector(*scale))
    if material:
        component.set_material(0, material)
    return item


def text(existing, label, value, position, size):
    item = place(existing, label, u.TextRenderActor, position, u.Rotator(0, 0, 90))
    renderer = item.get_component_by_class(u.TextRenderComponent)
    renderer.set_text(value)
    renderer.set_horizontal_alignment(u.HorizTextAligment.EHTA_CENTER)
    renderer.set_text_render_color(u.Color(255, 217, 149, 255))
    renderer.set_world_size(size)
    return item


def hide(item):
    item.set_actor_hidden_in_game(True)
    item.set_actor_enable_collision(False)


def light_material(name, color, alpha=None):
    path = f'{ARCHIVE}/{name}'
    mat = lib.load_asset(path) if lib.does_asset_exist(path) else tools.create_asset(name, ARCHIVE, u.Material, u.MaterialFactoryNew())
    mat.set_editor_property('shading_model', u.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property('blend_mode', u.BlendMode.BLEND_TRANSLUCENT if alpha is not None else u.BlendMode.BLEND_OPAQUE)
    edit.delete_all_material_expressions(mat)
    tint = edit.create_material_expression(mat, u.MaterialExpressionConstant3Vector, -220, 0)
    tint.set_editor_property('constant', u.LinearColor(*color, 1))
    edit.connect_material_property(tint, '', u.MaterialProperty.MP_EMISSIVE_COLOR)
    if alpha is not None:
        mat.set_editor_property('used_with_skeletal_mesh', True)
        opacity = edit.create_material_expression(mat, u.MaterialExpressionConstant, -220, 120)
        opacity.set_editor_property('r', alpha)
        edit.connect_material_property(opacity, '', u.MaterialProperty.MP_OPACITY)
    edit.recompile_material(mat)
    assert lib.save_loaded_asset(mat, only_if_is_dirty=False)
    return mat


def save():
    assert levels.save_current_level()


models = runpy.run_path(str(PROJECT / 'SourceAssets/Stage3TakeBridge/import_props.py'))['import_props']()
cube = asset('/Engine/BasicShapes/Cube')
sphere = asset('/Engine/BasicShapes/Sphere')
ghost = light_material('M_S3Take_Ghost', (.10, .68, 1.20), .48)
cyan = light_material('M_S3Projection_Cyan', (.22, 1.02, 1.17))
gold = light_material('M_S3Projection_Gold', (1.32, .69, .18))
scratch = light_material('M_S3Projection_Grain', (.22, .29, .36))

take_class = u.load_class(None, '/Script/MegaJam.Stage3TakePuzzle')
assert take_class
existing = load(TAKE)
door = existing['Bloom_ExitDoor']
old_controller = existing.get('Bloom_Controller')
if old_controller:
    assert actors.destroy_actor(old_controller)
for label, item in existing.items():
    if label.startswith(('Bloom Shutter Clue', 'Bloom_Sign_', 'Bloom_Number_', 'Bloom_Instructions', 'Bloom_ConsoleLabel', 'Stage3 Film Scene', 'Bloom_PostProcess')):
        hide(item)
existing['Bloom_PostProcess'].set_editor_property('enabled', False)

controller = place(existing, 'Two Takes Controller', take_class, (0, 0, 0))
controller.set_editor_property('ExitDoor', door)
controller.set_editor_property('GhostMaterial', ghost)
camera = asset(f'{ARCHIVE}/SM_Stage3_ArchiveCamera')
mesh(existing, 'Take Recorder Camera', camera, (1050, -160, 4), (.9, .9, .9))
text(existing, 'Take Recorder Sign', 'TWO TAKES  /  E CAMERA', (1050, -120, 234), 24)
for x, mark, prop in ((690, 'TAKE 1', 'LeftLamp'), (1420, 'TAKE 2', 'RightLamp')):
    mesh(existing, f'{mark} Pressure Plate', models['SM_S3Take_PressurePlate'], (x, 0, 4))
    mesh(existing, f'{mark} Cue Lamp', models['SM_S3Take_CueLamp'], (x, -132, 3))
    lit = mesh(existing, f'{mark} Activated Light', sphere, (x, -112, 69), (.21, .08, .21), cyan)
    lit.set_actor_hidden_in_game(True)
    controller.set_editor_property(prop, lit)
    text(existing, f'{mark} Sign', mark, (x, -110, 212), 26)
save()

existing = load(BRIDGE)
res = existing['Resolution_Controller']
existing['Resolution_NonblockingPit'].set_actor_enable_collision(False)
for label, item in existing.items():
    if (label.startswith(('Archive Resolution Choice', 'Reel Station', 'Film Decoder', 'Resolution_DotPattern_', 'Resolution_Guide_', 'Archive Walkway Resolution_'))
            or label in ('Resolution_Tile_1', 'Resolution_Tile_2', 'Resolution_Tile_4', 'Resolution_Tile_5')):
        hide(item)

screen = mesh(existing, 'Bridge Projection Screen', models['SM_S3Bridge_ProjectionScreen'], (682, -100, 326))
desk = mesh(existing, 'Bridge Splice Desk', models['SM_S3Bridge_SpliceDesk'], (210, -125, 3))
text(existing, 'Bridge Desk Sign', 'E  /  FILM SPLICER', (210, -88, 183), 26)
clips = [mesh(existing, f'Bridge Film Clip {i + 1}', models['SM_S3Bridge_FilmClip'], (210 + offset, -80, 75), movable=True)
         for i, offset in enumerate((-43, 43))]
platforms = []
for i, x in enumerate((481, 959), 1):
    body = mesh(existing, f'Bridge Platform {i} Collision', cube, (x, 0, -15), (3.20, 1.48, .30), movable=True, blocking=True)
    body.static_mesh_component.set_hidden_in_game(True)
    platform_art = mesh(existing, f'Bridge Platform {i} Model', models['SM_S3Bridge_Platform'], (x, 0, 0), (1.60, 1, 1), movable=True)
    platform_art.attach_to_actor(body, '', u.AttachmentRule.KEEP_WORLD, u.AttachmentRule.KEEP_WORLD, u.AttachmentRule.KEEP_WORLD, False)
    mesh(existing, f'Bridge Platform {i} Rail', models['SM_S3Bridge_Rail'], (x, 0, -70), (1.33, 1, 1))
    platforms.append(body)

for key, value in {
        'bUseStationChoices': False, 'bUseReelHunt': False, 'bUseProjectedBridge': True,
        'BridgePlatforms': platforms, 'BridgeClipActors': clips, 'BridgeConsole': desk,
        'ProjectionScreen': screen, 'ProjectionLineMaterial': cyan, 'ProjectionSelectedMaterial': gold,
        'ProjectionScratchMaterial': scratch, 'GuidanceArrows': [], 'InitialBridgeNotches': [1, -2],
        'bUseLocalCheckpoint': True, 'LocalCheckpointOffset': u.Vector(210, 0, 65),
        'bRestrictOverlayStart': True, 'ShowOverlayFromOffsetX': -40., 'HideOverlayBeyondX': 1370.,
    }.items():
    res.set_editor_property(key, value)
save()

existing = load(MAIN)
for label, item in existing.items():
    if label.startswith('Archive Mosaic Frame') or label == 'Stage3 Film Editing Console':
        hide(item)
save()
u.log('STAGE3 TWO TAKES AND PROJECTED BRIDGE SAVED')
