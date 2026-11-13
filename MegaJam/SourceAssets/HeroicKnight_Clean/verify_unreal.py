"""Reload the saved UE assets and test level after the final FBX import."""

import json
from pathlib import Path
import unreal


ROOT = Path(r'D:\UnrealProject\Epic_AI_MegaJam\MegaJam\SourceAssets\HeroicKnight_Clean')
with (ROOT / 'unreal_import_report.json').open(encoding='utf-8') as f:
    imported = json.load(f)
with (ROOT / 'unreal_test_report.json').open(encoding='utf-8') as f:
    test = json.load(f)

mesh = unreal.load_asset(imported['mesh'])
animation = unreal.load_asset(imported['animations'][0])
material = unreal.load_asset(imported['material'])
physics = unreal.load_asset(imported['physics_asset'])
assert mesh and animation and material and physics
assert mesh.get_editor_property('skeleton') == animation.get_editor_property('skeleton')
assert mesh.get_editor_property('physics_asset') == physics
slots = list(mesh.get_editor_property('materials'))
assert len(slots) == 1 and slots[0].get_editor_property('material_interface') == material
assert abs(animation.get_play_length() - 2.0) < 0.01

skeletal_editor = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
assert skeletal_editor.is_physics_asset_compatible(mesh, physics)

levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.load_level(test['level'])
knight = [a for a in unreal.EditorLevelLibrary.get_all_level_actors()
          if a.get_actor_label() == 'HeroicKnight_Clean_Idle_Test']
assert len(knight) == 1
component = knight[0].get_editor_property('skeletal_mesh_component')
assert component.get_skeletal_mesh_asset() == mesh

samples = [x for x in unreal.MaterialEditingLibrary.get_material_expressions(material)
           if isinstance(x, unreal.MaterialExpressionTextureSample)]
used_textures = [x.get_editor_property('texture').get_path_name() for x in samples
                 if x.get_editor_property('texture')]
for expected in imported['textures']:
    assert expected in used_textures, (expected, used_textures)

report = {
    'mesh': mesh.get_path_name(),
    'height_cm': 2.0 * mesh.get_imported_bounds().box_extent.z,
    'animation': animation.get_path_name(),
    'animation_length_s': animation.get_play_length(),
    'material': material.get_path_name(),
    'material_textures': used_textures,
    'physics_asset': physics.get_path_name(),
    'physics_asset_compatible': True,
    'test_level': test['level'],
    'test_actor': knight[0].get_actor_label(),
}
with (ROOT / 'unreal_validation.json').open('w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)
unreal.log('HEROIC_KNIGHT_UE_VALIDATION_OK ' + json.dumps(report))
