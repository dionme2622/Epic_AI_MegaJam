# HeroicKnight 정리·리텍스처·리깅

제공된 FBX와 색상 PNG를 원본으로 사용해 로컬 Blender 5.3 및 Unreal Engine 5.8에서 작업했습니다. Tripo 서비스의 UV, 텍스처, 리깅, 애니메이션 기능은 사용하지 않았습니다.

## 열어 볼 파일

| 파일 | 내용 |
|---|---|
| `HeroicKnight_Clean_Rigged.blend` | 수정 가능한 최종 메시, PBR 재질, 24본 리그, 대기 동작 |
| `HeroicKnight_Clean_Rigged.fbx` | Unreal용 스켈레탈 메시와 2초 애니메이션, 색상 텍스처 포함 |
| `CleanUV_BaseColor.png` | 새 UV에 베이크하고 색을 정돈한 4096² BaseColor |
| `CleanUV_ORM.png` | R=AO, G=Roughness, B=Metallic인 4096² 맵 |
| `HeroicKnight_Clean_Idle.gif` | 최종 2초 반복 동작 미리보기 |
| `CleanUV_Preview.png`, `HeroicKnight_Clean_BendTest.png` | 텍스처 및 관절 굽힘 검사 렌더 |

Unreal 에셋은 `/Game/Assets/HeroicKnight_Clean`에 있으며, `L_HeroicKnight_Clean_Test` 맵에서 스켈레탈 메시와 반복 대기 동작을 확인할 수 있습니다.

## 검증

- UV 아일랜드 980개 → 238개. 접힌 UV 면 0개, 1024² 래스터 검사에서 겹침 0픽셀.
- 메시 2,524정점·5,100삼각형. Blender에서 24본을 직접 배치하고 스킨 웨이트를 작성했습니다. 미할당 정점 0개, 정점당 최대 4개 영향, 웨이트 합 약 1.0.
- 30fps, 1~61프레임의 2초 반복 동작. 시작·끝 정점 위치 차이 0m. 어깨·팔꿈치·무릎·망토 굽힘 렌더와 FBX 재가져오기를 확인했습니다.
- Unreal 5.8 재가져오기에서 신장 173.83cm, 2.0초 애니메이션, 스켈레톤 일치, BaseColor/ORM 재질 연결, 물리 에셋 호환성 및 테스트 맵 저장을 확인했습니다.

세부 수치는 `CleanUV_report.json`, `rig_validation.json`, `unreal_import_report.json`, `unreal_validation.json`에 있습니다.

## 재생성

`uv_retexture.py`는 Blender 5.3의 Python에 `xatlas==0.0.11`이 필요합니다. 이 스크립트가 `CleanUV_Knight.blend`와 4K 맵을 만듭니다. 이어서 `rig_animation.py`를 Blender 백그라운드 모드로 실행하면 최종 `.blend`, `.fbx`, 미리보기가 갱신됩니다. `import_unreal.py`, `create_unreal_test_level.py`, `verify_unreal.py`는 UE 5.8 Python Script Plugin에서 순서대로 실행합니다.
