"""Import the authored Stage3 Take/Bridge meshes, without modifying levels."""

import json
from pathlib import Path

import unreal


def import_props(destination="/Game/Stage3Integrated/Archive"):
    export_path = Path(__file__).resolve().parent / "Exports"
    manifest = json.loads((export_path / "mesh_manifest.json").read_text(encoding="utf-8"))
    library = unreal.EditorAssetLibrary
    tasks = []
    for name in manifest:
        source = export_path / f"{name}.fbx"
        if not source.is_file():
            raise FileNotFoundError(source)

        options = unreal.FbxImportUI()
        options.import_as_skeletal = False
        options.import_materials = False
        options.import_textures = False
        options.static_mesh_import_data.auto_generate_collision = False
        options.static_mesh_import_data.combine_meshes = True

        task = unreal.AssetImportTask()
        task.filename = str(source)
        task.destination_path = destination
        task.destination_name = name
        task.automated = True
        task.replace_existing = True
        task.options = options
        tasks.append(task)

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    meshes = {}
    for name, info in manifest.items():
        mesh = library.load_asset(f"{destination}/{name}")
        if not mesh:
            raise RuntimeError(f"Mesh import failed: {name}")

        imported_slots = mesh.get_editor_property("static_materials")
        imported_names = {str(slot.get_editor_property("imported_material_slot_name")) for slot in imported_slots}
        if imported_names != set(info["material_slots"]):
            raise RuntimeError(f"Unexpected slot names for {name}: {sorted(imported_names)}")
        for index, slot in enumerate(imported_slots):
            slot_name = str(slot.get_editor_property("imported_material_slot_name"))
            material = library.load_asset(f"/Game/Stage4Integrated/Theatre/{slot_name}")
            if not material:
                raise RuntimeError(f"Missing theatre material: {slot_name}")
            mesh.set_material(index, material)

        if not library.save_loaded_asset(mesh, only_if_is_dirty=False):
            raise RuntimeError(f"Could not save mesh: {name}")
        meshes[name] = mesh
    return meshes


if __name__ == "__main__":
    unreal.log(f"Imported {len(import_props())} Stage3 Take and Bridge meshes.")
