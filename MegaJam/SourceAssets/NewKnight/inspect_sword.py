import bpy
from mathutils import Vector
bpy.ops.import_scene.fbx(filepath=r'C:\Users\서가은\Downloads\Knight_Combat_Package\Knight_Combat\Knight_Sword.fbx')
for o in bpy.data.objects:
    if o.type!='MESH': continue
    c=[o.matrix_world@Vector(v) for v in o.bound_box]
    print(o.name,tuple(o.location),tuple(o.scale),[(min(v[i] for v in c),max(v[i] for v in c)) for i in range(3)], [m.name for m in o.data.materials])
