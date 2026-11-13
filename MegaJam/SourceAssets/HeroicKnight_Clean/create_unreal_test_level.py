"""Create a small UE level to inspect the imported knight and idle animation."""

import json
from pathlib import Path
import unreal


ROOT = Path(r'D:\UnrealProject\Epic_AI_MegaJam\MegaJam\SourceAssets\HeroicKnight_Clean')
DEST = '/Game/Assets/HeroicKnight_Clean'
LEVEL = DEST + '/L_HeroicKnight_Clean_Test'
with (ROOT / 'unreal_import_report.json').open(encoding='utf-8') as f:
    report = json.load(f)

mesh = unreal.load_asset(report['mesh'])
animations = [unreal.load_asset(x) for x in report['animations']]
assert mesh and len(animations) == 1 and animations[0]
animation = animations[0]

levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(LEVEL):
    assert levels.load_level(LEVEL)
else:
    assert levels.new_level(LEVEL)

for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    unreal.EditorLevelLibrary.destroy_actor(actor)

knight = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
knight.set_actor_label('HeroicKnight_Clean_Idle_Test')
component = knight.get_editor_property('skeletal_mesh_component')
component.set_skeletal_mesh_asset(mesh)
component.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
component.set_animation(animation)
component.play(True)

floor_mesh = unreal.load_asset('/Engine/BasicShapes/Plane')
assert floor_mesh
floor_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.StaticMeshActor, unreal.Vector(0, 0, -2), unreal.Rotator(0, 0, 0))
floor_actor.set_actor_label('Preview_Floor')
floor_actor.static_mesh_component.set_static_mesh(floor_mesh)
floor_actor.set_actor_scale3d(unreal.Vector(4, 4, 1))

sun = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.DirectionalLight, unreal.Vector(0, 0, 300), unreal.Rotator(-35, -45, 0))
sun.set_actor_label('Preview_Key_Light')
sky = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.SkyLight, unreal.Vector(0, 0, 250))
sky.set_actor_label('Preview_Sky_Light')

camera = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.CineCameraActor, unreal.Vector(-350, -450, 170), unreal.Rotator(-8, 50, 0))
camera.set_actor_label('Preview_Camera')

unreal.EditorLevelLibrary.save_current_level()
assert unreal.EditorAssetLibrary.does_asset_exist(LEVEL)
test_report = {
    'level': LEVEL,
    'mesh': mesh.get_path_name(),
    'animation': animation.get_path_name(),
    'actors': [a.get_actor_label() for a in unreal.EditorLevelLibrary.get_all_level_actors()],
}
with (ROOT / 'unreal_test_report.json').open('w', encoding='utf-8') as f:
    json.dump(test_report, f, indent=2)
unreal.log('HEROIC_KNIGHT_TEST_LEVEL_OK ' + json.dumps(test_report))
