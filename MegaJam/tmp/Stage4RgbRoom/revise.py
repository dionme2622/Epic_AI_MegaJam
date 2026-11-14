"""Author the Stage4 lighting booth using the existing theatre's mesh tools."""
from pathlib import Path
scene_tool = Path.cwd()/"SourceAssets/Stage4ShadowTheatre/build_theatre.py"
source = scene_tool.read_text(encoding="utf-8-sig")
namespace = {"__file__": str(scene_tool)}
exec(compile(source.split("# Courses are staggered")[0],str(scene_tool),"exec"),namespace)
exec(compile(source[source.index("def drape("):source.index("\ndrape(-478")],str(scene_tool),"exec"),namespace)
globals().update({k:v for k,v in namespace.items() if not k.startswith("__")})
random.seed(148)
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
