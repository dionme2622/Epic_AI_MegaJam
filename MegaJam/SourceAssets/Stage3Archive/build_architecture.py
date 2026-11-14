"""Modular archive theatre set dressing, in Unreal centimetres.

Run: blender -b -t 4 --python build_architecture.py -- OUTPUT_DIRECTORY
All assets are decorative and should be placed without collision.
"""
from pathlib import Path
import math
import random
import bpy

p = Path(__file__).resolve().parents[1] / 'Stage4ShadowTheatre' / 'build_theatre.py'
namespace = {'__file__': str(p)}
exec(compile(p.read_text(encoding='utf-8-sig').split('# Courses are staggered')[0], str(p), 'exec'), namespace)
globals().update({k:v for k,v in namespace.items() if not k.startswith('__')})
random.seed(32003)

def cloth(points, bottom, y=0, depth=3, folds=18):
    """Pleated velvet with a curved lower edge; bottom(t) is in cm."""
    left,right,top=points
    xs=[left+(right-left)*i/folds for i in range(folds+1)]
    # Alternating seams give the material convincing vertical folds from the game camera.
    for i in range(folds):
        x0,x1=xs[i],xs[i+1]
        z0,z1=bottom((x0-left)/(right-left)),bottom((x1-left)/(right-left))
        prism([(x0,z0),(x1,z1),(x1,top),(x0,top)],y+(1.5 if i%2==0 else -1),depth,'12' if i%3 else '13',.15)
        if i<folds-1:
            rod((x1,y+3,z1+2),(x1,y+3,top-3),.55,'13',6)
    for i in range(folds):
        x0,x1=xs[i],xs[i+1]
        z0,z1=bottom((x0-left)/(right-left)),bottom((x1-left)/(right-left))
        rod((x0,y+4,z0),(x1,y+4,z1),2.2,'08',8)
        rod((x0,y+4,z0-3),(x0,y+4,z0-12),.9,'06',6)

# Large reusable side drape and curved valance.  Each module spans 940 cm.
box(0,-2,689,960,12,15,'07',2)
cloth((-460,460,682),lambda t:620-75*math.sin(math.pi*t),0,4,32)
for side in (-1,1):
    x=side*410
    prism([(x-58,682),(x+58,682),(x+side*30,360),(x+side*55,80),(x-side*16,120),(x-side*35,360)],5,8,'12',1)
    for j in range(7):
        xx=x-45+j*15
        rod((xx,11,670),(xx+side*7,11,136),1.1,'13',7)
    rod((x-58,13,268),(x+58,13,278),5,'06',12)
    rod((x-58,15,262),(x+58,15,272),1.5,'08',8)
    for k in range(5):
        rod((x+side*(12+k*6),12,266),(x+side*(17+k*6),12,225),1.2,'08',6)
    box(x+side*35,13,220,12,9,28,'06',2)
finish('SM_Stage3_TheatreCurtains')

# Banner with raised camera motif and crossed tripod legs.
prism([(-60,0),(60,0),(60,175),(0,215),(-60,175)],0,5,'12',1)
for x in (-51,51): box(x,5,90,4,4,178,'06',1)
for a,b in [((-50,5,171),(0,5,205)),((0,5,205),(50,5,171))]:rod(a,b,2,'06',8)
for z in (15,23):box(0,5,z,102,4,3,'06',1)
box(0,9,107,56,7,35,'06',2)
ring(-18,10,139,12,3,'08',True,20)
ring(15,10,139,12,3,'08',True,20)
prism([(29,114),(48,125),(48,96),(29,101)],10,7,'08',1)
rod((0,8,90),(-27,8,48),2.5,'06',8)
rod((0,8,90),(27,8,48),2.5,'06',8)
rod((0,8,90),(0,8,45),2.5,'06',8)
finish('SM_Stage3_CameraBanner')

# Gothic windows: inset is opaque dusky glass for clean silhouettes.
prism([(-116,0),(116,0),(116,280),(106,325),(78,365),(0,405),(-78,365),(-106,325),(-116,280)],0,10,'19',2)
prism([(-100,13),(100,13),(100,278),(89,316),(65,349),(0,382),(-65,349),(-89,316),(-100,278)],7,5,'03',0)
for x in (-112,112):
    box(x,13,148,18,16,296,'05',2)
    box(x,20,12,30,22,24,'04',2)
for i in range(10):
    a=math.pi*i/10; b=math.pi*(i+1)/10
    # Gothic peak is built from two opposing curved ribs.
    t0=i/10;t1=(i+1)/10
    for side in (-1,1):
        ax=side*(112-112*t0);bx=side*(112-112*t1)
        az=280+125*math.sin(t0*math.pi/2);bz=280+125*math.sin(t1*math.pi/2)
        rod((ax,16,az),(bx,16,bz),8,'05',8)
for x in (-70,0,70): rod((x,18,24),(x,18,300 if x else 371),3,'07',8)
for z in (100,190,278):rod((-100,18,z),(100,18,z),3,'07',8)
for x in (-70,70):
    for z in (145,235):
        rod((x-24,20,z),(x,20,z+28),1.5,'06',6)
        rod((x,20,z+28),(x+24,20,z),1.5,'06',6)
        rod((x+24,20,z),(x,20,z-28),1.5,'06',6)
        rod((x,20,z-28),(x-24,20,z),1.5,'06',6)
finish('SM_Stage3_GothicWindow')

# Exposed steel lighting truss and spotlights.
for z in (0,35):
    rod((-580,0,z),(580,0,z),5,'09',10)
for x in range(-560,561,80):
    rod((x,0,0),(x,0,35),3,'09',8)
    if x<560:rod((x,0,0),(x+80,0,35),2.2,'07',8)
for x in (-390,0,390):
    rod((x,0,0),(x,0,-60),3,'09',8)
    box(x,1,-64,35,20,12,'09',2)
    rod((x,-4,-78),(x,25,-125),16,'09',16,other=23)
    ring(x,27,-125,21,3,'07',True,20)
    box(x,29,-125,25,2,20,'14',1)
finish('SM_Stage3_StudioTruss')

# Repeated masonry proscenium arch (opening remains clear of moving actors).
for x in (-460,460):
    column(x,0,0,500,56,36)
arch(0,0,500,460,34,34,19)
for x in (-460,460):
    box(x,22,28,105,16,20,'06',2)
    box(x,22,468,91,16,12,'07',1)
finish('SM_Stage3_StoneProscenium')

print('STAGE3 ARCHITECTURE COMPLETE', [obj.name for obj in EXPORTS])
