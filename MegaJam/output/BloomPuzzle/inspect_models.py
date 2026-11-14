import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path('C:/LHH/Epic_AI_MegaJam/MegaJam/output/BloomPuzzle')
for n in ['SM_Bloom_Frame','SM_Bloom_Star','SM_Bloom_Moon','SM_Bloom_Sun']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(root/(n+'.fbx')))
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  pts=[o.matrix_world@Vector(c) for c in o.bound_box]
  print('MESH',n,o.name,'dims',list(o.dimensions),'minmax',[[round(min(v[i] for v in pts),3) for i in range(3)],[round(max(v[i] for v in pts),3) for i in range(3)]],flush=True)
