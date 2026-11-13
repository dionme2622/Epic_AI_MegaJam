import json, unreal
from pathlib import Path
names=['Stage1_Ground','Stage1_Backdrop','Wheel_High','Wheel_Low','Gear_High','Gear_Low','LiftPlatform']
out={}
for n in names:
    folder = '/Game/Stage1Generated/Meshes/' if n.startswith('Stage1_') else '/Game/Stage1Generated/PivotReady/'
    mesh=unreal.load_asset(folder+n)
    if not mesh: out[n]=None; continue
    b=mesh.get_bounding_box()
    out[n]={'min':[b.min.x,b.min.y,b.min.z], 'max':[b.max.x,b.max.y,b.max.z], 'materials':[str(m.material_interface.get_path_name()) if m.material_interface else None for m in mesh.static_materials]}
Path(r'C:\LHH\Epic_AI_MegaJam\MegaJam\output\Stage1_Unreal_Export\bounds_report.json').write_text(json.dumps(out,indent=2),encoding='utf8')
