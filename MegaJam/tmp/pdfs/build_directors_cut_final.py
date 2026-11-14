from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path.cwd()
OUT = ROOT / "output/pdf/Directors_Cut_Prologue_Stage4_Design.pdf"
GENERATED = Path("C:/Users/LHH/.codex/generated_images/01a1c368-7c29-7123-8d09-d646705e7b7b")
ART = {
    "prologue": ROOT / "output/Prologue_Fortress/fortress-throne-hall.png",
    "stage1": ROOT / "output/Prologue_Fortress/fortress-backstage-keep.png",
    "stage1_game": ROOT / "output/Prologue_Fortress/transition_stage_entry_done.png",
    "stage2": GENERATED / "exec-b759c320-2a56-4557-ae15-995b3d3fba17.png",
    "stage3": GENERATED / "exec-714d4851-6ee4-419d-9563-40fdbf04dcbb.png",
    "stage4": GENERATED / "exec-1fe19750-b14a-4da1-9a30-075316e94668.png",
    "bloom_on": ROOT / "output/BloomPuzzle/DetailRefined/star_on.png",
    "bloom_off": ROOT / "output/BloomPuzzle/DetailRefined/star_off.png",
    "resolution_low": ROOT / "output/ResolutionCorridor/final_low.png",
    "shadow_on": ROOT / "output/Stage4Integrated/shadow_on.png",
    "shadow_off": ROOT / "output/Stage4Integrated/shadow_off.png",
}
for font, file in [("Malgun", "malgun.ttf"), ("MalgunBold", "malgunbd.ttf")]:
    pdfmetrics.registerFont(TTFont(font, str(Path("C:/Windows/Fonts") / file)))

W, H = A4
M = 44
CW = W - 2 * M
TOTAL = 12
INK = "#201B29"
MUTED = "#565065"
PAPER = "#FAF7F1"
LINE = "#DAD2C7"
PURPLE = "#56396B"
GOLD = "#B97532"
CREAM = "#F1E9DA"
SOFT_PURPLE = "#EEE7F2"

c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
c.setTitle("Director's Cut | 잘려 나간 용 | 통합 게임 기획안")
c.setAuthor("Director's Cut 프로젝트")
c.setSubject("프롤로그와 Stage 1~4의 스토리, 퍼즐, 레벨 디자인 및 엔딩")
page = 0
image_cache = {}


def box(x, top, w, h, fill, radius=0, stroke=None):
    c.setFillColor(HexColor(fill))
    if stroke:
        c.setStrokeColor(HexColor(stroke))
    if radius:
        c.roundRect(x, H - top - h, w, h, radius, fill=1, stroke=bool(stroke))
    else:
        c.rect(x, H - top - h, w, h, fill=1, stroke=bool(stroke))


def line(x1, x2, top, color=LINE, width=0.65):
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(width)
    c.line(x1, H - top, x2, H - top)


def label(text, x, top, size=10, color=INK, bold=False):
    c.setFont("MalgunBold" if bold else "Malgun", size)
    c.setFillColor(HexColor(color))
    c.drawString(x, H - top - size, text)


def paragraph(text, top, x=M, w=CW, size=11.2, leading=17.3, color=MUTED, bold=False, draw=True):
    style = ParagraphStyle(
        "body", fontName="MalgunBold" if bold else "Malgun", fontSize=size,
        leading=leading, textColor=HexColor(color), wordWrap="CJK",
    )
    item = Paragraph(escape(text).replace("\n", "<br/>"), style)
    _, h = item.wrap(w, H)
    if draw:
        item.drawOn(c, x, H - top - h)
    return h


def image(key, top, h, *, x=M, w=CW, crop=None):
    if key not in image_cache:
        encoded = BytesIO()
        with Image.open(ART[key]) as source:
            source.convert("RGB").save(encoded, format="JPEG", quality=91, optimize=True, subsampling=0)
        encoded.seek(0)
        image_cache[key] = ImageReader(encoded)
    im = image_cache[key]
    iw, ih = im.getSize()
    left, upper, right, lower = crop or (0, 0, 1, 1)
    scale = max(w / (iw * (right - left)), h / (ih * (lower - upper)))
    rw, rh = iw * scale, ih * scale
    dx = x - left * rw - ((right - left) * rw - w) / 2
    dy = H - top - h - (1 - lower) * rh - ((lower - upper) * rh - h) / 2
    c.saveState()
    clip = c.beginPath()
    clip.rect(x, H - top - h, w, h)
    c.clipPath(clip, stroke=0, fill=0)
    c.drawImage(im, dx, dy, rw, rh, mask="auto")
    c.restoreState()


def caption(text, top, x=M, w=CW):
    return top + paragraph(text, top, x, w, size=8.5, leading=12, color=MUTED) + 8


def head(bookmark, chapter, title, subtitle):
    global page
    page += 1
    c.bookmarkPage(bookmark)
    c.addOutlineEntry(title, bookmark, level=0)
    box(0, 0, W, H, PAPER)
    box(0, 0, W, 5, PURPLE)
    label("DIRECTOR'S CUT", M, 27, 9, PURPLE, True)
    c.setFont("Malgun", 9)
    c.setFillColor(HexColor(MUTED))
    c.drawRightString(W - M, H - 36, chapter)
    line(M, W - M, 49)
    label(title, M, 63, 25, INK, True)
    tagline = paragraph(subtitle, 102, size=11.1, leading=16.5)
    return 102 + tagline + 17


def finish(used=None):
    if used is not None and used > H - 57:
        raise RuntimeError(f"Page {page} exceeds content area at y={used:.1f}")
    line(M, W - M, H - 45)
    label("잘려 나간 용  /  통합 게임 기획안", M, H - 35, 8, MUTED)
    c.setFont("MalgunBold", 8.5)
    c.setFillColor(HexColor(PURPLE))
    c.drawRightString(W - M, 26, f"{page:02d}  /  {TOTAL:02d}")
    c.showPage()


def blurb(title, text, y, *, x=M, w=CW):
    label(title, x, y, 13, PURPLE, True)
    return y + 24 + paragraph(text, y + 23, x, w) + 13


def numbered(items, y):
    for k, (title, body) in enumerate(items, 1):
        box(M, y + 2, 26, 23, SOFT_PURPLE, radius=4)
        label(f"{k:02d}", M + 6, y + 5, 9, PURPLE, True)
        label(title, M + 38, y, 11.8, INK, True)
        y += 19 + paragraph(body, y + 19, M + 38, CW - 38, size=10.8, leading=16.4) + 11
    return y


def note(title, text, y, fill=CREAM):
    h = paragraph(text, 0, w=CW - 30, size=10.2, leading=15.5, draw=False)
    box(M, y, CW, h + 48, fill, radius=7)
    label(title, M + 15, y + 10, 11.3, PURPLE, True)
    paragraph(text, y + 29, M + 15, CW - 30, size=10.2, leading=15.5)
    return y + h + 48 + 13


def table(headers, rows, widths, top, size=10.3):
    assert abs(sum(widths) - CW) < 0.1
    box(M, top, CW, 30, PURPLE, radius=4)
    x = M
    for heading, width in zip(headers, widths):
        label(heading, x + 10, top + 8, 9.5, "#FFFFFF", True)
        x += width
    top += 30
    for ix, row in enumerate(rows):
        heights = [paragraph(t, 0, w=width - 21, size=size, leading=15.1, draw=False)
                   for t, width in zip(row, widths)]
        hh = max(heights) + 18
        if ix % 2 == 0:
            box(M, top, CW, hh, "#F3EEE5")
        x = M
        for j, (t, width) in enumerate(zip(row, widths)):
            paragraph(t, top + 8, x + 10, width - 21, size=size, leading=15.1,
                      color=INK if j == 0 else MUTED, bold=j == 0)
            x += width
        top += hh
        line(M, W - M, top)
    return top + 16


def photo_pair(keys, captions, top, height=142, crop=None):
    gap = 12
    wid = (CW - gap) / 2
    xs = [M, M + wid + gap]
    for key, text, x in zip(keys, captions, xs):
        image(key, top, height, x=x, w=wid, crop=crop)
        caption(text, top + height + 5, x, wid)
    return top + height + 28


def map_chain(y):
    gap = 7
    wid = (CW - 4 * gap) / 5
    for idx, (top, name) in enumerate([
        ("PROLOGUE", "최종 전투"), ("STAGE 1", "성채 통로"), ("STAGE 2", "모델 제작소"),
        ("STAGE 3", "편집실"), ("STAGE 4", "촬영 보관소")
    ]):
        x = M + idx * (wid + gap)
        box(x, y, wid, 54, SOFT_PURPLE if idx < 4 else PURPLE, radius=5)
        label(top, x + 9, y + 8, 7.2, PURPLE if idx < 4 else "#EBDDFA", True)
        label(name, x + 9, y + 26, 10.2, INK if idx < 4 else "#FFFFFF", True)
    return y + 72


# 01 / Cover
page += 1
c.bookmarkPage("cover")
c.addOutlineEntry("표지", "cover", 0)
box(0, 0, W, H, "#1E1928")
box(M, 56, 33, 3, "#DFA361")
label("DIRECTOR'S CUT", M, 73, 15, "#ECC387", True)
label("잘려 나간 용", M, 103, 39, "#FFF8EE", True)
label("프롤로그부터 Stage 4까지", M, 169, 14, "#D8CDE6", True)
image("stage3", 219, 332, x=0, w=W)
box(0, 551, W, 4, "#B97F48")
paragraph("최종 보스 역할을 끝낸 드래곤이 무대 뒤로 향한다. 카메라에 잡히지 않아 잘려 나간 자신의 하체를 되찾기 위해, 게임 설정을 바꿔 세트와 촬영 기록의 비밀을 푼다.",
          588, w=CW - 45, size=14, leading=24, color="#FFF5E6")
line(M, W - M, 710, "#574861")
label("2.5D 횡스크롤 퍼즐 어드벤처", M, 731, 10.4, "#EAC188", True)
label("통합 게임 기획안  /  2026.11.14", M, 753, 9.5, "#D8CDE6")
c.showPage()

# 02 / Progression
y = head("overview", "GAME OVERVIEW", "게임의 흐름", "촬영이 끝난 성채에서 출발해, 무대 뒤 제작소와 편집실을 거쳐 최종 보관소로 향한다.")
y = map_chain(y)
y = table(["구간", "진행 내용", "다음 목표"], [
    ("프롤로그", "용사의 승리 장면이 끝나고, 카메라가 이동하며 드래곤의 하체가 잘려 나간 사실이 드러난다.", "성채 뒤편으로 나간다."),
    ("Stage 1", "앞발로 이동하며 성채 통로에서 방향과 상호작용을 익힌다. 횃불과 소품이 출구를 안내한다.", "제작소로 들어간다."),
    ("Stage 2", "휠체어를 타고 모델 품질을 바꿔 돌바퀴를 멈추고 톱니 승강기를 작동한다.", "승강기를 타고 위층 출구에 도달한다."),
    ("Stage 3", "초점 소품, 블룸 간판, 해상도 발판을 통과한다. 보관대의 상자는 비어 있다.", "운반 기록을 따라 최종 보관소로 간다."),
    ("Stage 4", "용사의 다리로 움직이며 네 카메라의 필름을 맞추고 그림자 무대를 건넌다.", "원래 하체를 회수한다."),
], [86, 260, CW - 346], y)
y = blurb("플레이의 기본 흐름", "설정이나 카메라를 바꾼다 → 보이는 단서를 확인한다 → 소품을 조작하거나 안전하게 이동한다. 퍼즐이 끝나면 조명, 장치음, 문 열림으로 결과를 알려준다.", y + 3)
y = note("이동 방식과 시점", "이동은 2.5D 측면 시점으로 진행한다. 제어반을 사용할 때는 단서와 조작부를 한 화면에 담는다. Stage 3 입구에서 용사의 다리를 임시 장착하는 장면을 넣어 이후 발판 점프를 설명한다.", y)
finish(y)

# 03 / Prologue
y = head("prologue", "PROLOGUE", "마지막 전투, 잘린 출연 분량", "용사의 최종 전투가 끝나는 순간, 드래곤의 이야기가 시작된다.")
image("prologue", y, 168, crop=(0, 0, 1, .66))
y = caption("컨셉 이미지. 왕좌, 석조 기둥, 붉은 커튼이 전투 무대와 뒤편 통로를 나눈다.", y + 174)
y = numbered([
    ("승리 장면", "용사가 최종 보스인 용을 쓰러뜨린다. 승리 음악이 흐르고 용사는 무대 밖으로 퇴장한다."),
    ("카메라가 움직인다", "용은 고개를 들며 ‘쓰러지는 연기는 이 정도면 됐겠지’라고 말한다. 일어나려는 용을 따라 카메라가 오른쪽으로 이동한다. 프레임 밖에 있어야 할 하체가 통째로 비어 있다."),
    ("개발 메모를 발견한다", "‘최종 보스 하체 - 테스트 구역으로 이동. 현재 카메라에 잡히지 않으므로 임시 제거.’ 용은 앞발로 몸을 끌어 ‘하체 보관실’ 표시가 있는 무대 뒤편으로 향한다."),
], y + 2)
y = note("장면 전환", "카메라가 용의 뒷모습과 통로 입구를 잡으면 화면을 천천히 어둡게 한다. Stage 1에서 화면이 밝아지며 측면 시점의 조작을 시작한다.", y)
finish(y)

# 04 / Stage 1
y = head("stage1", "STAGE 1", "성채 뒤편 통로", "왕좌의 촬영 세트에서 벗어나 제작소로 이어지는 첫 조작 구간.")
image("stage1", y, 164, crop=(0, 0, 1, .65))
y = caption("성채 뒤편 컨셉. 석조 아치, 도르래, 뒤집힌 배경판을 통해 무대의 뒷면을 보여준다.", y + 170)
y = blurb("이동과 시선 유도", "횃불이 가까운 벽과 바닥을 비추고, 커튼 뒤로 통로가 이어진다. 플레이어는 앞발로 오른쪽으로 움직이면서 길을 찾는다. 조작을 익힐 수 있도록 첫 구간은 짧은 평지로 구성한다.", y + 4)
y = blurb("소품 배치", "벽의 문양 받침대, 제작 중인 돌 소품, 바닥에 떨어진 촬영 흔적을 지나간다. 앞쪽에는 극 중 성채의 표면을, 뒤쪽에는 목재 받침과 세트 조립 흔적을 배치한다.", y)
y = blurb("Stage 2로 이어지는 문", "성채 끝의 문 너머로 기계 소리와 따뜻한 작업등이 새어 나온다. 다음 스테이지에서는 작업용 휠체어에 올라 평평한 제작소를 이동한다.", y)
y = note("제작 참고", "현재 성채 통로 맵에서 석조 배경과 횃불, 오른쪽 출구를 확인할 수 있다. 성채에서 제작소로 넘어가는 최종 연결과 휠체어 탑승 장면은 전체 흐름에 맞춰 확인한다.", y)
finish(y)

# 05 / Stage 2
y = head("stage2", "STAGE 2", "무대 뒤편의 모델 제작소", "모델 품질에 따라 달라지는 기계의 동작을 이용해 위층 출구까지 올라간다.")
image("stage2", y, 270)
y = caption("최신 컨셉 이미지. 1층은 평평하고 오른쪽 문은 승강기로만 닿는 높이에 있다.", y + 276)
y = table(["구간", "상태와 플레이", "성공 조건"], [
    ("돌바퀴", "HIGH에서 바퀴가 굴러간다. 정지 구간에 들어오는 순간 LOW로 바꾸면 각진 접지면이 바닥에 닿으며 멈춘다.", "두 표식 사이에서 정지하면 문이 열린다."),
    ("톱니 승강기", "LOW에서는 단순화된 톱니가 헛돈다. 타고 내리는 바닥의 높이를 맞추고, HIGH에서 승강장에 올라 E로 작동한다.", "위층 발판에 내려 오른쪽 문으로 이동한다."),
], [90, 275, CW - 365], y, size=10)
y = note("이동 동선", "휠체어 주행 구간에는 계단과 경사를 두지 않는다. 돌바퀴의 두 모델은 같은 크기와 축을 공유하며 테두리 형태가 달라진다. 승강기를 타고 오르면 바로 위층 통로와 이어진다.", y)
finish(y)

# 06 / Stage 3 overview
y = head("stage3", "STAGE 3", "편집실과 빈 상자", "세트의 화면을 바꿔가며 상자를 찾아가고, 촬영이 끝난 뒤 무슨 일이 있었는지 알아낸다.")
image("stage3", y, 270)
y = caption("편집실 컨셉 이미지. 초점 소품실에서 간판 세트와 발판 복도를 거쳐 빈 상자에 닿는다.", y + 276)
y = blurb("입구에서 보는 운반 장면", "촬영 모니터에 드래곤의 하체가 상자에 들어가는 장면이 남아 있다. 모니터 속 상자의 무늬를 보관 구역에서 다시 확인할 수 있게 하여 목적지를 분명히 잡아준다.", y + 2)
y = blurb("용사의 다리를 임시 장착", "Stage 3 입구에서 전투 촬영용 예비 소품인 용사의 다리를 장착한다. 짧은 이동과 낮은 점프로 조작을 보여주고, 해상도 발판과 최종 무대까지 이어서 사용한다.", y)
y = note("구간 연결", "초점 소품실의 문을 열고 블룸 간판으로 이동한 뒤, 해상도 테스트 복도를 건넌다. 각 구간에서만 관련 화면 효과와 안내를 보여준다.", y)
finish(y)

# 07 / Stage 3 puzzles 1 and 2
y = head("stage3-filters", "STAGE 3 / PUZZLES 1-2", "초점 소품실과 블룸 간판", "열쇠를 맞춘 뒤 과하게 빛나는 간판에서 운반 통로의 단서를 읽는다.")
y = blurb("01  초점 밖 소품", "촬영 세트의 열쇠 조각이 서로 다른 깊이에 놓여 있다. 처음에는 카메라가 열쇠를 보여준 뒤 플레이어에게 돌아온다. 제어반을 사용하면 정면 촬영 시점으로 전환된다.", y)
y = numbered([
    ("초점을 고른다", "E로 시작하고 Q 또는 1, 2로 앞뒤 조각을 선택한다. 선택한 조각에 초점이 맞는다."),
    ("한 화면에 정렬한다", "A/D로 선택한 조각을 움직인다. Shift로 정밀하게 조정하고, 두 조각이 열쇠처럼 이어져 보이면 Enter로 확인한다."),
], y)
y = blurb("02  과노출 간판", "별, 달, 해가 그려진 촬영용 간판의 문양을 블룸이 가린다. B로 블룸을 끄고 각 간판을 읽는다. 제어반에서 E로 입력을 시작하고 별 → 달 → 해 순으로 해당 키를 누른다.", y + 4)
y = photo_pair(["bloom_on", "bloom_off"], ["플레이 테스트 / 블룸 켜짐", "플레이 테스트 / 블룸 꺼짐"],
               y + 2, height=128, crop=(.17, .15, .81, .68))
y = note("성공과 재시도", "열쇠가 맞으면 문이 열리고 이동 시점으로 복귀한다. 간판의 오답은 입력 순서만 초기화한다. 간판 뒤로 드러난 운반 수레 자국은 다음 복도로 이어진다.", y)
finish(y)

# 08 / Stage 3 resolution and ending
y = head("stage3-box", "STAGE 3 / PUZZLE 3", "해상도 검수 복도와 빈 상자", "낮은 해상도에서 확인한 길로 보관대에 도달한다.")
image("resolution_low", y, 201, crop=(.17, .15, .81, .68))
y = caption("플레이 테스트. 점무늬 표식은 해상도를 낮췄을 때 안전 발판 위치를 알려준다.", y + 207)
y = numbered([
    ("저해상도 단서 확인", "설정에서 해상도를 낮음으로 바꾼다. 복잡한 점무늬에서 큰 표식이 드러나고 안전 발판 세 개의 위치를 읽을 수 있다."),
    ("발판을 순서대로 밟기", "용사의 다리로 안전한 발판 세 개를 차례로 밟는다. 확인 후 해상도를 높여도 길과 판정은 유지된다. 잘못된 발판을 밟으면 서서히 내려가고 복도 시작점으로 돌아간다."),
    ("보관대를 열기", "영상과 같은 무늬의 상자가 조명 아래 놓여 있다. 뚜껑을 열면 비어 있고, 안쪽에는 하체 모양으로 눌린 완충재가 남아 있다."),
], y + 2)
y = note("다음 촬영 구역", "상자 뒤의 손수레 자국과 운반 기록이 최종 촬영 보관소를 가리킨다. 무대 대기등이 켜지면 드래곤은 Stage 4로 향한다. 상자 상호작용과 Stage 4 전환은 제작 항목이다.", y)
finish(y)

# 09 / Stage 4 overview
y = head("stage4", "STAGE 4 / FINALE", "최종 촬영 보관소", "운반 기록의 결정적인 한 컷을 복원하고, 그 장면에 나온 무대를 직접 건넌다.")
image("stage4", y, 270)
y = caption("최종 컨셉 이미지. 네 화면과 다이얼, 그림자 무대, 하체 보관대, 용사의 다리를 장착한 드래곤.", y + 276)
y = table(["위치", "공간과 플레이"], [
    ("왼쪽 / 기록실", "차가운 석조 벽, 필름 릴, RGB 프리즘과 네 개의 화면. 운반 기록의 같은 순간을 맞춘다."),
    ("중앙 / 검수 무대", "매달린 성벽 배경판과 깊은 틈. 발판 위치와 배경판의 통과 시점을 읽고 점프한다."),
    ("오른쪽 / 회수 무대", "유리 보관함 안에 진짜 하체가 놓여 있다. 따뜻한 조명과 붉은 커튼으로 보관대를 강조한다."),
], [124, CW - 124], y)
y = note("최종 스테이지의 범위", "퍼즐은 색 신호 복원과 그림자 무대 두 개다. 현재 통합 레벨에는 기존 다이얼 퍼즐, 그림자 발판, 추락 복귀와 기본 회수 판정이 있다. 다음 페이지부터 최신 퍼즐과 엔딩의 제작 사양을 정리한다.", y)
finish(y)

# 10 / Stage 4 color sync
y = head("stage4-sync", "STAGE 4 / PUZZLE 1", "네 카메라의 같은 순간", "네 다이얼로 운반 필름을 돌려, 수레가 보관소 문턱을 넘는 장면을 맞춘다.")
y = blurb("기준 프레임", "첫 번째 화면으로 수레 앞바퀴가 문턱을 넘는 순간을 찾는다. 제어반 옆에는 문턱과 바퀴를 그린 기준 그림을 붙인다. 각 화면은 각도가 다르고, 다이얼을 돌리면 정지 프레임이 앞뒤로 바뀐다.", y)
y = table(["필터", "비교할 화면", "맞춰야 할 상태"], [
    ("빨강", "화면 1과 2", "앞바퀴의 분필 표시가 같은 방향을 향한다."),
    ("초록", "화면 2와 3", "견인 케이블이 같은 정도로 당겨져 있다."),
    ("파랑", "화면 3과 4", "문 위 점멸등과 보관대 셔터가 같은 단계에 있다."),
], [75, 110, CW - 185], y)
label("비교 순서", M, y, 11, PURPLE, True)
for i, (number, desc) in enumerate([("화면 1", "문턱에서 시작"), ("화면 2", "빨강 / 바퀴"), ("화면 3", "초록 / 케이블"), ("화면 4", "파랑 / 셔터")]):
    x = M + i * (CW / 4)
    box(x, y + 21, CW / 4 - 9, 43, SOFT_PURPLE, radius=5)
    label(number, x + 9, y + 25, 9.7, PURPLE, True)
    label(desc, x + 9, y + 43, 9.1, INK)
y += 78
y = numbered([
    ("1번 필름을 기준에 고정", "앞바퀴가 문턱을 넘는 프레임을 고른다. 그 컷에서 바퀴의 분필 표식이 오른쪽 위를 향한다고 가정한다."),
    ("단서를 이어서 세 화면을 맞춤", "빨강으로 2번 화면의 바퀴를 맞춘다. 초록으로 해당 컷의 케이블을 확인해 3번을 맞춘다. 파랑으로 3번의 점멸등과 셔터 상태를 읽고 4번을 맞춘다."),
    ("제출과 보상", "맞지 않은 화면 쌍의 경계가 한 번 깜빡인다. 다이얼은 조정한 위치에 남는다. 모두 맞으면 네 화면이 함께 재생되고, 실제 하체가 유리 보관함으로 옮겨진 장면을 볼 수 있다."),
], y)
y = note("조작과 제작 사양", "E로 제어반, Q로 전체 및 RGB 필터, 1~4로 화면별 프레임 조정, Space로 확인, R로 초기화한다. 바퀴 표시에는 방향 기준점을 넣어 시점이 달라도 비교할 수 있게 한다. 화면당 정지 프레임 네 장으로 시작하고, 각 비교의 정답이 하나인지 검증한다.", y)
finish(y)

# 11 / Stage 4 shadow
y = head("stage4-shadow", "STAGE 4 / PUZZLE 2", "그림자가 먼저 지나가는 무대", "발판을 확인하고 배경판의 움직임을 예측해, 용사의 다리로 두 개의 틈을 건넌다.")
y = photo_pair(["shadow_on", "shadow_off"], ["기존 발판 테스트 / 그림자 켜짐", "기존 발판 테스트 / 그림자 꺼짐"],
               y, height=115, crop=(.17, .16, .81, .68))
y = table(["관찰", "얻는 정보"], [
    ("그림자 끄기", "발판 끝과 틈이 드러난다. 뛰어야 할 거리와 착지 위치를 파악한다."),
    ("그림자 켜기", "천장 레일의 배경판이 벽에 톱니 모양 그림자를 드리운다. 벽의 황동 표식에 닿는 순간을 보고 실제 배경판의 통과를 예측한다."),
], [112, CW - 112], y, size=10)
y = numbered([
    ("첫 번째 틈 / 발판 세 개", "출발점에서 그림자가 황동 표식에 닿고 한 박자 뒤에 배경판이 지나가는 모습을 볼 수 있다. 같은 주기를 반복해 보여준 뒤, 발판 세 개를 건너도록 한다."),
    ("중간 안전 무대", "넓은 발판에서 쉬며 설정을 바꾸고 두 번째 틈을 관찰한다. 여기까지 도달하면 두 번째 틈에서 떨어져도 이 위치에서 재시도한다."),
    ("두 번째 틈 / 발판 세 개", "가운데 발판의 왼쪽은 배경판이 지나가고 오른쪽에는 대기할 공간이 있다. 배경판이 물러날 때 오른쪽에 착지한 뒤 마지막 발판으로 도약한다."),
], y + 1)
y = note("배경판과 실패 판정", "배경판의 경로와 충돌은 그림자 설정과 관계없이 같다. 레일의 방향 전환 소리와 반복 주기로 타이밍을 알린다. 그림자 설정은 안전한 발판에서 조작할 수 있게 하고, 첫 틈에서 실패하면 입구로 복귀한다.", y)
finish(y)

# 12 / Ending and handoff
y = head("ending", "ENDING / PRODUCTION", "복원한 컷, 그 다음 장면", "Stage 3의 빈 상자를 열었던 동작이 최종 무대에서 실제 하체를 여는 동작으로 이어진다.")
right_w = 247
right_x = W - M - right_w
image("stage4", y, 211, x=right_x, w=right_w, crop=(.70, .27, 1, .75))
image_end = caption("회수 무대 컨셉. 갑옷 다리와 원래 하체를 함께 보여준다.", y + 217, right_x, right_w)
left_w = CW - right_w - 21
y = blurb("복원 영상의 마지막 컷", "보관대에서 영상과 같은 카메라 각도로 하체를 비춘다. 플레이어가 상호작용하면 유리 덮개가 올라가고 용이 원래 하체를 회수한다.", y, w=left_w)
y = blurb("드래곤의 첫발", "무대 조명과 커튼으로 장면을 전환한다. 드래곤이 원래 하체로 첫발을 내딛고, 용사의 다리는 보관대 옆 거치대에 남는다.", y, w=left_w)
y = max(y, image_end) + 6
y = note("마지막 대사", "용  “이번 컷은 끝까지 찍어.”\n카메라는 드래곤이 무대 밖으로 걸어가는 모습까지 담고, 커튼이 닫히며 크레딧으로 이어진다.", y)
y = table(["제작 우선순위", "구현 및 검증할 내용"], [
    ("이야기 연결", "성채에서 제작소로 연결하고, Stage 3에서 용사의 다리 장착과 빈 상자 연출을 추가한다."),
    ("최종 퍼즐", "색 신호 화면과 프레임 단서, 이동 배경판과 그림자 선행 타이밍, 중간 체크포인트를 구현한다."),
    ("엔딩", "Stage 3에서 Stage 4로 전환하고 보관함 상호작용, 하체 재결합, 엔딩 컷을 연결한다."),
], [115, CW - 115], y, size=9.7)
finish(y)

assert page == TOTAL
c.save()
print(OUT)
