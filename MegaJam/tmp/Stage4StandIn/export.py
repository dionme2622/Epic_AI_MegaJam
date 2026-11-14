import bpy, bmesh
from pathlib import Path
out=Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4StandIn")
src=bpy.data.objects["SM_Vault_Drapery"]
bm=bmesh.new()
bm.from_mesh(src.data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.x<20],context="VERTS")
for v in bm.verts: v.co.y*=-1
bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
mesh=bpy.data.meshes.new("SM_StandIn_ExhibitCurtains")
bm.to_mesh(mesh)
bm.free()
for m in src.data.materials: mesh.materials.append(m)
obj=bpy.data.objects.new(mesh.name,mesh)
bpy.context.collection.objects.link(obj)
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active=obj
bpy.ops.export_scene.fbx(filepath=str(out/(obj.name+".fbx")),use_selection=True,object_types={"MESH"},axis_forward="-Y",axis_up="Z",mesh_smooth_type="FACE",add_leaf_bones=False,bake_anim=False)
