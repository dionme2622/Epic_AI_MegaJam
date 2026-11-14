"""Run with Unreal's Python command only when the project editor is ready."""
from pathlib import Path
import unreal as u

source = Path(r'C:/LHH/Epic_AI_MegaJam/MegaJam/SourceAssets/Stage3PuzzleArt')
destination = '/Game/Stage3Integrated/Archive'
names = [
    'SM_Stage3_ArchiveCamera', 'SM_Stage3_FilmRack', 'SM_Stage3_EditConsole',
    'SM_Stage3_StageSpotlight', 'SM_Stage3_FilmCanStack',
]
assets = u.EditorAssetLibrary
tools = u.AssetToolsHelpers.get_asset_tools()
materials = {
    n.rsplit('/', 1)[-1].split('.')[0]: assets.load_asset(n)
    for n in assets.list_assets('/Game/Stage4Integrated/Theatre', False)
    if n.rsplit('/', 1)[-1].startswith('M')
}
tasks=[]
for name in names:
    task=u.AssetImportTask()
    task.filename=str(source / (name+'.fbx'))
    task.destination_path=destination
    task.destination_name=name
    task.automated=True
    task.replace_existing=True
    task.save=False
    options=u.FbxImportUI()
    options.import_as_skeletal=False
    options.import_materials=False
    options.import_textures=False
    options.static_mesh_import_data.auto_generate_collision=False
    options.static_mesh_import_data.combine_meshes=True
    task.options=options
    tasks.append(task)
tools.import_asset_tasks(tasks)
for name in names:
    mesh=assets.load_asset(destination+'/'+name)
    assert mesh, name
    for i, slot in enumerate(mesh.get_editor_property('static_materials')):
        key=str(slot.get_editor_property('imported_material_slot_name'))
        assert key in materials, (name,key)
        mesh.set_material(i, materials[key])
    assert assets.save_loaded_asset(mesh, only_if_is_dirty=False)
print('STAGE3 PUZZLE PROPS IMPORTED')
