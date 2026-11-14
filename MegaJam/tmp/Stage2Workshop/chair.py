from pathlib import Path
tool=Path.cwd()/"SourceAssets/Stage4ShadowTheatre/build_theatre.py"
txt=tool.read_text(encoding="utf-8-sig")
ns={"__file__":str(tool)}
exec(compile(txt.split("# Courses are staggered")[0],str(tool),"exec"),ns)
globals().update({k:v for k,v in ns.items() if not k.startswith("__")})
def rail(a,b,r=3,m="07"):
 rod(a,b,r,m,12)
# Local origin is the character capsule center. Seat and wheels follow the pawn.
for y in [-36,36]:
 ring(-12,y,-39,44,4.2,"09",True,40)
 ring(-12,y+3,-39,39,2.4,"06",True,36)
 for i in range(10):
  angle=i*math.tau/10
  rail((-12,y+4,-39),(-12+math.cos(angle)*37,y+4,-39+math.sin(angle)*37),1.3,"06")
 rod((-12,y-4,-39),(-12,y+8,-39),7,"07",16)
 rail((-25,y,-40),(-43,y,17),3.2)
 rail((-43,y,17),(8,y,16),3.2)
 rail((8,y,16),(18,y,-33),3.2)
 rail((18,y,-33),(-12,y,-39),3.2)
 rail((-43,y,17),(-48,y,60),3.2)
 rail((-48,y,60),(-62,y,65),3.2)
 rail((18,y,-33),(51,y,-68),3.4)
 rail((51,y,-68),(76,y,-68),3.4)
 ring(69,y,-73,13,3,"09",True,20)
 rod((69,y-4,-73),(69,y+5,-73),4,"06",10)
box(-16,0,6,57,69,12,"17",3)
box(-45,0,33,11,69,47,"17",3,tilt=-7)
box(-11,0,9,54,63,5,"12",2)
for y in [-37,37]:
 rail((-45,y,30),(11,y,30),3.2)
 rail((11,y,30),(14,y,14),3.2)
finish("SM_Workshop_DragonWheelchair")
