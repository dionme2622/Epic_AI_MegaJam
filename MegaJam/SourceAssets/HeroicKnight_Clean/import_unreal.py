"""Import the hand-rigged knight and its baked textures into UE 5.8."""

import json
from pathlib import Path
import unreal


ROOT = Path(r'D:\UnrealProject\Epic_AI_MegaJam\MegaJam\SourceAssets\HeroicKnight_Clean')
DEST = '/Game/Assets/HeroicKnight_Clean'
FBX = ROOT / 'HeroicKnight_Clean_Rigged.fbx'
BASE = ROOT / 'CleanUV_BaseColor.png'
ORM = ROOT / 'CleanUV_ORM.png'

for path in (FBX, BASE, ORM):
    if not path.is_file():
        raise FileNotFoundError(path)

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
unreal.EditorAssetLibrary.make_directory(DEST)


def import_file(path, options=None):
    task = unreal.AssetImportTask()
    task.set_editor_property('filename', str(path))
    task.set_editor_property('destination_path', DEST)
    task.set_editor_property('automated', True)
    task.set_editor_property('save', True)
    task.set_editor_property('replace_existing', True)
    if options is not None:
        task.set_editor_property('options', options)
    asset_tools.import_asset_tasks([task])
    paths = list(task.get_editor_property('imported_object_paths'))
    unreal.log('HEROIC_KNIGHT_IMPORTED ' + path.name + ': ' + repr(paths))
    return paths


fbx_options = unreal.FbxImportUI()
fbx_options.set_editor_property('automated_import_should_detect_type', False)
fbx_options.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_SKELETAL_MESH)
fbx_options.set_editor_property('import_as_skeletal', True)
fbx_options.set_editor_property('import_mesh', True)
fbx_options.set_editor_property('import_animations', True)
fbx_options.set_editor_property('import_materials', False)
fbx_options.set_editor_property('import_textures', False)
fbx_options.set_editor_property('create_physics_asset', True)
fbx_paths = import_file(FBX, fbx_options)
base_paths = import_file(BASE)
orm_paths = import_file(ORM)

assets = {}
for path in unreal.EditorAssetLibrary.list_assets(DEST, recursive=True, include_folder=False):
    obj = unreal.load_asset(path)
    if obj:
        assets[path] = obj


def one(cls, source_paths=None):
    source_paths = source_paths or assets.keys()
    found = [assets[p] for p in source_paths if p in assets and isinstance(assets[p], cls)]
    if len(found) != 1:
        raise RuntimeError('Expected one ' + cls.__name__ + ', got ' + repr([x.get_path_name() for x in found]))
    return found[0]


mesh = one(unreal.SkeletalMesh, fbx_paths)
base_tex = one(unreal.Texture2D, base_paths)
orm_tex = one(unreal.Texture2D, orm_paths)
orm_tex.set_editor_property('srgb', False)
orm_tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
unreal.EditorAssetLibrary.save_loaded_asset(orm_tex)

mat_path = DEST + '/M_HeroicKnight_Clean'
mat = unreal.load_asset(mat_path)
if mat is None:
    mat = asset_tools.create_asset('M_HeroicKnight_Clean', DEST, unreal.Material, unreal.MaterialFactoryNew())
if mat is None:
    raise RuntimeError('Could not create material')

lib = unreal.MaterialEditingLibrary
lib.delete_all_material_expressions(mat)
base_node = lib.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -450, -100)
base_node.set_editor_property('texture', base_tex)
orm_node = lib.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -450, 200)
orm_node.set_editor_property('texture', orm_tex)
orm_node.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
assert lib.connect_material_property(base_node, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)
assert lib.connect_material_property(orm_node, 'R', unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
assert lib.connect_material_property(orm_node, 'G', unreal.MaterialProperty.MP_ROUGHNESS)
assert lib.connect_material_property(orm_node, 'B', unreal.MaterialProperty.MP_METALLIC)
lib.set_base_material_usage(mat, unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH)
lib.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)

slots = list(mesh.get_editor_property('materials'))
if not slots:
    raise RuntimeError('Imported skeletal mesh has no material slot')
for slot in slots:
    slot.set_editor_property('material_interface', mat)
mesh.set_editor_property('materials', slots)

skeletal_editor = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
physics = mesh.get_editor_property('physics_asset')
if physics is None:
    physics = skeletal_editor.create_physics_asset(mesh, True, 0)
if physics is None or not skeletal_editor.is_physics_asset_compatible(mesh, physics):
    raise RuntimeError('Physics asset was not generated or is incompatible')
unreal.EditorAssetLibrary.save_loaded_asset(physics)
unreal.EditorAssetLibrary.save_loaded_asset(mesh)

animations = [assets[p] for p in fbx_paths if p in assets and isinstance(assets[p], unreal.AnimSequence)]
animation_reused = False
if not animations:
    # Interchange returns only the mesh path on FBX reimport; the sequence
    # remains as the existing asset with the same source FBX.
    old_animation = unreal.load_asset(DEST + '/HeroicKnight_Clean_Rigged_Anim')
    if old_animation and isinstance(old_animation, unreal.AnimSequence):
        animations = [old_animation]
        animation_reused = True
if len(animations) != 1:
    raise RuntimeError('Expected one animation sequence from FBX, got ' + repr(fbx_paths))
for animation in animations:
    if animation.get_editor_property('skeleton') != mesh.get_editor_property('skeleton'):
        raise RuntimeError('Animation uses a different skeleton from the mesh')
    if not 1.8 < animation.get_play_length() < 2.2:
        raise RuntimeError('Unexpected idle length: ' + str(animation.get_play_length()))
    unreal.EditorAssetLibrary.save_loaded_asset(animation)

bounds = mesh.get_imported_bounds()
height_cm = 2.0 * bounds.box_extent.z
if not 160.0 < height_cm < 190.0:
    raise RuntimeError('Knight import has unexpected height in cm: ' + str(height_cm))

report = {
    'fbx': str(FBX),
    'mesh': mesh.get_path_name(),
    'skeleton': mesh.get_editor_property('skeleton').get_path_name(),
    'animations': [a.get_path_name() for a in animations],
    'material': mat.get_path_name(),
    'textures': [base_tex.get_path_name(), orm_tex.get_path_name()],
    'material_slots': len(slots),
    'height_cm': height_cm,
    'animation_lengths_s': [a.get_play_length() for a in animations],
    'animation_reused_on_reimport': animation_reused,
    'physics_asset': physics.get_path_name(),
    'asset_paths': sorted(assets.keys()),
}
with (ROOT / 'unreal_import_report.json').open('w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)
unreal.log('HEROIC_KNIGHT_IMPORT_OK ' + json.dumps(report))
