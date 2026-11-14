"""Author the Stage4 lighting booth using the existing theatre's mesh tools."""
from pathlib import Path
scene_tool = Path.cwd()/"SourceAssets/Stage4ShadowTheatre/build_theatre.py"
source = scene_tool.read_text(encoding="utf-8-sig")
namespace = {"__file__": str(scene_tool)}
exec(compile(source.split("# Courses are staggered")[0],str(scene_tool),"exec"),namespace)
exec(compile(source[source.index("def drape("):source.index("\ndrape(-478")],str(scene_tool),"exec"),namespace)
globals().update({k:v for k,v in namespace.items() if not k.startswith("__")})
random.seed(148)
# Ceiling and twin alcoves. Brick courses continue into the adjacent stage.
box(385,-316,308,1860,65,876,"01")
for row in range(12):
    z=-110+row*62
    x=-545
    first=True
    while x<1310:
        width=min(1310-x,(64 if row%2 else 135) if first else random.uniform(96,145))
        if width>9:
            box(x+width*.5,-280+random.uniform(-1.4,1.4),z,width-2.9,16,58,
                random.choice(["02","03","03","04","04","05"]),2.6)
        x+=width
        first=False
for x in [-490,-251,246,760,1101,1248]:
    column(x,-251,-15,436,57,47)
for x,r in [(0,203),(503,208),(923,124)]:
    arch(x,-254,408,r,31,35,15)
for x in range(-530,1320,122):
    for z,h in [(483,22),(518,46),(554,18),(-62,25)]:
        box(x,-237,z,119,63,h,random.choice(STONE),2.7)
for x in range(-496,1280,125):
    box(x,-220,568,16,30,17,"07",1)
    rod((x,-203,568),(x,-200,568),3.0,"06",8)
finish("SM_RGB_StoneGallery")

# The gallery floor has stone tile seams and a continuous brass edge. The 
# original traversal surface will supply the unchanged collision.
box(450,0,-37,1800,280,69,"02",4)
for row in range(5):
    yy=-116+row*57
    first=-450+(-23 if row%2 else 0)
    for x in range(first,1350,95):
        right=min(x+95,1350)
        left=max(-450,x)
        if right-left>7:
            box((left+right)*.5,yy,-4,right-left-2.2,54,8,random.choice(["03","04","04","05"]),1.2)
for x in range(-401,1350,90):
    if x+45>1350: break
    box(x,144,-18,88,14,26,random.choice(STONE),2.5)
    box(x,146,-3,90,16,9,"07",1)
    box(x,150,.0,90,4,3,"08",.5)
    rod((x,153,-5),(x,156,-5),2,"09",8)
for x in [-80,271,643,1027,1307]:
    arch(x,121,-151,104,22,50,10)
    box(x-115,117,-104,19,40,103,"03",2)
finish("SM_RGB_GalleryFloor")

# Proscenium drapes frame the console. A smaller swag marks the wing door.
drape(-238,236,318,447,-213,True)
drape(-236,-181,22,465,-215)
drape(181,235,22,465,-215)
drape(784,1071,313,436,-217,True)
drape(1004,1067,9,402,-217)
for x in [-211,213,1035]:
    rod((x-10,-193,173),(x+11,-190,178),3.8,"06",10)
    rod((x+11,-190,178),(x+14,-187,148),2.3,"07",9)
    ring(x+14,-187,147,4.5,1.8,"06",True,14)
finish("SM_RGB_Curtains")

# Practical lectern for the full-screen RGB console. Three colored lens
# housings are separate material slots for stable ordering on import.
for code,name,col in [("22","M22_RGB_Red",(.78,.045,.056)),("23","M23_RGB_Green",(.085,.58,.18)),
                      ("24","M24_RGB_Blue",(.055,.25,.85))]:
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*col,1)
    materials[code]=m
box(0,-135,11,217,125,22,"04",4)
box(0,-135,24,187,107,10,"07",2.5)
for x in [-69,69]:
    box(x,-135,62,33,73,73,"10",4)
    box(x,-97,63,21,9,69,"07",1.8)
box(0,-128,109,229,99,33,"10",4)
box(0,-77,113,239,11,37,"07",3.2)
box(0,-143,163,245,51,109,"10",5)
box(0,-115,165,233,15,98,"07",3.8)
box(0,-105,166,219,12,87,"13",2.4)
for x in [-72,0,72]:
    ring(x,-93,162,25,3.9,"06",True,32)
    rod((x,-103,162),(x,-81,162),17.8,"09",32)
    rod((x,-79,162),(x,-67,162),13.7,"07",30)
    rod((x,-65,162),(x,-62,162),9.5,["22","23","24"][(x+72)//72],24)
    for a in [math.pi*.24,math.pi*.5,math.pi*.77]:
        xx=x+math.cos(a)*18.5
        zz=162+math.sin(a)*18.5
        rod((xx,-87,zz),(xx,-84,zz),1.5,"08",9)
for x in [-109,109]:
    for z in [131,202]:
        rod((x,-96,z),(x,-93,z),3,"06",8)
box(0,-152,232,216,40,32,"07",3)
box(0,-130,232,204,6,22,"13",1.6)
finish("SM_RGB_LightConsole")

# Lamps, reel storage, and shipping props in the alcoves.
for x,z in [(-179,234),(174,234),(749,239),(1051,239)]:
    y=-208
    box(x,y-26,z+17,36,38,49,"09",3)
    rod((x,y,z-15),(x,y,z+18),11,"14",16)
    for zz in [z-16,z+19]:
        ring(x,y,zz,13.2,2.5,"06",False,22)
    for j in range(7):
        a=j*math.tau/7
        xx=x+math.cos(a)*13
        yy=y+math.sin(a)*13
        rod((xx,yy,z-15),(xx,yy,z+22),1.7,"09",7)
    rod((x,y,z+18),(x,y,z+32),15,"07",16,4)
    rod((x,y,z-27),(x,y,z-16),4,"07",12,12)
for start in [310,624]:
    for x in [start,start+113]:
        box(x,-230,80,7,47,148,"10",1.8)
    for z in [8,57,104,154]:
        box(start+56.5,-226,z,121,47,7,"10",1.2)
        box(start+56.5,-202,z,125,5,6,"07",1)
    for j,(xx,zz,r) in enumerate([(28,127,18),(68,126,17),(88,75,12),(45,77,16),(78,29,14)]):
        x=start+xx
        rod((x,-217,zz),(x,-205,zz),r*.94,"09",24)
        ring(x,-203,zz,r,2.4,"07",True,27)
        for a in range(5):
            phi=a*math.tau/5+j
            rod((x,-201,zz),(x+math.cos(phi)*r*.84,-199,zz+math.sin(phi)*r*.84),1.6,"06",7)
for x,y,w,h in [(-388,-147,73,58),(-321,-147,49,42),(850,-178,63,62),(918,-175,46,38)]:
    box(x,y,h*.5,w,52,h,"10",2.4)
    for xx in [x-w*.41,x+w*.41]:
        box(xx,y+26,h*.5,w*.14,5,h+1,"11",1)
    box(x,y+27,h*.50,w-4,6,8,"07",1.5,tilt=16)
finish("SM_RGB_WallProps")

# The locked passage uses the original moving collision box and this attached
# lattice. Its sill, track and frame sit outside the playable plane.
for side in [-1]:
    yy=side*79
    box(1150,yy,143,78,22,286,"03",3)
    box(1150,yy,26,91,30,41,"05",2.5)
    box(1150,yy,273,90,28,21,"05",2.5)
    box(1150,yy,152,45,8,277,"09",2)
box(1150,-30,299,106,127,23,"04",3.8)
box(1150,-25,313,99,118,8,"06",1.5)
box(1185,-117,328,69,46,69,"03",3)
finish("SM_RGB_GateFrame")
for y in range(-69,70,23):
    box(0,y,-10,18,7.5,248,"09",2)
    box(10,y,-7,3.4,8.5,243,"07",1)
    rod((0,y,112),(0,y,145),9,"06",10,2)
for z in [-117,-43,43,110]:
    box(0,0,z,25,145,13,"07",2.5)
    for y in [-63,-42,-21,0,21,42,63]:
        rod((12,y,z),(17,y,z),3.6,"06",10)
for z in [-108,-44,44,108]:
    box(11,67,z,24,18,23,"06",2)
for x in [-9,10]:
    ring(x,45,9,13,2.8,"06",True,22)
finish("SM_RGB_Gate")

