import bpy
from pathlib import Path
scene=bpy.data.scenes['Stage1_Wheel_Puzzle']
bpy.context.window.scene=scene
out=Path(r'C:\LHH\Epic_AI_MegaJam\MegaJam\output\Stage1_Unreal_Export')
out.mkdir(parents=True,exist_ok=True)
def objects(collection_names):
    found=[]
    excluded=('SM_Second','PROP_Second','TXT_Second','MARK_Second')
    for name in collection_names:
        c=scene.collection.children.get(name)
        if c:
            found.extend(o for o in c.objects if o.type=='MESH' and not o.name.startswith(excluded))
    return found
def export(name, members, pivot=None):
    if not members: raise RuntimeError('No meshes for '+name)
    bpy.ops.object.select_all(action='DESELECT')
    original={ob:ob.location.copy() for ob in members}
    for ob in members:
        ob.hide_viewport=False; ob.hide_set(False); ob.select_set(True)
        if pivot is not None:
            ob.location -= pivot
    bpy.context.view_layer.objects.active=members[0]
    bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False)
    for ob,loc in original.items(): ob.location=loc
    print('EXPORT',name,'meshes',len(members))
export('Stage1_Ground',objects(['01_Ground_Static','04_Ramp_and_Plate','11_Extended_Stage_Modules','13_Extended_Floors','19_GearLift_Ground']))
export('Stage1_Backdrop',objects(['02_RockPassage_Base','06_Backdrop_NoCollision','07_Props_NoCollision','12_Stage_Detail_NoCollision','14_Extended_Set_Dressing','20_GearLift_Scenery']))
from mathutils import Vector
for name,group,pivot in [('Wheel_High','03_Wheel_HIGH',(4.4,0,1.49)),('Wheel_Low','05_Wheel_LOW',(4.4,0,1.49)),('Gear_High','21_Gear_HIGH',(82,1.53,2)),('Gear_Low','22_Gear_LOW',(82,1.53,2))]: export(name,objects([group]),Vector(pivot))
export('LiftPlatform',objects(['23_GearLift_Moving']),Vector((87,0,.15)))
print('STAGE1_EXPORT_COMPLETE',str(out))
