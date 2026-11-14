from PIL import Image, ImageDraw
from pathlib import Path
from random import Random
import math

out=Path(__file__).parent/'DotMarkers';out.mkdir(exist_ok=True)
rng=Random(2411);N=768;center=N/2;radius=348
mask=Image.new('L',(N,N),0);draw=ImageDraw.Draw(mask)
draw.polygon([(center-72,center-220),(center+72,center-220),(center+72,center+18),
              (center+205,center+18),(center,center+224),(center-205,center+18),(center-72,center+18)],fill=255)
palette=[(191,75,42),(220,109,48),(232,141,61),(242,168,85),(210,100,64),(171,70,49),(230,152,104),(196,124,70)]
greens=[(91,138,65),(112,155,71),(125,163,77),(96,132,64),(145,169,83)]
mark_greens=[(36,94,38),(45,112,43),(50,126,42),(65,119,35),(39,106,45)]
neutral=Image.new('RGBA',(N,N),(0,0,0,0));safe=Image.new('RGBA',(N,N),(0,0,0,0))
d0=ImageDraw.Draw(neutral);d1=ImageDraw.Draw(safe)
for d in (d0,d1):
 d.ellipse((center-radius-7,center-radius-7,center+radius+7,center+radius+7),fill=(80,54,42,255))
 d.ellipse((center-radius,center-radius,center+radius,center+radius),fill=(246,223,186,255))
points=[];cells={};cellsize=25
for attempt in range(140000):
 if len(points)>=1950:break
 x=rng.uniform(center-radius,center+radius);y=rng.uniform(center-radius,center+radius)
 r=rng.choices([3.5,5,6.5,8,10,12],[8,12,15,13,8,3])[0]*rng.uniform(.85,1.1)
 if (x-center)**2+(y-center)**2>(radius-r-4)**2:continue
 cx=int(x//cellsize);cy=int(y//cellsize);valid=True
 for gx in range(cx-2,cx+3):
  for gy in range(cy-2,cy+3):
   for xx,yy,rr in cells.get((gx,gy),[]):
    if (x-xx)**2+(y-yy)**2<(r+rr+1.4)**2:valid=False;break
   if not valid:break
  if not valid:break
 if not valid:continue
 points.append((x,y,r));cells.setdefault((cx,cy),[]).append((x,y,r))
 green=rng.random()<.20
 normal=rng.choice(greens if green else palette)
 inmark=mask.getpixel((int(x),int(y)))>0
 selected=rng.choice(mark_greens) if inmark else normal
 bounds=(int(x-r),int(y-r),int(x+r),int(y+r))
 d0.ellipse(bounds,fill=(*normal,255));d1.ellipse(bounds,fill=(*selected,255))
neutral.save(out/'Dots_Neutral.png');safe.save(out/'Dots_Safe.png')
print('dots:',len(points))
