"""Import the independently modelled Stage 3 art; no levels are modified."""
import unreal as u
from pathlib import Path

src = Path(r'C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage3ResolutionArt/export')
folder = '/Game/Stage3Integrated/Archive'
names = ('SM_S3_DotRing', 'SM_S3_StainedGlass', 'SM_S3_TileRim',
         'SM_S3_BloomStar', 'SM_S3_BloomMoon', 'SM_S3_BloomSun')
lib = u.EditorAssetLibrary
tools = u.AssetToolsHelpers.get_asset_tools()
tasks = []
for name in names:
    if not lib.does_asset_exist(f'{folder}/{name}'):
        task = u.AssetImportTask()
        task.filename = str(src / f'{name}.fbx')
        task.destination_path = folder
        task.destination_name = name
        task.automated = True
        task.save = False
        options = u.FbxImportUI()
        options.import_as_skeletal = False
        options.import_materials = False
        options.import_textures = False
        options.static_mesh_import_data.auto_generate_collision = False
        options.static_mesh_import_data.combine_meshes = True
        task.options = options
        tasks.append(task)
if tasks:
    tools.import_asset_tasks(tasks)
for name in names:
    mesh = lib.load_asset(f'{folder}/{name}')
    assert mesh, name
    for index, slot in enumerate(mesh.get_editor_property('static_materials')):
        material_name = str(slot.get_editor_property('imported_material_slot_name'))
        material = lib.load_asset(f'/Game/Stage4Integrated/Theatre/{material_name}')
        assert material, (name, material_name)
        mesh.set_material(index, material)
    assert lib.save_loaded_asset(mesh, only_if_is_dirty=False)
u.log('STAGE3 RESOLUTION ART IMPORTED')
