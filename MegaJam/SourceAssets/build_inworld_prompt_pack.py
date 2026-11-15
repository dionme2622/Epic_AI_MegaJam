"""Export a reviewable voice direction pack from current subtitle source text."""
from pathlib import Path
import re
import csv

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'Source/MegaJam'
OUT = ROOT / 'SourceAssets/VoicePrompts'
OUT.mkdir(exist_ok=True)
rows = []

def add(id, scene, speaker, ko, en, direction, source, timing='자연스러운 속도. 생성 후 실제 음성 길이에 맞춰 자막 조정.'):
    voice = 'Brick' if speaker == '용사' else 'Hades'
    rows.append(dict(id=id, scene=scene, speaker=speaker, voice=voice, ko=ko, en=en, direction=direction, timing=timing, source=source))

p = (SRC/'DirectorCutPrologueSubtitles.cpp').read_text(encoding='utf-8')
ko = re.findall(r'TEXT\("(.*?)"\)', re.search(r'CaptionKo\[\] = \{(.*?)\};', p).group(1))
en = re.findall(r'TEXT\("(.*?)"\)', re.search(r'CaptionEn\[\] = \{(.*?)\};', p).group(1))
dirs = [
 'Deliver a bold theatrical battle challenge. Strong projection and heroic confidence, with an emphatic final address to the dragon. Do not sound angry at a real person.',
 'Begin with a booming villainous laugh, then deliver the threat with delighted theatrical arrogance. This is an actor playing a final boss in a comedy. Keep the words intelligible.',
 'Abruptly drop the villain performance. Start with a startled interruption, pause as you look down, then ask with genuine bafflement. Dry comic timing; no tragic pain.',
 'Sound personally offended by an absurd production decision. Stress the logic of being off camera, then let disbelief rise into the final question. Irritated and incredulous, not a roar.'
]
for i,(k,e,d) in enumerate(zip(ko,en,dirs),1):
    add(f'P{i:02}', '프롤로그', '용사' if i==1 else '드래곤', k,e,d,'DirectorCutPrologueSubtitles.cpp',f'기존 영어 클립 길이 약 {[1.824,3.48,3.912,4.32][i-1]}초. 새 생성 길이는 별도 확인.')

p = (SRC/'DirectorCutStoryData.cpp').read_text(encoding='utf-8')
pairs = re.findall(r'LOCTEXT\("(\w+)Ko", "(.*?)"\),\s*LOCTEXT\("\w+En", "(.*?)"\)',p)
dirs = [
 'Start with a questioning realization about where your legs were moved. Take a short beat, then turn annoyance into a firm, practical decision to retrieve them yourself.',
 'Notice the wheels with curious interest. Brighten slightly as a workable idea occurs to you. Practical optimism, spoken to yourself, without making fun of the chair.',
 'Listen attentively, then identify the workshop with quiet curiosity. Slight uncertainty on the final inference, as you follow the sound beyond the curtain.',
 'Scan a cluttered workshop while thinking aloud. Focused and mildly impatient, but confident that the transfer record can be found. Keep it conversational.',
 'Inspect a defective gear with puzzled technical frustration. Emphasize that the teeth do not touch; then reason out what the original model must have looked like. Leave a short thinking beat between sentences.',
 'React with a small burst of surprise on recognizing the hero’s legs. Then settle into an amused, matter-of-fact justification for borrowing them. Underplay the absurdity.',
 'Recognize the editing room, then state your next objective with calm determination. You are following a paper trail, not addressing the player as a tutorial narrator.',
 'Recognize the crate with growing relief. Take a small satisfied pause before the final sentence. This is sincere hope, with no knowledge yet that the crate is empty.',
 'Sound newly determined after the earlier disappointment. Then notice the note beside the lighting console with alert curiosity. Do not overemphasize the directions.',
 'Quiet excitement at seeing your real legs through the glass. Stress that this time they are real, with cautious relief after being misled before. Avoid a full victory shout.'
]
for i,((key,k,e),d) in enumerate(zip(pairs,dirs),1):
    stage = '스테이지 1' if i<=3 else '스테이지 2' if i<=6 else '스테이지 3' if i<=8 else '스테이지 4'
    add(key,stage,'드래곤',k.removeprefix('드래곤: '),e.removeprefix('Dragon: '),d,'DirectorCutStoryData.cpp','현재 자막 기본 4초. 긴 대사는 억지로 압축하지 말고 자막 표시 시간을 늘릴 것.')

add('StorageLog','스테이지 3 / 상자 개봉','기록 낭독','보관 기록: 원래 다리는 최종 보관소로 옮겼습니다.','Storage log: The real legs were moved to the final vault.','Read this written storage log in a flat, factual tone. A small beat after the label, then clear bureaucratic delivery. No villain acting. This voice assignment is a production suggestion, not an existing speaking character.','Stage3StorageCrate.cpp')
add('FinalTake','스테이지 4 / 회수 완료','드래곤','이번 컷은 끝까지 찍어.','Keep the camera rolling to the end of this take.','A calm, firm instruction to the off-screen film crew. Quiet satisfaction with a trace of weary authority. Emphasize keeping the camera rolling until the end. Land the meta joke dryly.','DirectorCutPlayHUD.cpp','현재 표시 5.5초.')

p=(SRC/'DirectorCutEnding.cpp').read_text(encoding='utf-8')
def loc(key):
    return re.search(r'LOCTEXT\("'+key+r'", "(.*?)"\)',p).group(1)
ending=[
 ('E01','엔딩 공통','용사','HeroLine','HeroLineEnglish','Friendly, confident anticipation from a fellow actor ready to resume filming. Ask the opening question lightly, then express relief that the final battle can finally be filmed properly.','기존 영어 약 4.632초, 시작 0.583초.'),
 ('E02','엔딩 공통','드래곤','DragonLine','DragonLineEnglish','Interrupt gently but decisively. You are asserting creative control over your appearance. A thoughtful pause after the opening word; composed, slightly fussy, and dryly funny.','기존 영어 약 4.608초, 시작 5.417초.'),
 ('E03','원래 다리 엔딩','용사','AwkwardHero','AwkwardHeroEnglish','Watch the dragon’s awkward walk in silence for a brief beat. Ask with hesitant disbelief and understated concern. The question should feel spontaneous, with no big comic punchline voice.','기존 영어 약 3.144초, 시작 6.5초. 자막 6.5–9.7초.'),
 ('E04','원래 다리 엔딩','드래곤','AwkwardDragon','AwkwardDragonEnglish','Begin with a short audible weary exhale, then mutter the complaint with exhausted frustration at yet another production problem. Keep the anger low and the comedy deadpan. For English, perform the opening Sigh as an exhale rather than literally saying the word.','기존 영어 약 4.2초, 시작 10.125초. 자막 10.1–14.4초.'),
 ('E05','수레 엔딩','드래곤','CartBrakes','CartBrakesEnglish','Begin with puzzled concern, then let panic build as the cart accelerates. Cut the last phrase off abruptly mid-thought because you are losing control. Do not resolve the sentence or add a scream to this clip.','기존 영어 약 2.496초, 시작 0.75초. 자막 0.75–3.3초.'),
 ('E06','수레 엔딩','드래곤','CartScream','CartScreamEnglish','Perform a single sustained open-vowel scream of startled panic while speeding downhill. Rise quickly into panic, sustain briefly, then finish naturally. Comic alarm, not agony; no extra words or laughter.','기존 영어 약 1.704초, 시작 약 3.292초. 자막 3.3–5.75초.'),
 ('E07','용사 다리 엔딩','용사','HeroLegsQuestion','HeroLegsQuestionEnglish','Notice your own legs attached to the dragon. Start with baffled recognition, then ask with rising personal indignation. Stress my legs naturally. Surprise and disbelief, not a battle cry.','기존 영어 약 3.288초, 시작 3.5초. 현재 자막은 6.5초에 끝나므로 음성 끝과 차이 확인.')
]
for id,scene,speaker,k,e,d,t in ending: add(id,scene,speaker,loc(k),loc(e),d,'DirectorCutEnding.cpp',t)

p=(SRC/'DirectorCutWallNote.cpp').read_text(encoding='utf-8')
notes=re.findall(r'Korean = LOCTEXT\("(\w+)Ko", "(.*?)"\);\s*English = LOCTEXT\("\w+En", "(.*?)"\);',p)
for key,k,e in notes:
    add('Note_'+key,'작업 메모 낭독','메모 낭독',k,e,'Read this production note as the dragon quietly reading a written clue. Clear, measured, practical delivery with a small pause between instructions. Keep every condition and comparison precise. No added explanation, discovery exclamation, or solution beyond the supplied text.','DirectorCutWallNote.cpp','플레이어가 메모를 열었을 때 사용하는 선택 제작분. 원래는 대화 자막이 아닌 문서 텍스트.')
add('P_Note','프롤로그 / 개발 메모','메모 낭독','개발 메모. 최종 보스 하체 — 테스트 구역으로 이동. 현재 카메라에 잡히지 않으므로 임시 제거.','Development note. Final boss lower body — moved to the test area. Temporarily removed because it is outside the camera frame.','Read a production memo with neutral bureaucratic seriousness. Pause after the heading and between sentences. The absurd removal of the boss’s legs is treated as routine paperwork. Do not add character reactions.','BossPrologue/make_graphics.ps1','선택 제작분. 한국어는 이미지의 제목·줄바꿈을 낭독용 구두점으로 연결. 영어는 제작용 번역.')

common='Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips.'
profiles={
 'Hades':'Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat.',
 'Brick':'Hero: a grounded adult masculine voice with a clear, sturdy mid-to-low register. A confident fantasy hero who is also a fellow actor. Heroic projection in the opening challenge; relaxed collegial speech in the ending; genuine bafflement in the reveal jokes.'
}
intro='''# Inworld 전체 대사 프롬프트 팩

현재 C++ 자막과 시네마틱 제작 소스를 기준으로 정리했습니다. 본편 대사·기록 자막 23개, 작업 메모 8개, 프롤로그 개발 메모 1개로 총 32개입니다. 메모의 화자 배정은 제작 제안입니다. 한국어와 영어를 각각 만들면 64클립입니다.

기존 제작 기록의 영어 보이스 배정은 드래곤 Hades / 용사 Brick입니다. 한국어는 같은 인물의 음색을 유지하도록 아래 성격 지시를 사용하고 실제 생성 결과를 확인하세요. 언어별로 한 줄씩 별도 생성합니다. 한국어·영어를 한 파일에 연달아 읽히지 마세요.

각 항목의 `Performance prompt`는 연기 지시용이고 `KO spoken text` 또는 `EN spoken text`가 실제 발화문입니다. 지시 입력란이 없는 작업 흐름에서는 프롬프트 문장까지 발화문에 붙여 넣지 마세요. 아래 문구는 특정 Inworld 입력 문법이나 태그를 전제하지 않는 제작용 지시입니다.

## 공통 연기 지시

'''
doc=[intro,common,'\n\n## 캐릭터 음색\n']
for voice,profile in profiles.items(): doc.append(f'\n**{voice}**\n\n{profile}\n')
doc.append('''
## 제작 및 적용 기준

- 파일명은 `ID_KO.wav`, `ID_EN.wav`로 통일합니다. 대사마다 개별 클립을 만드세요.
- 기존 초 수치는 참조값입니다. 새 음성이 그 길이에 정확히 맞는다는 뜻이 아닙니다. 길면 자막·시퀀스 타이밍을 조정하세요. 특히 스테이지 독백의 현재 기본 표시 시간은 4초입니다.
- 비명과 웃음은 해당 클립에서 실제로 연기합니다. 영어 E04의 `Sigh...`는 기존 자막 원문이며, 소리로는 한숨을 연기하는 방향입니다.
- UI 버튼, 조작 키, 설정 항목, 퍼즐 상태 표시와 간판은 대사 목록에서 제외했습니다. 메모와 기록은 읽을 수 있는 서사 텍스트라 포함했습니다.
- 과거 `NewKnight/make_subtitles.py`의 승리 내레이션·쓰러지는 연기 대사 등은 현재 보스 프롤로그의 4개 자막과 달라 본편에 중복 포함하지 않았습니다.
- 이 목록은 텍스트 소스 대조 결과입니다. 에디터의 맵 인스턴스·블루프린트에서 별도로 수정한 문자열까지 실시간 검사한 결과는 아닙니다.

## 개별 클립
''')
for r in rows:
    prompt=common+' '+profiles[r['voice']]+' '+r['direction']
    r['performance_prompt']=prompt
    doc.append(f"\n### {r['id']} · {r['scene']} · {r['speaker']}\n\n보이스: **{r['voice']}**\n\n**KO spoken text**\n\n> {r['ko']}\n\n**EN spoken text**\n\n> {r['en']}\n\n**Performance prompt**\n\n```text\n{prompt}\n```\n\n타이밍: {r['timing']}\n\n원문 근거: `{r['source']}`\n")
(OUT/'Inworld_All_Dialogue_Prompts_KO_EN.md').write_text('\n'.join(doc),encoding='utf-8')
with (OUT/'Inworld_All_Dialogue_Prompts_KO_EN.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]))
    writer.writeheader();writer.writerows(rows)
assert len(rows)==32, len(rows)
print(f'Exported {len(rows)} cues to {OUT}')
