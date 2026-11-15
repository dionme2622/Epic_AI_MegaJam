from pathlib import Path
import csv

root = Path(__file__).resolve().parent / 'VoicePrompts'
with (root/'Inworld_All_Dialogue_Prompts_KO_EN.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
tags = [
    'bold, heroic, loudly challenging, emphasizing “dragon”',
    'booming villainous laughter, theatrical, arrogantly delighted, threatening',
    'startled, confused, dropping the villain act, brief pause after “Wait”',
    'incredulous, offended, slightly indignant, dry comic timing',
    'questioning, mildly annoyed, then resolute and determined',
    'curious, thinking aloud, brightening with a practical idea',
    'attentive, curious, quietly drawing a conclusion',
    'focused, searching, mildly impatient, conversational',
    'puzzled, technically frustrated, thoughtful pause between sentences',
    'surprised recognition, then amused and matter-of-fact',
    'calm, focused, determined, thinking aloud',
    'relieved, quietly excited, satisfied pause before the final sentence',
    'determined, then observant and curious',
    'cautiously relieved, quietly excited, emphasizing “real”',
    'neutral, factual, dry bureaucratic delivery, brief pause after the heading',
    'calm, firm, quietly satisfied, dry humor, emphasizing “to the end”',
    'friendly, confident, expectant, relieved to resume filming',
    'gently interrupting, composed, slightly fussy, thoughtful pause after “Wait”',
    'hesitant, baffled, understated concern, awkward pause before speaking',
    'weary, exasperated, muttering, dry deadpan delivery',
    'concerned, increasingly panicked, accelerating delivery, abruptly cut off mid-sentence',
    'screaming in sudden panic, sustained open vowel, comic alarm',
    'confused, incredulous, slightly indignant, emphasizing “MY legs”',
    'reading a production note, clear, practical, measured, brief pauses between instructions',
    'reading a production note, clear, thoughtful, measured',
    'reading a production note, precise, matter-of-fact, emphasizing keeping the first take',
    'reading a production note, clear, practical, measured, brief pause between sentences',
    'reading a production note, precise, measured, emphasizing the color comparisons',
    'reading a production note, reflective, clear, matter-of-fact',
    'reading a production note, clear, practical, measured, brief pause between sentences',
    'reading a production note, precise, measured, emphasizing the signal returning',
    'reading a development memo, neutral, bureaucratic, dry seriousness, pauses between sentences',
]
assert len(tags) == len(rows) == 32
for r,t in zip(rows,tags):
    en = r['en']
    if r['id'] == 'E04':
        en = "What's wrong with the animation now?"
        t = 'sighing, weary, exasperated, muttering, dry deadpan delivery'
    if r['id'] == 'E07':
        en = 'Why are MY legs over there?!'
    r['playground_en'] = f'[{t}] {en}'
    kt = t.replace('“dragon”', '“드래곤”').replace('“Wait”', '“잠깐”').replace('“real”', '“진짜”').replace('“to the end”', '“끝까지”').replace('“MY legs”', '“내 다리”')
    r['playground_ko'] = f'[{kt}] {r["ko"]}'

doc = ['# Inworld Playground 복사·붙여넣기용 대사',
       '요청한 `[연기 지시] 대사` 형식입니다. 각 코드 블록의 한 줄만 복사하세요. 드래곤은 Hades, 용사는 Brick 기준입니다. 메모·기록의 Hades 배정은 낭독용 제안입니다. 대괄호는 요청하신 표현 형식이며 모델별 지원 문법을 검증한 목록은 아닙니다.',
       '영어 E07은 요청하신 강조·문장부호를 반영했고, E04의 `Sigh...`는 실제 한숨 지시로 바꿨습니다. 나머지 발화문은 이전 원문을 유지했습니다.']
for r in rows:
    doc.append(f'## {r["id"]} · {r["scene"]} · {r["speaker"]} / {r["voice"]}\n\n영어\n\n```text\n{r["playground_en"]}\n```\n\n한국어\n\n```text\n{r["playground_ko"]}\n```')
(root/'Inworld_Playground_Ready_KO_EN.md').write_text('\n\n'.join(doc)+'\n',encoding='utf-8')
for lang in ['en','ko']:
    (root/f'Inworld_Playground_{lang.upper()}.txt').write_text('\n\n'.join(f'{r["id"]} | {r["voice"]}\n{r[f"playground_{lang}"]}' for r in rows)+'\n',encoding='utf-8')
print(f'Generated {len(rows)} lines per language.')
