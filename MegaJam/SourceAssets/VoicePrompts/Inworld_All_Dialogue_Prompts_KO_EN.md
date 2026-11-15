# Inworld 전체 대사 프롬프트 팩

현재 C++ 자막과 시네마틱 제작 소스를 기준으로 정리했습니다. 본편 대사·기록 자막 23개, 작업 메모 8개, 프롤로그 개발 메모 1개로 총 32개입니다. 메모의 화자 배정은 제작 제안입니다. 한국어와 영어를 각각 만들면 64클립입니다.

기존 제작 기록의 영어 보이스 배정은 드래곤 Hades / 용사 Brick입니다. 한국어는 같은 인물의 음색을 유지하도록 아래 성격 지시를 사용하고 실제 생성 결과를 확인하세요. 언어별로 한 줄씩 별도 생성합니다. 한국어·영어를 한 파일에 연달아 읽히지 마세요.

각 항목의 `Performance prompt`는 연기 지시용이고 `KO spoken text` 또는 `EN spoken text`가 실제 발화문입니다. 지시 입력란이 없는 작업 흐름에서는 프롬프트 문장까지 발화문에 붙여 넣지 마세요. 아래 문구는 특정 Inworld 입력 문법이나 태그를 전제하지 않는 제작용 지시입니다.

## 공통 연기 지시


Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips.


## 캐릭터 음색


**Hades**

Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat.


**Brick**

Hero: a grounded adult masculine voice with a clear, sturdy mid-to-low register. A confident fantasy hero who is also a fellow actor. Heroic projection in the opening challenge; relaxed collegial speech in the ending; genuine bafflement in the reveal jokes.


## 제작 및 적용 기준

- 파일명은 `ID_KO.wav`, `ID_EN.wav`로 통일합니다. 대사마다 개별 클립을 만드세요.
- 기존 초 수치는 참조값입니다. 새 음성이 그 길이에 정확히 맞는다는 뜻이 아닙니다. 길면 자막·시퀀스 타이밍을 조정하세요. 특히 스테이지 독백의 현재 기본 표시 시간은 4초입니다.
- 비명과 웃음은 해당 클립에서 실제로 연기합니다. 영어 E04의 `Sigh...`는 기존 자막 원문이며, 소리로는 한숨을 연기하는 방향입니다.
- UI 버튼, 조작 키, 설정 항목, 퍼즐 상태 표시와 간판은 대사 목록에서 제외했습니다. 메모와 기록은 읽을 수 있는 서사 텍스트라 포함했습니다.
- 과거 `NewKnight/make_subtitles.py`의 승리 내레이션·쓰러지는 연기 대사 등은 현재 보스 프롤로그의 4개 자막과 달라 본편에 중복 포함하지 않았습니다.
- 이 목록은 텍스트 소스 대조 결과입니다. 에디터의 맵 인스턴스·블루프린트에서 별도로 수정한 문자열까지 실시간 검사한 결과는 아닙니다.

## 개별 클립


### P01 · 프롤로그 · 용사

보이스: **Brick**

**KO spoken text**

> 각오해라, 드래곤!!!

**EN spoken text**

> Prepare yourself, dragon!

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Hero: a grounded adult masculine voice with a clear, sturdy mid-to-low register. A confident fantasy hero who is also a fellow actor. Heroic projection in the opening challenge; relaxed collegial speech in the ending; genuine bafflement in the reveal jokes. Deliver a bold theatrical battle challenge. Strong projection and heroic confidence, with an emphatic final address to the dragon. Do not sound angry at a real person.
```

타이밍: 기존 영어 클립 길이 약 1.824초. 새 생성 길이는 별도 확인.

원문 근거: `DirectorCutPrologueSubtitles.cpp`


### P02 · 프롤로그 · 드래곤

보이스: **Hades**

**KO spoken text**

> 크하하!! 통구이로 만들어주지!!!!!!

**EN spoken text**

> Ha ha ha! I'll roast you alive!

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Begin with a booming villainous laugh, then deliver the threat with delighted theatrical arrogance. This is an actor playing a final boss in a comedy. Keep the words intelligible.
```

타이밍: 기존 영어 클립 길이 약 3.48초. 새 생성 길이는 별도 확인.

원문 근거: `DirectorCutPrologueSubtitles.cpp`


### P03 · 프롤로그 · 드래곤

보이스: **Hades**

**KO spoken text**

> 잠깐… 내 다리는 어디 갔지?

**EN spoken text**

> Wait... Where did my legs go?

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Abruptly drop the villain performance. Start with a startled interruption, pause as you look down, then ask with genuine bafflement. Dry comic timing; no tragic pain.
```

타이밍: 기존 영어 클립 길이 약 3.912초. 새 생성 길이는 별도 확인.

원문 근거: `DirectorCutPrologueSubtitles.cpp`


### P04 · 프롤로그 · 드래곤

보이스: **Hades**

**KO spoken text**

> 화면에 안 나온다고 다리를 떼어 가?

**EN spoken text**

> You took my legs because they were off camera?

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Sound personally offended by an absurd production decision. Stress the logic of being off camera, then let disbelief rise into the final question. Irritated and incredulous, not a roar.
```

타이밍: 기존 영어 클립 길이 약 4.32초. 새 생성 길이는 별도 확인.

원문 근거: `DirectorCutPrologueSubtitles.cpp`


### CastleResolve · 스테이지 1 · 드래곤

보이스: **Hades**

**KO spoken text**

> 다리는 테스트 구역으로 옮겼다고? 그럼 내가 직접 찾으러 가지.

**EN spoken text**

> They moved my legs to the test area? I'll go find them myself.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Start with a questioning realization about where your legs were moved. Take a short beat, then turn annoyance into a firm, practical decision to retrieve them yourself.
```

타이밍: 현재 자막 기본 4초. 긴 대사는 억지로 압축하지 말고 자막 표시 시간을 늘릴 것.

원문 근거: `DirectorCutStoryData.cpp`


### CastleChair · 스테이지 1 · 드래곤

보이스: **Hades**

**KO spoken text**

> 저 의자엔 바퀴가 달렸네. 앞발만 있어도 움직일 수 있겠어.

**EN spoken text**

> That chair has wheels. I could move it with just my front paws.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Notice the wheels with curious interest. Brighten slightly as a workable idea occurs to you. Practical optimism, spoken to yourself, without making fun of the chair.
```

타이밍: 현재 자막 기본 4초. 긴 대사는 억지로 압축하지 말고 자막 표시 시간을 늘릴 것.

원문 근거: `DirectorCutStoryData.cpp`


### CastleWorkshop · 스테이지 1 · 드래곤

보이스: **Hades**

**KO spoken text**

> 커튼 너머에서 기계 소리가 나. 저쪽이 제작소인가 봐.

**EN spoken text**

> I hear machinery past the curtain. That must be the workshop.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Listen attentively, then identify the workshop with quiet curiosity. Slight uncertainty on the final inference, as you follow the sound beyond the curtain.
```

타이밍: 현재 자막 기본 4초. 긴 대사는 억지로 압축하지 말고 자막 표시 시간을 늘릴 것.

원문 근거: `DirectorCutStoryData.cpp`


### WorkshopArrival · 스테이지 2 · 드래곤

보이스: **Hades**

**KO spoken text**

> 다리 운반 기록이 여기 어딘가에 있겠지.

**EN spoken text**

> The transfer record must be here somewhere.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Scan a cluttered workshop while thinking aloud. Focused and mildly impatient, but confident that the transfer record can be found. Keep it conversational.
```

타이밍: 현재 자막 기본 4초. 긴 대사는 억지로 압축하지 말고 자막 표시 시간을 늘릴 것.

원문 근거: `DirectorCutStoryData.cpp`


### WorkshopLift · 스테이지 2 · 드래곤

보이스: **Hades**

**KO spoken text**

> 톱니끼리 닿지도 않네. 원래 모형에는 저 틈에도 톱니가 있었을 텐데.

**EN spoken text**

> Those teeth don't even touch. The original gear must have had teeth in those gaps.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Inspect a defective gear with puzzled technical frustration. Emphasize that the teeth do not touch; then reason out what the original model must have looked like. Leave a short thinking beat between sentences.
```

타이밍: 현재 자막 기본 4초. 긴 대사는 억지로 압축하지 말고 자막 표시 시간을 늘릴 것.

원문 근거: `DirectorCutStoryData.cpp`


### WorkshopLegs · 스테이지 2 · 드래곤

보이스: **Hades**

**KO spoken text**

> 용사의 다리잖아! 내 다리를 찾을 때까지만 빌려 쓰자.

**EN spoken text**

> The hero’s legs! I’ll borrow them until I find mine.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. React with a small burst of surprise on recognizing the hero’s legs. Then settle into an amused, matter-of-fact justification for borrowing them. Underplay the absurdity.
```

타이밍: 현재 자막 기본 4초. 긴 대사는 억지로 압축하지 말고 자막 표시 시간을 늘릴 것.

원문 근거: `DirectorCutStoryData.cpp`


### EditingArrival · 스테이지 3 · 드래곤

보이스: **Hades**

**KO spoken text**

> 여기가 편집실이군. 운반 기록을 따라 내 다리가 든 상자를 찾자.

**EN spoken text**

> This is the editing room. I'll follow the transfer record to my crate.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Recognize the editing room, then state your next objective with calm determination. You are following a paper trail, not addressing the player as a tutorial narrator.
```

타이밍: 현재 자막 기본 4초. 긴 대사는 억지로 압축하지 말고 자막 표시 시간을 늘릴 것.

원문 근거: `DirectorCutStoryData.cpp`


### EditingCrate · 스테이지 3 · 드래곤

보이스: **Hades**

**KO spoken text**

> 운반 기록에 나온 상자야. 드디어 찾았네.

**EN spoken text**

> That's the crate from the transfer record. I finally found it.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Recognize the crate with growing relief. Take a small satisfied pause before the final sentence. This is sincere hope, with no knowledge yet that the crate is empty.
```

타이밍: 현재 자막 기본 4초. 긴 대사는 억지로 압축하지 말고 자막 표시 시간을 늘릴 것.

원문 근거: `DirectorCutStoryData.cpp`


### VaultArrival · 스테이지 4 · 드래곤

보이스: **Hades**

**KO spoken text**

> 진짜 다리는 이 보관소에 있어. 조명대 오른쪽에 메모지가 붙어 있네.

**EN spoken text**

> My legs are in this vault. There's a note to the right of the lighting console.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Sound newly determined after the earlier disappointment. Then notice the note beside the lighting console with alert curiosity. Do not overemphasize the directions.
```

타이밍: 현재 자막 기본 4초. 긴 대사는 억지로 압축하지 말고 자막 표시 시간을 늘릴 것.

원문 근거: `DirectorCutStoryData.cpp`


### VaultExhibit · 스테이지 4 · 드래곤

보이스: **Hades**

**KO spoken text**

> 저 유리 보관함 안에 내 다리가 있어. 이번엔 진짜야.

**EN spoken text**

> My legs are inside that glass case. This time they're real.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Quiet excitement at seeing your real legs through the glass. Stress that this time they are real, with cautious relief after being misled before. Avoid a full victory shout.
```

타이밍: 현재 자막 기본 4초. 긴 대사는 억지로 압축하지 말고 자막 표시 시간을 늘릴 것.

원문 근거: `DirectorCutStoryData.cpp`


### StorageLog · 스테이지 3 / 상자 개봉 · 기록 낭독

보이스: **Hades**

**KO spoken text**

> 보관 기록: 원래 다리는 최종 보관소로 옮겼습니다.

**EN spoken text**

> Storage log: The real legs were moved to the final vault.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Read this written storage log in a flat, factual tone. A small beat after the label, then clear bureaucratic delivery. No villain acting. This voice assignment is a production suggestion, not an existing speaking character.
```

타이밍: 자연스러운 속도. 생성 후 실제 음성 길이에 맞춰 자막 조정.

원문 근거: `Stage3StorageCrate.cpp`


### FinalTake · 스테이지 4 / 회수 완료 · 드래곤

보이스: **Hades**

**KO spoken text**

> 이번 컷은 끝까지 찍어.

**EN spoken text**

> Keep the camera rolling to the end of this take.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. A calm, firm instruction to the off-screen film crew. Quiet satisfaction with a trace of weary authority. Emphasize keeping the camera rolling until the end. Land the meta joke dryly.
```

타이밍: 현재 표시 5.5초.

원문 근거: `DirectorCutPlayHUD.cpp`


### E01 · 엔딩 공통 · 용사

보이스: **Brick**

**KO spoken text**

> 준비됐어? 이제 제대로 마지막 전투를 찍을 수 있겠네.

**EN spoken text**

> Ready? Now we can finally film the final battle properly.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Hero: a grounded adult masculine voice with a clear, sturdy mid-to-low register. A confident fantasy hero who is also a fellow actor. Heroic projection in the opening challenge; relaxed collegial speech in the ending; genuine bafflement in the reveal jokes. Friendly, confident anticipation from a fellow actor ready to resume filming. Ask the opening question lightly, then express relief that the final battle can finally be filmed properly.
```

타이밍: 기존 영어 약 4.632초, 시작 0.583초.

원문 근거: `DirectorCutEnding.cpp`


### E02 · 엔딩 공통 · 드래곤

보이스: **Hades**

**KO spoken text**

> 잠깐. 나는 어떤 모습으로 나갈지 아직 안 정했어.

**EN spoken text**

> Wait. I haven't decided what I want to look like yet.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Interrupt gently but decisively. You are asserting creative control over your appearance. A thoughtful pause after the opening word; composed, slightly fussy, and dryly funny.
```

타이밍: 기존 영어 약 4.608초, 시작 5.417초.

원문 근거: `DirectorCutEnding.cpp`


### E03 · 원래 다리 엔딩 · 용사

보이스: **Brick**

**KO spoken text**

> …너 원래 그렇게 걸었어?

**EN spoken text**

> ...Have you always walked like that?

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Hero: a grounded adult masculine voice with a clear, sturdy mid-to-low register. A confident fantasy hero who is also a fellow actor. Heroic projection in the opening challenge; relaxed collegial speech in the ending; genuine bafflement in the reveal jokes. Watch the dragon’s awkward walk in silence for a brief beat. Ask with hesitant disbelief and understated concern. The question should feel spontaneous, with no big comic punchline voice.
```

타이밍: 기존 영어 약 3.144초, 시작 6.5초. 자막 6.5–9.7초.

원문 근거: `DirectorCutEnding.cpp`


### E04 · 원래 다리 엔딩 · 드래곤

보이스: **Hades**

**KO spoken text**

> 하... 애니메이션은 또 왜 이래.

**EN spoken text**

> Sigh... What's wrong with the animation now?

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Begin with a short audible weary exhale, then mutter the complaint with exhausted frustration at yet another production problem. Keep the anger low and the comedy deadpan. For English, perform the opening Sigh as an exhale rather than literally saying the word.
```

타이밍: 기존 영어 약 4.2초, 시작 10.125초. 자막 10.1–14.4초.

원문 근거: `DirectorCutEnding.cpp`


### E05 · 수레 엔딩 · 드래곤

보이스: **Hades**

**KO spoken text**

> 잠깐. 이거 브레이크는 어디—

**EN spoken text**

> Wait. Where are the brakes on this—

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Begin with puzzled concern, then let panic build as the cart accelerates. Cut the last phrase off abruptly mid-thought because you are losing control. Do not resolve the sentence or add a scream to this clip.
```

타이밍: 기존 영어 약 2.496초, 시작 0.75초. 자막 0.75–3.3초.

원문 근거: `DirectorCutEnding.cpp`


### E06 · 수레 엔딩 · 드래곤

보이스: **Hades**

**KO spoken text**

> 으아아!!!

**EN spoken text**

> Aaaah!!!

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Perform a single sustained open-vowel scream of startled panic while speeding downhill. Rise quickly into panic, sustain briefly, then finish naturally. Comic alarm, not agony; no extra words or laughter.
```

타이밍: 기존 영어 약 1.704초, 시작 약 3.292초. 자막 3.3–5.75초.

원문 근거: `DirectorCutEnding.cpp`


### E07 · 용사 다리 엔딩 · 용사

보이스: **Brick**

**KO spoken text**

> 왜 내 다리가 저기 있는거야?

**EN spoken text**

> Why are my legs over there?

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Hero: a grounded adult masculine voice with a clear, sturdy mid-to-low register. A confident fantasy hero who is also a fellow actor. Heroic projection in the opening challenge; relaxed collegial speech in the ending; genuine bafflement in the reveal jokes. Notice your own legs attached to the dragon. Start with baffled recognition, then ask with rising personal indignation. Stress my legs naturally. Surprise and disbelief, not a battle cry.
```

타이밍: 기존 영어 약 3.288초, 시작 3.5초. 현재 자막은 6.5초에 끝나므로 음성 끝과 차이 확인.

원문 근거: `DirectorCutEnding.cpp`


### Note_Wheel · 작업 메모 낭독 · 메모 낭독

보이스: **Hades**

**KO spoken text**

> 그래픽 설정의 Model Detail에 따라 바퀴 모양이 달라짐. 둥근 원본은 잘 굴러감. 각진 검수본은 황동 받침 위에서 미끄러지지 않음.

**EN spoken text**

> The wheel changes shape with Model Detail. The round master rolls freely. The angular proof holds on the brass cradle.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Read this production note as the dragon quietly reading a written clue. Clear, measured, practical delivery with a small pause between instructions. Keep every condition and comparison precise. No added explanation, discovery exclamation, or solution beyond the supplied text.
```

타이밍: 플레이어가 메모를 열었을 때 사용하는 선택 제작분. 원래는 대화 자막이 아닌 문서 텍스트.

원문 근거: `DirectorCutWallNote.cpp`


### Note_Lens · 작업 메모 낭독 · 메모 낭독

보이스: **Hades**

**KO spoken text**

> 소품은 두 조각으로 제작. 카메라에서 봤을 땐 열쇠 하나처럼 보여야 함.

**EN spoken text**

> The prop comes in two pieces. Through the lens it should look like a single key.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Read this production note as the dragon quietly reading a written clue. Clear, measured, practical delivery with a small pause between instructions. Keep every condition and comparison precise. No added explanation, discovery exclamation, or solution beyond the supplied text.
```

타이밍: 플레이어가 메모를 열었을 때 사용하는 선택 제작분. 원래는 대화 자막이 아닌 문서 텍스트.

원문 근거: `DirectorCutWallNote.cpp`


### Note_TwoTakes · 작업 메모 낭독 · 메모 낭독

보이스: **Hades**

**KO spoken text**

> 두 표시등이 한 프레임에 켜져야 함. 첫 번째 테이크는 지우지 말 것.

**EN spoken text**

> Both lamps need to show in the same frame. Keep the first take.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Read this production note as the dragon quietly reading a written clue. Clear, measured, practical delivery with a small pause between instructions. Keep every condition and comparison precise. No added explanation, discovery exclamation, or solution beyond the supplied text.
```

타이밍: 플레이어가 메모를 열었을 때 사용하는 선택 제작분. 원래는 대화 자막이 아닌 문서 텍스트.

원문 근거: `DirectorCutWallNote.cpp`


### Note_Projection · 작업 메모 낭독 · 메모 낭독

보이스: **Hades**

**KO spoken text**

> 그래픽 설정의 Resolution에 따라 같은 필름도 다르게 보인다. 작은 검수본에선 잔흠집이 묻혀 이어 붙인 자리가 더 잘 보인다.

**EN spoken text**

> The same film looks different at each Resolution setting. Fine scratches vanish on the small proof, making the splices easier to see.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Read this production note as the dragon quietly reading a written clue. Clear, measured, practical delivery with a small pause between instructions. Keep every condition and comparison precise. No added explanation, discovery exclamation, or solution beyond the supplied text.
```

타이밍: 플레이어가 메모를 열었을 때 사용하는 선택 제작분. 원래는 대화 자막이 아닌 문서 텍스트.

원문 근거: `DirectorCutWallNote.cpp`


### Note_Lighting · 작업 메모 낭독 · 메모 낭독

보이스: **Hades**

**KO spoken text**

> 파란 조명이 가장 밝다. 빨강은 초록보다 한 칸 위. 모든 조명은 켜둔다.

**EN spoken text**

> Blue gets top billing. Red sits one notch above green. Every lamp stays lit.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Read this production note as the dragon quietly reading a written clue. Clear, measured, practical delivery with a small pause between instructions. Keep every condition and comparison precise. No added explanation, discovery exclamation, or solution beyond the supplied text.
```

타이밍: 플레이어가 메모를 열었을 때 사용하는 선택 제작분. 원래는 대화 자막이 아닌 문서 텍스트.

원문 근거: `DirectorCutWallNote.cpp`


### Note_Retake · 작업 메모 낭독 · 메모 낭독

보이스: **Hades**

**KO spoken text**

> 지난 테이크에선 성벽 그림자의 윤곽이 벽에 그린 선과 딱 맞았다.

**EN spoken text**

> In the last take, the castle shadow fit the outline painted on the wall.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Read this production note as the dragon quietly reading a written clue. Clear, measured, practical delivery with a small pause between instructions. Keep every condition and comparison precise. No added explanation, discovery exclamation, or solution beyond the supplied text.
```

타이밍: 플레이어가 메모를 열었을 때 사용하는 선택 제작분. 원래는 대화 자막이 아닌 문서 텍스트.

원문 근거: `DirectorCutWallNote.cpp`


### Note_Ferry · 작업 메모 낭독 · 메모 낭독

보이스: **Hades**

**KO spoken text**

> 스위치는 배우 대신 그림자에 반응한다. 대기 신호가 남아 있으면 발판도 정지 상태.

**EN spoken text**

> The switches respond to shadows. As long as the hold signal stays lit, so does the ferry brake.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Read this production note as the dragon quietly reading a written clue. Clear, measured, practical delivery with a small pause between instructions. Keep every condition and comparison precise. No added explanation, discovery exclamation, or solution beyond the supplied text.
```

타이밍: 플레이어가 메모를 열었을 때 사용하는 선택 제작분. 원래는 대화 자막이 아닌 문서 텍스트.

원문 근거: `DirectorCutWallNote.cpp`


### Note_UpperSwitch · 작업 메모 낭독 · 메모 낭독

보이스: **Hades**

**KO spoken text**

> 위쪽 스위치의 촬영 기록은 신호가 끊겼다 돌아올 때 갱신된다.

**EN spoken text**

> The upper switch logs a new take when it sees the signal return.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Read this production note as the dragon quietly reading a written clue. Clear, measured, practical delivery with a small pause between instructions. Keep every condition and comparison precise. No added explanation, discovery exclamation, or solution beyond the supplied text.
```

타이밍: 플레이어가 메모를 열었을 때 사용하는 선택 제작분. 원래는 대화 자막이 아닌 문서 텍스트.

원문 근거: `DirectorCutWallNote.cpp`


### P_Note · 프롤로그 / 개발 메모 · 메모 낭독

보이스: **Hades**

**KO spoken text**

> 개발 메모. 최종 보스 하체 — 테스트 구역으로 이동. 현재 카메라에 잡히지 않으므로 임시 제거.

**EN spoken text**

> Development note. Final boss lower body — moved to the test area. Temporarily removed because it is outside the camera frame.

**Performance prompt**

```text
Produce one clean, isolated game dialogue performance. Speak only the supplied spoken text in the selected language. Do not read the ID, speaker label, or performance instructions aloud. Do not add words, music, sound effects, room reverb, or a second voice. Keep the character voice consistent between clips. Dragon: a deep, resonant adult masculine voice with a textured low register. A theatrical fantasy villain who is actually a practical, slightly irritable actor on a film set. Use controlled power, clear diction, conversational inner monologues, and dry comic timing. Reserve booming projection for the opening threat. Read a production memo with neutral bureaucratic seriousness. Pause after the heading and between sentences. The absurd removal of the boss’s legs is treated as routine paperwork. Do not add character reactions.
```

타이밍: 선택 제작분. 한국어는 이미지의 제목·줄바꿈을 낭독용 구두점으로 연결. 영어는 제작용 번역.

원문 근거: `BossPrologue/make_graphics.ps1`
