# 보스 프롤로그

Unreal Engine 5.8에서 `/Game/DirectorCut/Prologue/L_BossPrologue`를 열고 **Play**를 누르면 약 25초짜리 프롤로그가 자동 재생됩니다. 자동 재생 시퀀스는 `/Game/DirectorCut/Prologue/LS_BossPrologue_Cinematic`입니다.

용사는 `Withdrawing_Sword` 이후 `Crouch_Idle`로 돌아갑니다. 드래곤의 불꽃, 카메라 흔들림과 이동, 사라진 하체의 개발 메모, 하체 보관실 입구와 이동 동작, 한국어 위·영어 아래 자막 및 영어 음성이 시퀀스에 들어 있습니다.

`build_boss_prologue.py`는 같은 폴더의 `Graphics/`와 `Voice/`를 언리얼 콘텐츠로 가져와 맵과 시퀀스를 다시 만듭니다. 편집기에서 **Tools → Execute Python Script**로 실행하세요. 맵을 편집기에서 열어 둔 상태로 실행해야 저장이 완료됩니다. `make_graphics.ps1`과 `generate_voice.py`는 원본 그래픽과 음성 생성용이며, 이미 생성된 파일도 함께 보관되어 있습니다.
