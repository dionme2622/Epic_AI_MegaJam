import unreal as u
from pathlib import Path
D="/Game/Stage4Integrated/Theatre"
BASE=Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4Retake")
lib=u.EditorAssetLibrary
tools=u.AssetToolsHelpers.get_asset_tools()
mats={n.split("/")[-1].split(".")[0]:lib.load_asset(n) for n in lib.list_assets(D,False) if n.split("/")[-1].startswith("M")}
tasks=[]
for idx in range(1,10):
    name=f"SM_Vault_RetakeDeck_{idx:02}"
    if lib.does_asset_exist(f"{D}/{name}"):
        continue
    task=u.AssetImportTask()
    task.filename=str(BASE/(name+".fbx"))
    task.destination_name=name
    task.destination_path=D
    task.automated=True
    task.save=False
    fbx=u.FbxImportUI()
    fbx.import_as_skeletal=False
    fbx.import_materials=False
    fbx.import_textures=False
    fbx.static_mesh_import_data.combine_meshes=True
    fbx.static_mesh_import_data.auto_generate_collision=False
    task.options=fbx
    tasks.append(task)
if tasks:
    tools.import_asset_tasks(tasks)
for idx in range(1,10):
    name=f"SM_Vault_RetakeDeck_{idx:02}"
    mesh=lib.load_asset(f"{D}/{name}")
    assert mesh
    for i,s in enumerate(mesh.get_editor_property("static_materials")):
        key=str(s.get_editor_property("imported_material_slot_name"))
        assert key in mats,(key,name)
        mesh.set_material(i,mats[key])
    assert lib.save_loaded_asset(mesh,only_if_is_dirty=False),name
u.log("RETAKE MESHES READY")

