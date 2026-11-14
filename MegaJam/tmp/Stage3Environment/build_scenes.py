from pathlib import Path
p=Path("SourceAssets/Stage4ShadowTheatre/build_theatre.py")
src=p.read_text(encoding="utf-8-sig")
scope={"__file__":str(p.resolve())}
exec(compile(src.split("# Courses are staggered")[0],str(p),"exec"),scope)
globals().update({k:v for k,v in scope.items() if not k.startswith("__")})
for index in range(3):
 # Fine copper silhouette reliefs of the cart at three stages of the move.
 box(0,-3,0,204,14,116,"07",4)
 box(0,6,0,190,5,102,"13",2)
 for x in [-90,90]:
  box(x,10,0,4,4,102,"06",.5)
 for z in [-48,48]:
  box(0,10,z,182,4,4,"06",.5)
 # Cart platform, wheels and handle.
 box(-5,15,-18,105,6,8,"06",1)
 box(-10,15,-7,83,5,13,"11",1)
 for x in [-40,30]:
  ring(x,19,-35,12,3,"06",True,24)
  rod((x,12,-35),(x,21,-35),3,"08",12)
  for phi in [0,math.pi/2]:
   rod((x-math.cos(phi)*8,20,-35-math.sin(phi)*8),(x+math.cos(phi)*8,20,-35+math.sin(phi)*8),1.3,"08",8)
 rod((45,15,-15),(63,15,18),3,"06",10)
 rod((60,15,16),(70,15,16),3,"06",10)
 if index >= 1:
  box(-7,17,11,49,8,36,"10",2)
  for x in [-28,14]:box(x,22,11,4,2,34,"06",.5)
  for z in [-5,27]:box(-7,22,z,50,2,3,"07",.5)
  box(-7,22,11,4,2,6,"06",.5)
 if index == 0:
  for x in [-71,-58,-45]:
   box(x,15,23,5,4,3,"08",.5)
 elif index == 1:
  rod((-7,15,38),(-7,15,32),2.4,"08",9)
  rod((-7,15,32),(-13,15,37),2.4,"08",9)
  rod((-7,15,32),(-1,15,37),2.4,"08",9)
 else:
  rod((-76,15,13),(-61,15,13),2.5,"08",8)
  rod((-76,15,5),(-66,15,5),2.5,"08",8)
  rod((65,15,10),(80,15,10),2.2,"08",8)
  rod((80,15,10),(75,15,15),2.2,"08",8)
  rod((80,15,10),(75,15,5),2.2,"08",8)
 finish(f"SM_Stage3_FilmScene_{index+1:02}")
