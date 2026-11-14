"""Stage 2 backstage workshop geometry, authored in centimetres."""
from pathlib import Path
scene_tool=Path.cwd()/"SourceAssets/Stage4ShadowTheatre/build_theatre.py"
source=scene_tool.read_text(encoding="utf-8-sig")
ns={"__file__":str(scene_tool)}
exec(compile(source.split("# Courses are staggered")[0],str(scene_tool),"exec"),ns)
exec(compile(source[source.index("def drape("):source.index("\ndrape(-478")],str(scene_tool),"exec"),ns)
globals().update({k:v for k,v in ns.items() if not k.startswith("__")})
random.seed(2611)
for code,name,c in [("21","WorkshopTeal",(.014,.13,.17)),("22","WorkshopDeep",(.009,.045,.065)),
                     ("23","WorkshopWire",(.17,.69,.73)),("24","WorkshopCanvas",(.52,.35,.23))]:
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);materials[code]=m

def beam(a,b,width,depth,mat="10"):
 a=Vector(a);b=Vector(b);center=(a+b)*.5;delta=b-a
 obj=box(*center,delta.length,depth,width,mat,2)
 obj.rotation_euler.y=-math.atan2(delta.z,delta.x)
 return obj

def window(x,z=360,w=170,h=430):
 box(x,-385,z,w+26,25,h+25,"02",3)
 box(x,-368,z,w,15,h,"21",2)
 for xx in [x-w*.5,x,x+w*.5]:
  box(xx,-356,z,8,7,h,"09",1)
 for zz in [z-h*.26,z,z+h*.26]:
  box(x,-355,zz,w,8,8,"09",1)
 arch(x,-364,z+h*.5,w*.5,13,20,9)

def truss(x,h=550,wide=360):
 for xx in [x-wide*.5,x+wide*.5]:
  box(xx,-220,h*.5+5,22,45,h,"10",3)
  for zz in [65,285,h-25]:
   box(xx,-192,zz,31,11,18,"07",2)
 for zz in [22,245,h-18]:
  box(x,-218,zz,wide+45,42,21,"10",3)
 beam((x-wide*.45,-210,37),(x+wide*.45,-210,h-38),13,23,"11")
 beam((x+wide*.45,-204,37),(x-wide*.45,-204,h-38),12,20,"10")

def lamp(x,z=300,y=-170):
 box(x,y-18,z,30,30,24,"07",3)
 rod((x,y,z-17),(x,y,z+19),13,"14",16)
 for zz in [z-19,z+21]:ring(x,y,zz,15,2.6,"06",False,24)
 for i in range(6):
  a=math.tau*i/6
  xx=x+math.cos(a)*15; yy=y+math.sin(a)*15
  rod((xx,yy,z-18),(xx,yy,z+21),1.8,"09",7)
 rod((x,y,z+20),(x,y,z+37),16,"07",15,4)
 rod((x,y,z-28),(x,y,z-19),3,"07",10,14)

def crate(x,z=40,size=70,y=-187):
 box(x,y,z,size,55,size,"10",2.5)
 for xx in [x-size*.4,x+size*.4]:box(xx,y+29,z,6,5,size,"11",1)
 for zz in [z-size*.4,z+size*.4]:box(x,y+30,zz,size,5,7,"07",1)
 beam((x-size*.36,y+33,z-size*.33),(x+size*.36,y+33,z+size*.33),5,6,"07")

def stool(x,y=-180):
 for xx in [x-28,x+28]:
  for yy in [y-19,y+19]:rod((xx,yy,0),(xx,yy,72),4,"10",8)
 box(x,y,77,99,54,10,"10",2)
 box(x,y+28,78,103,7,11,"07",1)

def panel(x,y,z,w,h):
 box(x,y-6,z,w+16,19,h+16,"10",3)
 box(x,y+5,z,w,5,h,"22",1)
 for xx in [x-w*.5,x+w*.5]:box(xx,y+9,z,6,6,h,"06",1)
 for zz in [z-h*.5,z+h*.5]:box(x,y+9,zz,w,6,6,"06",1)

def wire(x,z,r,y=-160,n=10):
 for i in range(n):
  a=math.tau*i/n;b=math.tau*(i+1)/n
  rod((x+r*math.cos(a),y,z+r*math.sin(a)),(x+r*math.cos(b),y,z+r*math.sin(b)),1.6,"23",7)
  if i%2==0:
   rod((x,y,z),(x+r*math.cos(a),y,z+r*math.sin(a)),.8,"23",6)
 rod((x-r,y,z),(x+r,y,z),1.2,"23",7)

def gear(x,z,r=70,y=-192,teeth=10):
 ring(x,y,z,r*.75,9,"06",True,32)
 ring(x,y+7,z,r*.17,7,"08",True,20)
 for i in range(teeth):
  a=math.tau*i/teeth
  xx=x+math.cos(a)*r*.94;zz=z+math.sin(a)*r*.94
  ob=box(xx,y,zz,19,22,24,"06",2)
  ob.rotation_euler.y=-a
 for i in range(5):
  a=math.tau*i/5
  rod((x+math.cos(a)*r*.17,y,z+math.sin(a)*r*.17),
      (x+math.cos(a)*r*.72,y,z+math.sin(a)*r*.72),5,"07",10)

def stage_floor(x0,x1):
 # Front fascia stays below the walkable surface and never touches the player.
 for x in range(x0,x1,100):
  w=min(98,x1-x)
  if w<10:continue
  box(x+w/2,151,-61,w,20,56,random.choice(STONE),2.8)
  box(x+w/2,158,-29,w+2,7,8,"07",1)
  if x%300<100:rod((x+w/2,163,-30),(x+w/2,166,-30),2.3,"08",8)

# Deep painted scenery and exposed rigging across the entire playable length.
for idx,(lo,hi) in enumerate([(-1250,1900),(1900,4750),(4750,7700),(7700,10400)]):
 box((lo+hi)*.5,-465,320,hi-lo,36,1350,"22")
 for x in range(lo+200,hi,575):
  box(x,-423,280,22,22,1000,"09",2)
  beam((x,-416,-90),(x+430,-416,800),14,14,"09")
  beam((x+430,-414,-90),(x,-414,800),13,13,"09")
 for x in range(lo+420,hi,980):
  window(x,350,155,430)
 for z in [510,552,750]:
  box((lo+hi)*.5,-245,z,hi-lo,40,24,"10",3)
 stage_floor(lo,hi)
 finish(f"SM_Workshop_Background_{idx+1:02}")

# Entrance and moving wheel stage. No wheel is duplicated or obscured.
column(70,-230,0,350,72,48);column(820,-230,0,350,72,48)
arch(445,-235,350,376,43,50,20)
for x in [70,820]:
 lamp(x,255,-166)
truss(-610,525,340)
stool(-440)
panel(-440,-215,220,225,150)
wire(-490,225,39,-200);wire(-396,225,43,-200,7)
crate(-742,43,82);crate(-654,30,54)
# Brass outlined low/high samples sit on the bench.
for x,poly in [(-465,8),(-398,18)]:
 ring(x,-151,139,26,4,"06",True,poly)
 rod((x,-153,139),(x,-145,139),19,"04",poly)
 rod((x,-143,139),(x,-138,139),6,"08",12)
drape(-1080,-668,431,560,-202,True);drape(-1102,-1050,55,560,-210)
drape(862,1215,438,555,-210,True)
for x in [1120,1312]:
 column(x,-242,2,266,42,26)
arch(1216,-244,265,100,22,27,12)
box(1215,-246,244,215,14,10,"07",2)
for x in [1112,1320]:lamp(x,215,-191)
finish("SM_Workshop_WheelHall")

# Production floor in between puzzles, with distinct construction stations.
for x in [2340,3650,4970,6450,7480]:
 truss(x,540,310)
for x in [2700,4130,5920,7120]:
 lamp(x,300,-190)
for x in [2750,4050,6000]:
 stool(x)
 for dx in [-32,0,32]:
  rod((x+dx,-174,90),(x+dx,-174,114),5,"18",9)
for x in [2480,2518,4570,4640,6760,6825]:
 crate(x,25,48)
for x in [3200,5240,7090]:
 panel(x,-216,243,245,183)
 wire(x-42,265,55,-201,11);wire(x+64,234,38,-201,7)
for x in [3020,5580,7060]:
 ring(x,-186,133,55,7,"07",True,16)
 for i in range(8):
  a=i*math.tau/8
  rod((x,-180,133),(x+math.cos(a)*48,-180,133+math.sin(a)*48),3,"09",8)
for start,end in [(2050,2570),(3760,4290),(5130,5650),(6720,7160)]:
 drape(start,end,422,552,-201,True)
finish("SM_Workshop_Production")

# Lift counterweight and gateway scenery, clear of all moving collisions.
for x in [7960,8490,9000,10160]:
 truss(x,575,180)
for x in [8510,8900]:
 box(x,-200,301,33,45,594,"10",4)
 box(x,-171,301,13,10,584,"07",1.5)
 for z in range(54,560,46):box(x,-164,z,22,12,15,"06",1)
for x in [8630,8805]:
 rod((x,-215,35),(x,-215,546),3.4,"07",9)
 rod((x,-204,35),(x,-204,546),1.8,"08",8)
for x,z,r in [(8080,348,56),(8290,363,48),(8364,447,31),(8575,494,33),(8750,494,33)]:
 gear(x,z,r)
box(8690,-220,553,650,42,25,"10",3)
for x in [8170,8960,9440,10050]:lamp(x,295,-174)
for x in [9050,9670]:
 column(x,-238,285,530,65,45)
arch(9360,-241,525,308,35,44,17)
# Framed set door and film emblem.
box(9645,-239,486,250,47,270,"03",4)
arch(9645,-218,620,100,24,32,13)
box(9645,-207,488,193,17,245,"10",3)
for x in [9588,9645,9702]:box(x,-193,488,5,7,236,"07",1)
for x in [9603,9687]:
 ring(x,-181,488,23,4,"06",True,20)
 rod((x,-181,488),(x,-173,488),5,"08",12)
for x in [9260,9930]:crate(x,30,58)
drape(9680,10200,442,574,-191,True)
finish("SM_Workshop_LiftHall")

# Light strips and workshop identification create a readable hierarchy.
for x in [-800,350,1300,2350,3950,5500,6900,8210,9070]:
 box(x,-222,590,220,21,18,"07",3)
 for dx in [-85,0,85]:
  rod((x+dx,-208,590),(x+dx,-203,590),3.3,"08",10)
finish("SM_Workshop_Trim")

for obj in EXPORTS:obj.hide_set(False)
bpy.ops.wm.save_as_mainfile(filepath=str(Path.cwd()/"SourceAssets/Stage2Workshop.blend"))
