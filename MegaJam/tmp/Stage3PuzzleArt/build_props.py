from pathlib import Path
import math

source = Path('SourceAssets/Stage4ShadowTheatre/build_theatre.py')
scope = {'__file__': str(source.resolve())}
exec(compile(source.read_text(encoding='utf-8-sig').split('# Courses are staggered')[0], str(source), 'exec'), scope)
globals().update({k:v for k,v in scope.items() if not k.startswith('__')})

def fastener(x,y,z,rad=2):
    rod((x,y,z),(x,y+2,z),rad,'08',10)

def reel(x,y,z,r=38):
    # Camera-facing two-flange film reel, raised hub and six spokes.
    rod((x,y-5,z),(x,y+5,z),r,'09',32)
    ring(x,y+7,z,r-2,3,'06',True,36)
    ring(x,y+8,z,r*.64,2,'07',True,32)
    for i in range(6):
        a=2*math.pi*i/6
        rod((x+math.cos(a)*10,y+9,z+math.sin(a)*10),
            (x+math.cos(a)*(r-5),y+9,z+math.sin(a)*(r-5)),3,'06',10)
    rod((x,y+7,z),(x,y+13,z),9,'07',20)
    rod((x,y+13,z),(x,y+15,z),4,'08',16)

# Movie camera and wooden tripod, approx. 2.4 m tall.
for foot in [(-58,20,3),(58,20,3),(0,-56,3)]:
    rod((0,0,112),foot,3.6,'07',12,2.7)
    rod((foot[0]-8,foot[1],3),(foot[0]+8,foot[1],3),3,'09',10)
ring(0,0,98,29,2,'06',False,28)
rod((0,0,92),(0,0,130),7,'09',16)
box(0,0,145,108,58,68,'09',3)
box(0,32,145,103,5,63,'07',1.5)
box(0,35,145,92,3,52,'11',1)
for x in [-48,48]:
    for z in [116,174]: fastener(x,36,z)
rod((53,0,145),(92,0,145),22,'09',24)
rod((86,0,145),(106,0,145),26,'07',24)
rod((106,0,145),(110,0,145),21,'08',24)
box(-32,39,145,37,6,33,'06',2)
rod((-32,43,145),(-32,49,145),13,'09',24)
rod((-32,49,145),(-32,51,145),9,'15',24)
for x in [-31,31]:
    rod((x,0,179),(x,0,189),5,'07',12)
    reel(x,2,212,31)
box(0,-8,179,105,26,6,'07',1)
finish('SM_Stage3_ArchiveCamera')

# Archive shelves: wood frame, film tins, reels, stacked canisters.
for x in [-91,91]:
    box(x,0,116,10,45,232,'11',2)
    box(x,24,116,7,5,220,'06',1)
for z in [8,62,116,170,226]:
    box(0,0,z,190,48,8,'10',1.5)
    box(0,25,z+1,185,3,3,'06',.5)
for z in [24,78,132]:
    for x in [-65,-18,29,67]:
        rod((x,-1,z),(x,-1,z+15),16,'09',24)
        rod((x,-1,z+15),(x,-1,z+18),17,'06',24)
        ring(x,0,z+11,16,1.3,'07',False,24)
for x in [-60,-4,52]: reel(x,4,198,21)
for x in [-91,91]:
    for z in [9,62,116,170,226]:fastener(x,28,z,2.1)
finish('SM_Stage3_FilmRack')

# Freestanding 3 lever film editing desk, shown from the 2.5D camera.
box(0,0,8,210,82,16,'11',3)
for x in [-92,92]:
    box(x,0,46,12,70,78,'10',2)
    box(x,37,46,5,3,75,'06',1)
box(0,0,83,210,84,18,'07',3)
box(0,0,96,204,78,12,'10',2)
box(0,40,67,182,3,35,'11',1)
for x in [-68,0,68]:
    box(x,0,104,54,62,4,'06',2)
    box(x,4,107,8,42,2,'09',1)
    rod((x,-7,107),(x,10,135),3,'07',10)
    rod((x,10,135),(x,10,143),6,'08',12)
    box(x,29,111,30,8,10,'09',1)
    box(x,34,112,23,3,6,'14',1)
    for dx in [-22,22]:fastener(x+dx,34,104,1.5)
for x in [-92,92]:
    for z in [16,76]:fastener(x,44,z)
finish('SM_Stage3_EditConsole')

# Stage spotlight on stand.
for foot in [(-38,18,2),(38,18,2),(0,-36,2)]:
    rod((0,0,67),foot,2.4,'09',9)
rod((0,0,55),(0,0,166),3.7,'09',12)
ring(0,0,112,8,2,'06',False,20)
box(0,0,169,66,46,50,'09',4)
box(0,25,169,57,4,43,'07',2)
rod((0,28,169),(0,38,169),17,'06',24)
rod((0,38,169),(0,41,169),13,'14',24)
for x in [-27,27]:
    for z in [149,189]:fastener(x,28,z)
box(0,0,198,68,52,5,'09',1)
finish('SM_Stage3_StageSpotlight')

# A small grouped set of archive film cans and upright reels.
for x,y,z,r in [(-35,0,0,25),(-35,0,13,25),(-35,0,26,25),(20,-8,0,29),(20,-8,13,29)]:
    rod((x,y,z),(x,y,z+10),r,'09',28)
    rod((x,y,z+10),(x,y,z+12),r+1,'06',28)
    ring(x,y,z+8,r,1.5,'07',False,28)
reel(50,4,40,26)
finish('SM_Stage3_FilmCanStack')
print('STAGE3_PUZZLE_PROPS_COMPLETE', len(EXPORTS))
