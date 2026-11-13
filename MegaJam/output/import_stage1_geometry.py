import json
from pathlib import Path
import unreal

source=Path(r'C:\LHH\Epic_AI_MegaJam\MegaJam\output\Stage1_Unreal_Export')
destination='/Game/Stage1Generated/PivotReady'
files=['Wheel_High','Wheel_Low','Gear_High','Gear_Low','LiftPlatform']
tasks=[]
for name in files:
    task=unreal.AssetImportTask()
    task.filename=str(source/(name+'.fbx'))
    task.destination_path=destination
    task.destination_name=name
    task.automated=True
    task.replace_existing=False
    task.save=True
    ui=unreal.FbxImportUI()
    ui.import_as_skeletal=False
    ui.import_materials=True
    ui.import_textures=False
    ui.static_mesh_import_data.combine_meshes=True
    ui.static_mesh_import_data.auto_generate_collision=False
    task.options=ui
    tasks.append(task)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
report={t.destination_name:list(t.imported_object_paths) for t in tasks}
(source/'import_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
unreal.log('STAGE1_GEOMETRY_IMPORT_COMPLETE '+json.dumps(report))
