import bpy
from pathlib import Path
from mathutils import Vector
root=Path('C:/LHH/Epic_AI_MegaJam/MegaJam/output/FocusPuzzle/Detail')
for name in ['SM_FocusDetail_Brass','SM_FocusDetail_Wood','SM_FocusDetail_Curtain']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(root/(name+'.fbx')))
 for o in bpy.context.scene.objects:
  if o.type=='MESH':
   p=[o.matrix_world@Vector(v.co) for v in o.data.vertices]
   print(name,'minmax',[[round(min(v[i] for v in p),2) for i in range(3)],[round(max(v[i] for v in p),2) for i in range(3)]],flush=True)
