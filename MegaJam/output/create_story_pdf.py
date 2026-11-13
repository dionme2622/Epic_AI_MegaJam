from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image
from pathlib import Path
import sys

root=Path('output/pdf'); root.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('Malgun','C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MalgunBold','C:/Windows/Fonts/malgunbd.ttf'))
pic=Image.open(sys.argv[1]).convert('RGB'); w,h=pic.size
ims=[pic.crop(box) for box in [(0,0,w//2,h//2),(w//2,0,w,h//2),(0,h//2,w//2,h),(w//2,h//2,w,h)]]
out=root/'Director_Cut_Prologue_Stage1_Stage2_Plan.pdf'
W,H=595.28,841.89
c=canvas.Canvas(str(out),pagesize=(W,H))
ink='#21243A'; muted='#626777'; purple='#554578'; light='#F3F1F8'; gold='#D28C55'
def text(x,y,s,size=10,color=ink,bold=False):
 c.setFillColor(color); c.setFont('MalgunBold' if bold else 'Malgun',size); c.drawString(x,y,s)
def header(n,title,sub):
 c.setFillColor('#FBFAFD'); c.rect(0,0,W,H,fill=1,stroke=0)
 text(42,802,'DIRECTOR’S CUT  /  GAME DESIGN',9,purple,True); text(42,765,title,23,ink,True); text(42,741,sub,10,muted)
 c.setStrokeColor('#DEDCE8'); c.line(42,726,553,726)
 text(42,25,'CONCEPT PLAN  ·  2.5D PUZZLE ADVENTURE',8,muted); text(535,25,f'{n:02}',9,purple,True)
def art(i,x,y,ww,hh):
 c.drawImage(ImageReader(ims[i]),x,y,width=ww,height=hh,preserveAspectRatio=False,mask='auto')
def block(y,title,lines):
 text(42,y,title,13,purple,True)
 for k,line in enumerate(lines): text(42,y-23-k*17,line,10,ink)
def box(x,y,w,h,title,lines):
 c.setFillColor(light); c.roundRect(x,y,w,h,8,fill=1,stroke=0); text(x+14,y+h-23,title,11,purple,True)
 for k,line in enumerate(lines): text(x+14,y+h-44-k*16,line,9.2,ink)
def finish(): c.showPage()

header(1,'잘려 나간 용','프롤로그부터 Stage 2까지  |  게임 콘셉트 기획안')
art(0,42,385,511,320)
text(42,346,'화면 밖으로 잘린 주인공의 이야기',16,ink,True)
text(42,316,'하체가 제거된 드래곤이 촬영장 뒤편을 탐험하며',11)
text(42,296,'게임 설정을 바꿔 퍼즐을 풀고 자신의 몸을 찾아간다.',11)
box(42,132,511,126,'핵심 경험',['2.5D 횡스크롤 퍼즐  ·  촬영 세트장과 개발 흔적','Stage 1: 모델 품질의 차이로 장애물과 기계를 해결','Stage 2: 그림자와 후처리 연출을 바꿔 숨겨진 기록을 발견'])
text(42,94,'이미지는 분위기 전달을 위한 콘셉트 예시입니다.',9,muted)
finish()

header(2,'PROLOGUE','마지막 전투, 잘린 출연 분량')
art(0,42,451,511,250)
block(412,'01  용사의 퇴장',['용사가 최종 보스인 용을 쓰러뜨린다. 승리 음악이 흐르고 용사는 무대 밖으로 퇴장한다.','쓰러져 있던 용이 고개를 들며 중얼거린다. “쓰러지는 연기는 이 정도면 됐겠지.”'])
block(333,'02  화면 밖의 진실',['용이 일어나려 하지만 몸이 움직이지 않는다. 카메라가 옆으로 이동하자','화면 밖에 있던 하체가 통째로 빠져 있다는 사실이 드러난다.'])
box(42,150,511,122,'남겨진 개발 메모',['“최종 보스 하체 - 테스트 구역으로 이동.”','“현재 카메라에 잡히지 않으므로 임시 제거.”','용은 앞발로 몸을 끌며 ‘하체 보관실’ 안내판을 따라 무대 뒤로 향한다.'])
text(42,110,'용: “화면에 안 나온다고 다리를 떼어 가?”',12,purple,True)
finish()

header(3,'STAGE 1','품질이 바뀌는 테스트 구역')
art(1,42,455,511,245)
block(415,'배경과 목표',['판타지 성벽, 돌길, 무대 장치와 개발 소품이 뒤섞인 긴 테스트 구역.','용은 모델 품질 HIGH / LOW를 전환하며 돌바퀴와 승강기를 통과한다.'])
box(42,235,245,122,'돌바퀴 퍼즐',['HIGH: 돌바퀴가 움직인다.','LOW: 돌바퀴가 멈춘다.','목표 구간에서 멈추면 문이 열린다.'])
box(308,235,245,122,'톱니 승강기',['LOW: 톱니가 헛돌아 작동하지 않는다.','HIGH: 승강기에 탑승해 E로 작동한다.','위층에 도착하면 다음 구역으로 이동한다.'])
block(198,'플레이 흐름',['입구 → 돌바퀴 위치 맞추기 → 열린 문 통과 → 톱니 승강기 → 조명실 입구','현재 구현은 프로토타입이며 형태 차이를 보여 주는 연출은 추가 개선이 필요하다.'])
finish()

header(4,'STAGE 2','빛이 지워진 촬영장')
art(2,42,450,511,250)
block(410,'핵심 아이디어',['그림자와 블룸, 노출을 바꾸어 같은 장면에서 서로 다른 정보를 발견한다.','감독이 보기 좋게 편집한 화면을 되돌려 감춰진 촬영 기록을 복원한다.'])
box(42,222,511,132,'일자형 맵의 진행 순서',['조명실 입구 → ① 그림자 연습실 → ② 블룸 과다 구역','→ ③ 감독의 편집실 → 촬영 기록 복원 → 기계 창고 입구','목표 플레이 시간: 첫 플레이 기준 약 8~12분'])
text(42,175,'설정을 바꾼 뒤에는 관찰한 정보를 이용해 소품 이동 또는 장치 조작이 필요하다.',10,purple,True)
finish()

header(5,'PUZZLE 01','그림자 연습실 - 진짜 용은 벽에 있다')
art(2,42,457,511,242)
block(416,'목표',['세트 조각 2개를 밀어 벽에 비친 그림자를 용의 목표 실루엣에 맞춘다.'])
box(42,250,511,118,'플레이 순서',['1  그림자 OFF: 세트 조각과 이동 레일을 살펴본다.','2  E로 조각을 잡고 좌우로 밀어 위치를 조정한다.','3  그림자 ON: 벽의 목표 모양과 실제 그림자를 비교한다.','4  두 조각이 목표 위치에 맞으면 확인등이 켜지고 출구가 열린다.'])
block(210,'판정과 힌트',['그림자 ON + 조각 A 정답 위치 + 조각 B 정답 위치가 성공 조건이다.','정답 위치 근처에서는 조각이 약하게 고정되며, 틀려도 계속 조정할 수 있다.'])
finish()

header(6,'PUZZLE 02','블룸 과다 구역 - 너무 빛나서 보이지 않는 것')
art(3,42,457,511,242)
block(416,'목표',['방 안의 세 간판에서 문양을 확인하고 제어반에 올바른 순서로 입력한다.'])
box(42,250,511,118,'플레이 순서',['1  방을 이동하며 빛이 번지는 간판 3개를 발견한다.','2  블룸 OFF: 빛 번짐이 줄어 별 → 달 → 태양 문양과 화살표가 드러난다.','3  제어반에서 확인한 순서대로 버튼을 누른다.','4  정답이면 출구가 열리고, 오답이면 입력만 초기화된다.'])
block(210,'설계 의도',['블룸을 끄는 행위는 단서를 읽는 방법이며, 정답 판정은 버튼 입력 순서로 한다.','빛의 강도를 제한하고 문양의 형태를 구분해 눈의 부담을 줄인다.'])
finish()

header(7,'PUZZLE 03','감독의 편집실 - 삭제된 테이크 복원')
art(3,42,488,511,210)
block(449,'세 필름에서 각각 단서를 찾는다',['필름을 고르고 설정을 조절해 번호, 이동 방향, 보관실 표식을 확인한다.'])
box(42,270,511,135,'필름과 정답',['필름 A  ·  블룸 OFF → 빛 뒤의 장면 번호 3 확인','필름 B  ·  그림자 OFF → 가려진 오른쪽 화살표 확인','필름 C  ·  노출 어둡게 → 밝은 배경에 묻힌 톱니 표식 확인','제어반 정답: 장면 3 / 오른쪽 / 톱니 표식'])
block(230,'클리어 연출',['영사기가 원본 기록을 재생하고 용의 하체가 기계 창고로 옮겨졌음을 보여 준다.','정답을 맞힌 항목은 유지하고, 필름은 언제든 다시 확인할 수 있다.'])
text(42,132,'제작 메모',11,purple,True)
text(42,111,'시각 효과와 정답 판정을 분리해 기기별 화면 차이에도 퍼즐이 일관되게 작동하도록 한다.',9.5)
text(42,91,'Stage 2는 제안 기획이며, 실제 렌더링 결과와 플레이 시간은 구현 후 검증이 필요하다.',9.5,muted)
finish(); c.save(); print(out.resolve())
