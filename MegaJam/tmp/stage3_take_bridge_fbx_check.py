import bpy, pathlib, json
from mathutils import Vector
root = pathlib.Path('SourceAssets/Stage3TakeBridge/Exports')
manifest = json.loads((root / 'mesh_manifest.json').read_text())
for name, info in manifest.items():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(root / (name + '.fbx')))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    assert len(meshes) == 1, name
    mesh = meshes[0]
    bounds = [mesh.matrix_world @ Vector(corner) for corner in mesh.bound_box]
    dimensions = [round((max(v[i] for v in bounds) - min(v[i] for v in bounds)) * 100, 1) for i in range(3)]
    expected = [round(hi - lo, 1) for lo, hi in zip(*info['bounds_cm'])]
    assert all(abs(a-b) < .3 for a,b in zip(dimensions,expected)), (name, dimensions, expected)
    assert [m.name.split('.')[0] for m in mesh.data.materials] == info['material_slots'], name
    print('VERIFIED', name, dimensions, 'slots', len(mesh.data.materials))
