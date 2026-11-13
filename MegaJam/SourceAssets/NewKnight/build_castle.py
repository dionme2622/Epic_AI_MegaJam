import bpy, math
from pathlib import Path

root=Path(r'D:\UnrealProject\Epic_AI_MegaJam\MegaJam\SourceAssets\NewKnight')
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
colors={'Stone_Blue':(.18,.23,.30,1),'Stone_Light':(.36,.39,.45,1),'Gold_Trim':(.78,.48,.13,1),'Burgundy_Banner':(.34,.045,.12,1),'Deep_Gate':(.075,.07,.11,1),'Stage_Stone':(.23,.25,.28,1)}
mats={}
for name,color in colors.items():
    m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True
    m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=color
    m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.8
    mats[name]=m

def cube(name,loc,scale,mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name
    o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mats[mat]);return o
def cyl(name,loc,radius,depth,mat,verts=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=radius,depth=depth,location=loc)
    o=bpy.context.object;o.name=name;o.data.materials.append(mats[mat]);return o
def cone(name,loc,r1,depth,mat):
    bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=r1,radius2=.05,depth=depth,location=loc)
    o=bpy.context.object;o.name=name;o.data.materials.append(mats[mat]);return o

# 20 m wide toy-fantasy castle with a low open arena in front.
cube('Arena_Floor',(0,0,-.25),(22,18,.5),'Stage_Stone')
for x in range(-10,11,2):
    cube('Arena_Edge',(x,-9,.22),(1.9,.45,.45),'Gold_Trim')
for x in (-8,8):
    for y in (5,):
        cyl('Round_Tower',(x,y,3.0),1.6,6,'Stone_Blue')
        cyl('Tower_Crown',(x,y,6.15),1.85,.45,'Gold_Trim')
        cone('Tower_Roof',(x,y,7.25),1.65,2.0,'Burgundy_Banner')
        for a in range(8):
            theta=2*math.pi*a/8
            cube('Crenellation',(x+1.38*math.cos(theta),y+1.38*math.sin(theta),6.6),(.55,.55,.7),'Stone_Light')
for x in (-4.3,4.3): cube('Back_Wall',(x,6,2.3),(5.2,1.1,4.6),'Stone_Blue')
cube('Gate_Arch',(0,6,4.1),(3.4,1.2,1.2),'Stone_Light')
cube('Dark_Gate',(0,6.15,1.75),(3.35,.25,3.45),'Deep_Gate')
for x in (-6,-4,-2,0,2,4,6): cube('Battlement',(x,6,5.1),(1.1,1.2,.9),'Stone_Light')
for x in (-5.5,5.5):
    cube('Hanging_Banner',(x,5.32,3.1),(.95,.12,2.1),'Burgundy_Banner')
    cube('Banner_Gold_Edge',(x,5.23,4.25),(1.1,.15,.18),'Gold_Trim')
for x in (-3,3):
    cyl('Torch_Pedestal',(x,2,.45),.4,.9,'Stone_Light')
    cone('Torch_Flame',(x,2,1.17),.32,.65,'Gold_Trim')

bpy.ops.object.select_all(action='SELECT')
bpy.context.view_layer.objects.active=bpy.context.selected_objects[0]
bpy.ops.object.join();bpy.context.object.name='SM_Prologue_Castle'
bpy.ops.export_scene.fbx(filepath=str(root/'SM_Prologue_Castle.fbx'),use_selection=True,
    object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'SM_Prologue_Castle.blend'))
