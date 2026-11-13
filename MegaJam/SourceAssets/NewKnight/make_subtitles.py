from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
root=Path(r'D:\UnrealProject\Epic_AI_MegaJam\MegaJam\SourceAssets\NewKnight\Subtitles');root.mkdir(exist_ok=True)
ko=ImageFont.truetype(r'C:\Windows\Fonts\malgun.ttf',49)
en=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',39)
lines=[
('01_Victory','용사가 마침내 용을 쓰러뜨렸다.','At last, the hero defeated the dragon.'),
('02_Dragon_Rises','용: “좋아. 쓰러지는 연기는 이 정도면 됐겠지.”','Dragon: “Good. That should be enough acting for the fall.”'),
('03_Missing','용: “…내 뒤쪽은 어디 갔지?”','Dragon: “…Where did the rest of me go?”'),
('04_Dev_Note','개발 메모: 최종 보스 하체 — 테스트 구역으로 이동.','DEV NOTE: Final boss lower body — moved to the test area.'),
('05_Dev_Note2','현재 카메라에 잡히지 않으므로 임시 제거.','Temporarily removed because it is outside the camera frame.'),
('06_Protest','용: “화면에 안 나온다고 다리를 떼어 가?”','Dragon: “You took my legs because they were off camera?”'),
('07_Crawl','용은 앞발로 몸을 끌며 테스트 구역으로 향한다.','The dragon drags itself toward the test area.'),
('08_Storage','하체 보관실','LOWER BODY STORAGE'),
]
for name,k,e in lines:
    im=Image.new('RGBA',(1920,190),(0,0,0,0));d=ImageDraw.Draw(im)
    d.rounded_rectangle((50,8,1870,182),radius=20,fill=(0,0,0,176))
    for text,font,y in ((k,ko,31),(e,en,100)):
        box=d.textbbox((0,0),text,font=font);w=box[2]-box[0]
        d.text(((1920-w)/2,y),text,font=font,fill=(255,255,255,255))
    im.save(root/(name+'.png'))
print('created',len(lines),'subtitles')
