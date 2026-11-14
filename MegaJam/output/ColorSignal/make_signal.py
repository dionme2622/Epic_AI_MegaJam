from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

size=256
channels=[Image.new('L',(size*4,size),0) for _ in range(3)]
targets=[[2,0,3,2],[1,3,0,1],[3,2,1,0]]
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',32)
for ch,img in enumerate(channels):
    for i,direction in enumerate(targets[ch]):
        arrow=Image.new('L',(size,size),0)
        d=ImageDraw.Draw(arrow)
        d.polygon([(45,113),(140,113),(140,80),(214,150),(140,220),(140,187),(45,187)],fill=210)
        arrow=arrow.rotate(direction*90,center=(130,150))
        img.paste(arrow,(i*size,0))
        d=ImageDraw.Draw(img)
        d.text((i*size+65,5),f'{i+1}: {"RGBR"[i]}',font=font,fill=230)
Image.merge('RGB',channels).save(Path(__file__).with_name('SignalAtlas.png'))
