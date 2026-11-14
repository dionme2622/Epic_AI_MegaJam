from pathlib import Path
tool=Path.cwd()/"SourceAssets/Stage4ShadowTheatre/build_theatre.py"
txt=tool.read_text(encoding="utf-8-sig")
ns={"__file__":str(tool)}
exec(compile(txt.split("# Courses are staggered")[0],str(tool),"exec"),ns)
globals().update({k:v for k,v in ns.items() if not k.startswith("__")})
random.seed(112)
for code,name,color in [("21","WorkshopFloorA",(.095,.065,.12)),("22","WorkshopFloorB",(.13,.095,.155)),("23","WorkshopFloorC",(.075,.055,.10))]:
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);materials[code]=m
for number,(start,end,level) in enumerate([(-1200,300,60),(300,980,None),(1450,8550,0),(8950,10200,260)],1):
 for x in range(start,end,110):
  w=min(110,end-x)
  if w<8:continue
  center=x+w*.5
  for row in range(4):
   y=-105+row*70
   top=(84-.08*center) if level is None else level
   # The top sits above the existing walkable surface. It has no collision.
   box(center,y,top+.26,w-1.4,68,.5,random.choice(["21","21","22","23"]),0,tilt=math.degrees(math.atan(.08)) if level is None else 0)
 finish("SM_Workshop_StoneFloor_%02d"%number)

