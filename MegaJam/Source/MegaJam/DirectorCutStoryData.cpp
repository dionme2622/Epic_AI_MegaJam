#include "DirectorCutStoryData.h"

#include "Containers/StaticArray.h"

#define LOCTEXT_NAMESPACE "DirectorCutStoryData"

namespace
{
    const FName CastleMap(TEXT("L_Stage1"));
    const FName WorkshopMap(TEXT("Stage2"));
    const FName LegacyWorkshopMap(TEXT("Stage1"));
    const FName EditingRoomMap(TEXT("Stage3_"));
    const FName VaultMap(TEXT("Stage4"));

    // The prologue's dialogue is authored as two-line cards in its Level Sequence.
    const FDirectorCutStoryCue CastleStory[] = {
        {-530.f, -275.f,
            LOCTEXT("CastleResolveKo", "용: 다리는 테스트 구역으로 옮겼다고? 그럼 내가 직접 찾으러 가지."),
            LOCTEXT("CastleResolveEn", "Dragon: They moved my legs to the test area? I'll go find them myself.")},
        {1080.f, 1340.f,
            LOCTEXT("CastleWorkshopKo", "용: 커튼 너머에서 기계 소리가 나. 저쪽이 제작소인가 봐."),
            LOCTEXT("CastleWorkshopEn", "Dragon: I hear machinery past the curtain. That must be the workshop.")},
    };
    const FDirectorCutAreaHint CastleHints[] = {
        {-1500.f, 600.f,
            LOCTEXT("CastleMoveKo", "A / D 또는 ← / →로 이동하세요."),
            LOCTEXT("CastleMoveEn", "Move with A / D or the left and right arrow keys.")},
        {600.f, 1700.f,
            LOCTEXT("CastleExitKo", "횃불을 따라 오른쪽 끝의 제작소 입구로 가세요."),
            LOCTEXT("CastleExitEn", "Follow the torches to the workshop entrance on the right.")},
    };

    const FDirectorCutStoryCue WorkshopStory[] = {
        {-1300.f, -670.f,
            LOCTEXT("WorkshopArrivalKo", "용: 작업용 휠체어라니. 덕분에 여기선 좀 빨리 움직일 수 있겠어."),
            LOCTEXT("WorkshopArrivalEn", "Dragon: A workshop wheelchair. I can get around a little faster now.")},
        {7600.f, 8050.f,
            LOCTEXT("WorkshopReelsKo", "용: 운반 기록은 위층 편집실에 있겠군. 이 승강기를 써 보자."),
            LOCTEXT("WorkshopReelsEn", "Dragon: The transfer records must be in the editing room upstairs. Let's try the lift.")},
    };
    const FDirectorCutAreaHint WorkshopHints[] = {
        {-650.f, 1640.f,
            LOCTEXT("WorkshopWheelKo", "바퀴 가까이에서 E로 밀어 황동 표식 사이에 놓으세요. 모델 디테일은 낮음이어야 합니다."),
            LOCTEXT("WorkshopWheelEn", "Press E near the wheel to push it between the brass marks with model detail set to Low.")},
        {1640.f, 8260.f,
            LOCTEXT("WorkshopPathKo", "제작소 오른쪽의 톱니 승강장에서 위층으로 올라갈 수 있습니다."),
            LOCTEXT("WorkshopPathEn", "The gear lift on the right leads upstairs.")},
        {8260.f, 9010.f,
            LOCTEXT("WorkshopLiftKo", "승강기 중앙에 올라 모델 품질을 높음으로 바꿔 톱니를 맞물리세요."),
            LOCTEXT("WorkshopLiftEn", "Stand at the center of the lift and set model quality to High to engage the gears.")},
        {9010.f, 10000.f,
            LOCTEXT("WorkshopExitKo", "위층에 도착하면 오른쪽 문으로 나가세요."),
            LOCTEXT("WorkshopExitEn", "Once upstairs, take the door on the right.")},
    };
    const TStaticArray<FDirectorCutAreaHint, UE_ARRAY_COUNT(WorkshopHints)> LegacyWorkshopHints = []
    {
        TStaticArray<FDirectorCutAreaHint, UE_ARRAY_COUNT(WorkshopHints)> Hints;
        for (int32 Index = 0; Index < UE_ARRAY_COUNT(WorkshopHints); ++Index)
        {
            Hints[Index] = WorkshopHints[Index];
        }
        Hints[0].Korean = LOCTEXT("LegacyWheelKo", "모델 디테일을 높이면 바퀴가 굴러갑니다. 황동 표식 사이에서 낮음으로 바꿔 멈추세요.");
        Hints[0].English = LOCTEXT("LegacyWheelEn", "High model detail rolls the wheel. Switch to Low between the brass marks to stop it.");
        return Hints;
    }();

    const FDirectorCutStoryCue EditingRoomStory[] = {
        {-140.f, 350.f,
            LOCTEXT("EditingArrivalKo", "용: 여기가 편집실이군. 운반 기록을 따라 내 다리가 든 상자를 찾자."),
            LOCTEXT("EditingArrivalEn", "Dragon: This is the editing room. I'll follow the transfer record to my crate.")},
        {1730.f, 2150.f,
            LOCTEXT("EditingTakeKo", "용: 두 자리를 동시에 밟으라고? 첫 번째 테이크의 내가 남아 있다면 되겠어."),
            LOCTEXT("EditingTakeEn", "Dragon: Two marks at once? My first take could cover one of them.")},
        {4730.f, 5120.f,
            LOCTEXT("EditingBridgeKo", "용: 필름이 끊긴 곳에서 다리도 끊겼네. 영사막부터 봐야겠어."),
            LOCTEXT("EditingBridgeEn", "Dragon: The bridge breaks where the film does. Let's check the screen.")},
        {6550.f, 6770.f,
            LOCTEXT("EditingCrateKo", "용: 운반 기록에 나온 상자야. 드디어 찾았네."),
            LOCTEXT("EditingCrateEn", "Dragon: That's the crate from the transfer record. I finally found it.")},
    };
    const FDirectorCutAreaHint EditingRoomHints[] = {
        {-320.f, 1150.f,
            LOCTEXT("EditingFocusKo", "앞뒤 열쇠 조각에 번갈아 초점을 맞추고, 카메라 안에서 두 조각을 겹치세요."),
            LOCTEXT("EditingFocusEn", "Focus on each key piece in turn and line them up in the camera.")},
        {1830.f, 4210.f,
            LOCTEXT("EditingTakeHintKo", "첫 테이크는 왼쪽 발판에서 잠시 머무르세요. 재생 중에는 오른쪽 발판을 밟으세요."),
            LOCTEXT("EditingTakeHintEn", "Hold the left plate in Take 1. During playback, stand on the right plate.")},
        {5090.f, 6430.f,
            LOCTEXT("EditingBridgeHintKo", "설정에서 해상도를 낮추고, 영사막의 선이 이어지도록 두 필름 조각을 움직이세요."),
            LOCTEXT("EditingBridgeHintEn", "Lower the resolution in Settings, then move both film clips to connect the line.")},
        {6500.f, 7100.f,
            LOCTEXT("EditingCrateHintKo", "작업등 아래의 운반 상자를 확인하세요."),
            LOCTEXT("EditingCrateHintEn", "Check the transport crate under the work light.")},
    };

    const FDirectorCutStoryCue VaultStory[] = {
        {-280.f, 220.f,
            LOCTEXT("VaultArrivalKo", "용: 진짜 다리는 이 보관소에 있어. 조명 제어반부터 살펴보자."),
            LOCTEXT("VaultArrivalEn", "Dragon: My legs are in this vault. Let's check the lighting console.")},
        {1320.f, 1635.f,
            LOCTEXT("VaultRetakeKo", "용: 빛을 돌리니 무대가 달라져. 제대로 맞춘 장면을 고정하면 건널 수 있겠어."),
            LOCTEXT("VaultRetakeEn", "Dragon: The stage changes when I aim the lamp. If I lock in the right shot, I can cross.")},
        {4760.f, 4910.f,
            LOCTEXT("VaultStandInKo", "용: 저 벽의 스위치에는 손이 안 닿아. 내 그림자라면 닿을지도 몰라."),
            LOCTEXT("VaultStandInEn", "Dragon: I can't reach that wall switch. Maybe my shadow can.")},
        {6660.f, 6810.f,
            LOCTEXT("VaultExhibitKo", "용: 저 유리 보관함 안에 내 다리가 있어. 이번엔 진짜야."),
            LOCTEXT("VaultExhibitEn", "Dragon: My legs are inside that glass case. This time they're real.")},
    };
    const FDirectorCutAreaHint VaultHints[] = {
        {-520.f, 1150.f,
            LOCTEXT("VaultLightsKo", "파란빛이 가장 밝습니다. 빨간빛은 초록빛보다 한 단계 밝고, 꺼진 조명은 없습니다."),
            LOCTEXT("VaultLightsEn", "Blue is brightest. Red is one step above green, and no light is off.")},
        {1320.f, 4700.f,
            LOCTEXT("VaultRetakeHintKo", "그림자를 높음으로 바꾸고, 조명을 돌려 벽의 황동 표식에 그림자를 맞추세요."),
            LOCTEXT("VaultRetakeHintEn", "Set Shadows to High and aim the lamp until the shadow lines up with a brass mark.")},
        {4830.f, 5680.f,
            LOCTEXT("VaultFerryKo", "황동 표식 위에 서서 그림자로 발판을 부르세요. 올라탄 뒤 그림자를 끄면 이동합니다."),
            LOCTEXT("VaultFerryEn", "Stand on the brass mark to call the ferry with your shadow. Board it, then turn Shadows off.")},
        {5680.f, 6400.f,
            LOCTEXT("VaultSwitchesKo", "낮은 스위치로 발판을 올린 뒤, 높은 표식에서 그림자를 껐다 켜 다리를 고정하세요."),
            LOCTEXT("VaultSwitchesEn", "Raise the platform with the low switch. At the raised mark, toggle Shadows off and on to lock the bridge.")},
        {6460.f, 7120.f,
            LOCTEXT("VaultExhibitHintKo", "유리 보관함으로 가서 드래곤의 다리를 되찾으세요."),
            LOCTEXT("VaultExhibitHintEn", "Go to the glass case to reclaim the dragon's legs.")},
    };
}

TConstArrayView<FDirectorCutStoryCue> GetDirectorCutStoryCues(FName MapName)
{
    if (MapName == CastleMap) return MakeArrayView(CastleStory);
    if (MapName == WorkshopMap || MapName == LegacyWorkshopMap) return MakeArrayView(WorkshopStory);
    if (MapName == EditingRoomMap) return MakeArrayView(EditingRoomStory);
    if (MapName == VaultMap) return MakeArrayView(VaultStory);
    return {};
}

TConstArrayView<FDirectorCutAreaHint> GetDirectorCutAreaHints(FName MapName)
{
    if (MapName == CastleMap) return MakeArrayView(CastleHints);
    if (MapName == WorkshopMap) return MakeArrayView(WorkshopHints);
    if (MapName == LegacyWorkshopMap) return MakeArrayView(LegacyWorkshopHints.GetData(), LegacyWorkshopHints.Num());
    if (MapName == EditingRoomMap) return MakeArrayView(EditingRoomHints);
    if (MapName == VaultMap) return MakeArrayView(VaultHints);
    return {};
}

#undef LOCTEXT_NAMESPACE
