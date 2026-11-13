import bpy
from pathlib import Path
from mathutils import Vector
scene=bpy.data.scenes['Stage1_Wheel_Puzzle']; bpy.context.window.scene=scene
out=Path(r'C:\LHH\Epic_AI_MegaJam\MegaJam\output\Stage1_Unreal_Export')
excluded=('SM_Second','PROP_Second','TXT_Second','MARK_Second')
door_prefix=('SM_GatePanel_MOVABLE','PROP_GateBrace_','PROP_DoorHandle')
collections=['02_RockPassage_Base','06_Backdrop_NoCollision','07_Props_NoCollision','12_Stage_Detail_NoCollision','14_Extended_Set_Dressing','20_GearLift_Scenery']
members=[o for n in collections for o in scene.collection.children[n].objects if o.type=='MESH' and not o.name.startswith(excluded)]
door=[o for o in members if o.name.startswith(door_prefix)]
backdrop=[o for o in members if o not in door]
def export(name,obs,pivot=None):
    if not obs: raise RuntimeError('Empty export '+name)
    bpy.ops.object.select_all(action='DESELECT')
    positions={o:o.location.copy() for o in obs}
    for o in obs:
        o.hide_viewport=False; o.hide_set(False); o.select_set(True)
        if pivot is not None: o.location-=pivot
    bpy.context.view_layer.objects.active=obs[0]
    bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False)
    for o,p in positions.items(): o.location=p
    print('EXPORT',name,len(obs))
export('Stage1_Backdrop_NoGate',backdrop)
export('Stage1_GateVisual',door,Vector((18.6,1.64,1.47)))
