import bpy,sys
from mathutils import Vector
for name in ['SM_Film_Three','SM_Film_Arrow','SM_Film_Gear']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath='C:/LHH/Epic_AI_MegaJam/MegaJam/output/FilmRestore/'+name+'.fbx')
 for o in bpy.context.scene.objects:
  if o.type=='MESH':
   vs=[o.matrix_world@v.co for v in o.data.vertices]
   print('BOUNDS',name,[(round(min(v[i] for v in vs),2),round(max(v[i] for v in vs),2)) for i in range(3)],'verts',len(vs))
