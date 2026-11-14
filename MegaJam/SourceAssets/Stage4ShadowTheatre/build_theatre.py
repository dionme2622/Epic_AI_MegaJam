"""Build the authored, centimetre-scale Stage 4 theatre meshes in Blender."""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
OUT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
random.seed(79415)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

PALETTE = {
    "M01_Bedrock": (.038, .025, .050, .91, 0),
    "M02_Basalt": (.088, .056, .105, .83, 0),
    "M03_Slate": (.118, .073, .147, .83, 0),
    "M04_Porphyry": (.151, .095, .167, .82, 0),
    "M05_Capstone": (.223, .153, .238, .76, 0),
    "M06_Gold": (.56, .288, .071, .35, .68),
    "M07_Tarnish": (.242, .120, .035, .48, .72),
    "M08_Highlight": (.95, .564, .156, .30, .63),
    "M09_Iron": (.079, .071, .092, .43, .80),
    "M10_Plank": (.252, .118, .053, .61, .03),
    "M11_Endgrain": (.119, .048, .022, .77, .02),
    "M12_Velvet": (.205, .018, .038, .89, 0),
    "M13_Seams": (.078, .007, .020, .87, 0),
    "M14_Lamp": (.975, .493, .126, .30, .1),
    "M15_Glass": (.66, .81, .91, .12, 0),
    "M16_Reflect": (.74, .66, .44, .25, .2),
    "M17_Leather": (.129, .057, .035, .69, 0),
    "M18_Steel": (.29, .33, .41, .34, .8),
    "M19_Pit": (.015, .010, .021, .98, 0),
}
materials = {}
for name, (r,g,b,roughness,metallic) in PALETTE.items():
    m = bpy.data.materials.new(name)
    m.diffuse_color = (r,g,b,1)
    m.use_nodes = True
    p = next((node for node in m.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if not p:
        p = m.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        surface = m.node_tree.nodes.new("ShaderNodeOutputMaterial")
        m.node_tree.links.new(p.outputs[0], surface.inputs["Surface"])
    p.inputs["Base Color"].default_value = (r,g,b,1)
    p.inputs["Roughness"].default_value = roughness
    p.inputs["Metallic"].default_value = metallic
    materials[name[1:3]] = m

BATCH = []
EXPORTS = []
STONE = ["02", "03", "03", "04", "04", "05"]

def coord(x, y, z):
    return (x / 100, y / 100, z / 100)

def put(obj, material):
    obj.data.materials.append(materials[material])
    BATCH.append(obj)
    return obj

def box(x, y, z, w, d, h, material, bevel=0, tilt=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=coord(x,y,z))
    obj = bpy.context.object
    obj.dimensions = coord(w,d,h)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.rotation_euler.y = math.radians(tilt)
    if bevel:
        mod = obj.modifiers.new("Chipped edge", "BEVEL")
        mod.width = bevel / 100
        mod.segments = 1
        normal = obj.modifiers.new("Weighted corners", "WEIGHTED_NORMAL")
        normal.keep_sharp = True
    return put(obj, material)

def prism(points, y, d, material, bevel=0):
    coords = [coord(x, y + j*d*.5, z) for j in [-1, 1] for x,z in points]
    n = len(points)
    faces = [tuple(range(n)), tuple(reversed(range(n,n*2)))]
    faces.extend((i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n))
    return polygon_mesh(coords, faces, material, bevel)

def polygon_mesh(coords, faces, material, bevel=0, smooth=False):
    data = bpy.data.meshes.new("Theatre section")
    data.from_pydata(coords, [], faces)
    data.update()
    obj = bpy.data.objects.new("Theatre section", data)
    bpy.context.collection.objects.link(obj)
    if bevel:
        mod = obj.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel/100
        mod.segments = 1
    if smooth:
        for face in data.polygons:
            face.use_smooth = True
    return put(obj, material)

def rod(a, b, radius, mat, sides=12, other=None):
    v1, v2 = Vector(coord(*a)), Vector(coord(*b))
    delta = v2-v1
    bpy.ops.mesh.primitive_cone_add(vertices=sides, radius1=radius/100, radius2=(other or radius)/100,
                                  depth=delta.length, location=(v1+v2)*.5)
    obj = bpy.context.object
    obj.rotation_euler = delta.to_track_quat('Z','Y').to_euler()
    return put(obj, mat)

def ring(x, y, z, radius, tube, mat, vertical=True, steps=40):
    bpy.ops.mesh.primitive_torus_add(major_segments=steps, minor_segments=8,
                                   location=coord(x,y,z),major_radius=radius/100,minor_radius=tube/100)
    obj = bpy.context.object
    if vertical:
        obj.rotation_euler.x = math.pi/2
    return put(obj, mat)

def arch(x, y, z, radius, thick, depth, n=11):
    for i in range(n):
        a = i*math.pi/n+.022
        b = (i+1)*math.pi/n-.022
        points = [(x+ra*math.cos(t), z+ra*math.sin(t)) for ra,t in
                  [(radius,a),(radius+thick,a),(radius+thick,b),(radius,b)]]
        prism(points,y,depth,"05" if i==n//2 else random.choice(STONE),2.2)

def column(x, y, bottom, top, w, d):
    box(x,y,bottom+10,w+32,d+24,20,"04",3)
    box(x,y,bottom+30,w+14,d+14,16,"05",2)
    for i in range(max(1,round((top-bottom-50)/48))):
        count=max(1,round((top-bottom-50)/48))
        h=(top-bottom-50)/count
        box(x+random.uniform(-2,2),y,bottom+42+(i+.5)*h,w+random.uniform(-3,3),d,h-2,random.choice(STONE),2.5)
    box(x,y,top-2,w+25,d+20,19,"04",2)
    box(x,y,top+10,w+48,d+33,13,"05",2)

def finish(name):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in BATCH:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        for modifier in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        obj.select_set(False)
    for obj in BATCH:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = BATCH[0]
    if len(BATCH)>1:
        bpy.ops.object.join()
    obj = bpy.context.object
    bpy.context.scene.cursor.location = (0,0,0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.name=name
    obj.data.name=name
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    # FBX's axis conversion into Unreal mirrors Blender's depth axis.
    for vertex in obj.data.vertices:
        vertex.co.y *= -1
    for polygon in obj.data.polygons:
        polygon.flip()
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+".fbx")),use_selection=True,
                             object_types={"MESH"},axis_forward="-Y",axis_up="Z",
                             mesh_smooth_type="FACE", add_leaf_bones=False,bake_anim=False)
    for vertex in obj.data.vertices:
        vertex.co.y *= -1
    for polygon in obj.data.polygons:
        polygon.flip()
    obj.hide_set(True)
    EXPORTS.append(obj)
    BATCH.clear()

# Courses are staggered and individually bevelled. These bricks receive the
# working lights and projected silhouettes directly in the engine.
for xlo, xhi, name in [(-515, 1090, "SM_Vault_WestWall"),(1090, 2360, "SM_Vault_CenterWall"),(2360, 3370, "SM_Vault_EastWall")]:
    box((xlo+xhi)*.5, -313, 97, xhi-xlo, 52, 1570,"01")
    for row in range(24):
        z = -600 + row * 55
        x=xlo
        first=True
        while x<xhi-1:
            w=min(xhi-x, (53 if row%2 else 111) if first else random.uniform(104,140))
            if w>7:
                colors = ["02", "03", "03", "04"] if z > -160 else ["01", "02", "02", "03"]
                box(x+w*.5,-284+random.uniform(-1,1),z,w-2.6,10,52,
                    random.choice(colors),2.5)
            first=False
            x+=w
    finish(name)

# Plaster ribs, arches and proscenium frame, behind the traversable ledges.
for x in [-290, 365, 1160, 1548, 2355, 2584, 3228]:
    column(x,-260, -480 if x in [365,1160,1548,2355] else -58, 430,78,29)
    box(x,-252,655,83,46,231,"03",4)
    for z in [-157, 149, 367, 560]:
        box(x,-252,z,95,44,20,"04",3)
for x,r in [(38,266),(755,342),(1354,150),(1951,353),(2469,76),(2900,282)]:
    arch(x,-263,418,r,25,22,12)
for z,h in [(573,18),(606,45),(646,20),(740,26),(-455,16),(-490,45)]:
    for i in range(21):
        x=-495+i*189
        box(x,-230,z,186,53,h,random.choice(STONE),3)
finish("SM_Vault_Architecture")

PLATFORMS = [
    (-475,350,0), (440,580,0), (680,820,22), (915,1080,37), (1190,1534,0),
    (1644,1799,35), (1900,2188,18), (2294,2455,0), (2560,3330,0),
]
for a,b,z in PLATFORMS:
    w=b-a
    x=(a+b)*.5
    box(x,0,z-16,w,184,32,"04",3)
    box(x,0,z-35,w-12,172,27,"02",5)
    for i in range(max(2,math.ceil(w/80))):
        n=max(2,math.ceil(w/80))
        brick=w/n
        box(a+(i+.5)*brick,93,z-22,brick-2.8,15,32,random.choice(STONE),3)
    box(x,92,z-4,w+4,15,12,"07",2)
    box(x,98,z-.7,w+6,5,5,"08",1)
    box(x,-88,z-1.8,w,12,7,"06",1)
    box(a+5,0,z-3,10,166,7,"07",1)
    box(b-5,0,z-3,10,166,7,"07",1)
    for i in range(max(2,int(w/46))):
        n=max(2,int(w/46))
        xx=a+(i+.5)*w/n
        rod((xx,100,z-4),(xx,104,z-4),2.3,"09",8)
    if w < 350:
        prism([(a+10,z-37),(b-10,z-37),(b-32,z-78),(x+w*.18,z-90),
               (x-w*.18,z-91),(a+31,z-75)],35,94,"03",4)
        box(x,89,z-55,w*.57,10,12,"04",2)
    else:
        for post in ([a+88,b-84] if w>550 else [x]):
            box(post,28,z-280,90,127,330,"02",5)
            box(post,91,z-126,104,8,21,"04",2)
            box(post,91,z-235,99,8,21,"03",2)
            prism([(post-73,z-44),(post+73,z-44),(post+40,z-94),(post-40,z-94)],44,129,"04",3)
        for ix in range(3 if w>550 else 1):
            arch(a+w*(ix+1)/(4 if w>550 else 2),69,z-166,76,18,39,8)
finish("SM_Vault_PlatformFaces")

# An iron fly rail with ratchets and attachment brackets.
for y in [-34,34]:
    box(1402,y,540,2588,20,17,"09",2)
    box(1402,y+8,544,2585,5,5,"06",1)
for x in range(145,2686,140):
    box(x,0,546,22,109,10,"09",2)
    for y in [-48,49]:
        rod((x,y,550),(x,y,556),3.4,"08",8)
for x in [360,720,1080,1450,1790,2130,2490]:
    box(x,0,574,37,126,37,"09",3)
    box(x,61,574,32,12,43,"07",2)
    for z in [561,588]:
        rod((x,67,z),(x,71,z),4,"08",10)
finish("SM_Vault_FlyRail")

# Actual dimensional silhouettes. Open archways and merlons shape the shadow.
def castle(name, base_z, width, height, rail_z):
    w=width*.5
    box(0,0,6,width+12,37,12,"07",2)
    box(0,20,5,width+14,7,6,"08",1)
    # Three towers cast one recognisable castle-shaped silhouette. The movable
    # bar is rendered from the same geometry that defines the hit envelope.
    for x, r, top in [(-w*.69,w*.31,height*.78),(0,w*.38,height),(w*.69,w*.31,height*.78)]:
        x1,x2=x-r,x+r
        box(x,0,top-19,2*r,29,38,"10",2)
        for j in range(3):
            bx=x1+(j+.5)*(2*r/3)
            box(bx,0,top+1,2*r/4.9,28,21,"10",2)
            box(bx,16,top+10,2*r/4.9,7,5,"06",1)
        portal = 20 if x==0 else 9
        key = 62 if x==0 else 44
        box((x1+x-portal)*.5,0,(top-11)*.5,x-portal-x1,28,top-11,"10",2)
        box((x2+x+portal)*.5,0,(top-11)*.5,x2-x-portal,28,top-11,"10",2)
        box(x,0,(top+key)*.5,2*portal,28,top-key,"10",2)
        arch(x,16,key-5,portal,6,12,9)
        for z in [20,60,105]:
            if z>=top-25:
                continue
            box(x1+7,16,z,5,3,30,"11",.5)
            box(x2-8,16,z,5,3,30,"11",.5)
        box(x,17,13,2*r,4,7,"11",1)
        for px in [x1+7,x2-8]:
            rod((px,20,17),(px,24,17),3,"06",10)
    for xx in [-w*.72,w*.72]:
        z0=height*.80
        z1=rail_z-base_z
        rod((xx,0,z0),(xx,0,z1),2.6,"07",10)
        for i in range(int((z1-z0)/16)):
            ring(xx,1,z0+8+i*16,5,1.3,"06",True,12)
        ring(xx,0,z0,8.5,3,"06",True,18)
        ring(xx,23,z1,17,4,"06")
        rod((xx,-13,z1),(xx,29,z1),13,"09",20)
        rod((xx,30,z1),(xx,35,z1),4.5,"08",14)
    box(0,0,rail_z-base_z-16,w*1.72,25,12,"09",2)
    finish(name)

castle("SM_Vault_WestFlyBar",119,162,141,540)
castle("SM_Vault_EastFlyBar",81,172,156,540)

# Curved curtain panels, swags, braided trim and pulley props.
def drape(x1,x2,bot,top,y,swag=False):
    cols,rows=64,14
    coords=[]
    for j in range(rows+1):
        v=j/rows
        for i in range(cols+1):
            u=i/cols
            x=x1+(x2-x1)*u
            bottom=bot+(54*abs(2*u-1)**2 if swag else 0)
            z=bottom+(top-bottom)*v
            depth=y+math.cos(2*math.pi*(u*(3 if swag else 8)+v*.31))*((1-v)*4+7)
            coords.append(coord(x,depth,z))
    faces=[]
    for j in range(rows):
        for i in range(cols):
            k=j*(cols+1)+i
            faces.append((k,k+1,k+cols+2,k+cols+1))
    obj=polygon_mesh(coords,faces,"12",smooth=True)
    obj.data.materials.append(materials["13"])
    for j,poly in enumerate(obj.data.polygons):
        if (j%cols)%8 in [1,2]:
            poly.material_index=1
    mod=obj.modifiers.new("Hem thickness","SOLIDIFY")
    mod.thickness=.028
    if swag:
        for j in range(61):
            u=j/60
            x=x1+(x2-x1)*u
            z=bot+54*abs(2*u-1)**2
            yy=y+math.cos(6*math.pi*u)*11+6
            rod((x,yy,z-9),(x,yy,z+3),1.7,"06",8)

drape(-478,303,336,568,-225,True)
drape(-481,-418,0,542,-221)
drape(2532,3319,0,589,-222)
drape(2529,2960,417,599,-185,True)
drape(2952,3332,417,599,-185,True)
for x in [2575,3285]:
    rod((x,-154,343),(x,-183,556),4,"07",12)
    rod((x,-155,337),(x,-155,363),7,"06",12,5)
    ring(x,-149,371,8,1.6,"08",True,16)
finish("SM_Vault_Drapery")

# Lantern cages, film shelves and reel perforations.
for x,y,z in [(-69,-142,229),(205,-165,241),(2741,-147,235),(3139,-154,255)]:
    box(x,y-15,z+2,25,32,16,"07",3)
    rod((x,y,z-14),(x,y,z+19),11,"14",14)
    for zz in [z-16,z+19]:
        ring(x,y,zz,13,2.6,"06",False,22)
    for i in range(6):
        angle=i*math.tau/6
        xx=x+math.cos(angle)*13
        yy=y+math.sin(angle)*13
        rod((xx,yy,z-15),(xx,yy,z+22),1.5,"09",6)
    rod((x,y,z+18),(x,y,z+31),14,"07",14,3)
    rod((x,y,z-24),(x,y,z-16),4,"07",12,13)
for x in [20,113,204]:
    box(x,-193,79,8,34,150,"11",2)
for z in [20,58,97,145]:
    box(115,-193,z,201,67,6,"10",1)
    box(115,-158,z,203,6,6,"06",1)
for x,y,z,r in [(61,-164,122,22),(120,-166,119,20),(169,-164,120,19),(78,-165,80,15),(132,-162,78,16)]:
    rod((x,y-14,z),(x,y+7,z),r-3,"09",28)
    ring(x,y+9,z,r,2.9,"07",True,28)
    ring(x,y+10,z,4,2,"06",True,16)
    for i in range(5):
        angle=i*math.tau/5
        dx,dz=math.cos(angle),math.sin(angle)
        rod((x+dx*4,y+7,z+dz*4),(x+dx*(r-2),y+9,z+dz*(r-2)),2.6,"07",8)
for x,y in [(268,-116),(289,-184)]:
    for dx,dy in [(-13,-10),(13,-10),(0,11)]:
        rod((x,y,74),(x+dx,y+dy,0),2.9,"09",10)
    rod((x,y+2,79),(x,y+18,85),16,"09",25)
    ring(x,y+19,85,15,2.7,"06",True,22)
    rod((x,y+17,85),(x,y+20,86),12,"14",21)
finish("SM_Vault_Props")

# Bell jar and pedestal. The main glass geometry stays transparent, with
# curved, offset highlights that keep the silhouette visible over the velvet.
for z,r1,r2,h,mat in [(15,142,142,30,"03"),(34,144,130,12,"05"),(58,123,123,39,"04"),(83,134,134,15,"07")]:
    rod((2885,-114,z-h*.5),(2885,-114,z+h*.5),r1,mat,32,r2)
for i in range(12):
    a=i*math.tau/12
    x=2885+125*math.cos(a)
    y=-114+125*math.sin(a)
    rod((x,y,43),(x,y,74),3.7,"05",8)
ring(2885,-114,89,128,3.0,"08",False)
for x in [3067,3111]:
    rod((x,14,18),(x,14,85),4,"07",10)
    rod((x-10,14,20),(x+10,14,20),4,"07",10)
    ring(x,14,83,13,2,"06")
box(3089,14,12,84,56,15,"09",3)
finish("SM_Vault_Pedestal")

def dome_profile():
    profile=[(0,125),(13,125),(125,125),(155,123),(173,119)]
    for j in range(1,21):
        angle=(math.pi/2)*(j/20)
        profile.append((173+114*math.sin(angle),max(.15,119*math.cos(angle))))
    return profile

def revolve(profile, mat, steps=80):
    coords=[]
    for z,r in profile:
        for j in range(steps):
            a=j*math.tau/steps
            coords.append(coord(r*math.cos(a),r*math.sin(a),z))
    faces=[]
    for k in range(len(profile)-1):
        for j in range(steps):
            n=(j+1)%steps
            faces.append((k*steps+j,k*steps+n,(k+1)*steps+n,(k+1)*steps+j))
    return polygon_mesh(coords,faces,mat,smooth=True)

revolve(dome_profile(),"15")
for z,r in [(5,126),(151,124)]:
    ring(0,0,z,r,2.5 if z==5 else 1.3,"16",False)
rod((0,0,279),(0,0,290),15,"07",18,10)
rod((0,0,286),(0,0,317),10,"06",18,2.0)
for sign in [-1,1]:
    points=[]
    for z,r in dome_profile()[4:20]:
        a=math.pi*(.31 if sign==1 else .72)
        points.append((r*math.cos(a),r*math.sin(a)+.9,z))
    for a,b in zip(points,points[1:]):
        rod(a,b,1.2,"16",7)
finish("SM_Vault_BellJar")

# Cue medallions sit in the projection, with a bright brass perimeter and
# a black centre that can read as a blacked-out lamp when the shadow crosses.
rod((0,-2,0),(0,4,0),23,"07",32)
ring(0,7,0,20,3,"08",True,40)
rod((0,4,0),(0,9,0),15,"06",32)
for x,z in [(0,11),(11,0),(0,-11),(-11,0)]:
    rod((x,9,z),(x,10,z),1.4,"09",8)
prism([(-5,0),(0,7),(5,0),(0,-7)],11,1.4,"09")
finish("SM_Vault_Cue")

# In work-light view the emissive strip identifies the true collision edge.
for i in [1,2,3,5,6,7]:
    a,b,z=PLATFORMS[i]
    box((a+b)*.5,104,z-1,b-a-13,4,3.3,"14",.4)
    for x in [a+16,b-16]:
        box(x,91,z+.7,11,18,1.8,"14",.3)
    if i==6:
        box(b-47,51,z+.7,68,6,1.5,"14",.2)
        box(b-44,68,z+.7,56,5,1.5,"14",.2)
    if i==3:
        finish("SM_Vault_WestWorkLines")
finish("SM_Vault_EastWorkLines")

# One greave is attached to each dragon shin in game. Shape remains narrow so
# it reads as the knight's practical costume over the existing run/jump rig.
revolve([(-15,4.2),(-13,6.6),(-10,7.1),(-2,8.0),(4,7.25),(9,6.5),(12,4.6)],"18",18)
for z,r in [(-12,6.8),(4,7.4),(10,6.0)]:
    ring(0,0,z,r,.62,"06",False,24)
prism([(-1.8,-9),(2.5,-11),(3.5,7),(0,12),(-2.2,3)],7,2.4,"07",.5)
finish("SM_Vault_KnightGreave")

# Show all export modules when the editable scene is opened.
for obj in EXPORTS:
    obj.hide_set(False)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/"Stage4ShadowTheatre.blend"))
