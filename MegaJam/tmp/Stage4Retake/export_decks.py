"""Export the original platform geometry as independently movable panels."""
import bpy
import bmesh
from pathlib import Path

out = Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4Retake")
source = bpy.data.objects["SM_Vault_PlatformFaces"]
# Split on empty space between the original ledges. Keep the original UVs,
# stone/bevel geometry, slots and world-aligned origin.
edges = [-560, 395, 630, 868, 1135, 1589, 1849, 2241, 2508, 3400]
for index, (lo, hi) in enumerate(zip(edges, edges[1:]), 1):
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.collection.objects.link(obj)
    obj.name = f"SM_Vault_RetakeDeck_{index:02}"
    obj.data.name = obj.name
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not (lo * .01 < v.co.x < hi * .01)], context='VERTS')
    assert len(bm.faces) > 20, obj.name
    for v in bm.verts:
        v.co.y *= -1
    bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(filepath=str(out/(obj.name+".fbx")), use_selection=True,
        object_types={"MESH"}, axis_forward="-Y", axis_up="Z", mesh_smooth_type="FACE",
        add_leaf_bones=False, bake_anim=False)
    bpy.data.objects.remove(obj, do_unlink=True)
