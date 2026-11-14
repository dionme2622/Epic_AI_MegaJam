import bpy,json,sys
from pathlib import Path
from mathutils import Vector
out={}
for f in ('Wheel_High','Wheel_Low','Gear_High','Gear_Low'):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(Path('C:/LHH/Epic_AI_MegaJam/MegaJam/output/Stage1_Unreal_Export')/(f+'.fbx')))
 objs=[]
 for o in bpy.context.scene.objects:
  if o.type=='MESH':
   pts=[o.matrix_world@Vector(c) for c in o.bound_box]
   objs.append({'name':o.name,'pos':list(o.location),'dims':list(o.dimensions),'bounds':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]],'mats':[m.name for m in o.data.materials]})
 out[f]=objs
print('MESH_REPORT',json.dumps(out))
