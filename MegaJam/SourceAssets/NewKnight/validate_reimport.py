import bpy, json
from pathlib import Path
root=Path(r'D:\UnrealProject\Epic_AI_MegaJam\MegaJam\SourceAssets\NewKnight')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(root/'Knight_New_Combat_Idle.fbx'))
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        print('MESH',o.name,'verts',len(o.data.vertices),'mats',[m.name for m in o.data.materials], 'bbox',[(round(min((o.matrix_world@v.co)[i] for v in o.data.vertices),3),round(max((o.matrix_world@v.co)[i] for v in o.data.vertices),3)) for i in range(3)])
    if o.type == 'ARMATURE':
        print('ARM',o.name,'bones',len(o.data.bones),'action',o.animation_data.action.name if o.animation_data and o.animation_data.action else None)
