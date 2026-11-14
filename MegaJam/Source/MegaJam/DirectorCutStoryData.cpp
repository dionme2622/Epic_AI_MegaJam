#include "DirectorCutStoryData.h"

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
        {1050.f, 1480.f,
            LOCTEXT("CastleWorkshopKo", "용: 커튼 너머에서 기계 소리가 나. 저쪽이 제작소인가 봐."),
            LOCTEXT("CastleWorkshopEn", "Dragon: I hear machinery past the curtain. That must be the workshop.")},
    };
    const FDirectorCutStoryCue WorkshopStory[] = {
        {-1300.f, -670.f,
            LOCTEXT("WorkshopArrivalKo", "용: 다리 운반 기록이 여기 어딘가에 있겠지. 저 바퀴부터 살펴보자."),
            LOCTEXT("WorkshopArrivalEn", "Dragon: The transfer record must be here somewhere. Let's start with that wheel.")},
        {7600.f, 8050.f,
            LOCTEXT("WorkshopReelsKo", "용: 운반 기록은 위층 편집실에 있겠군. 이 승강기를 써 보자."),
            LOCTEXT("WorkshopReelsEn", "Dragon: The transfer records must be in the editing room upstairs. Let's try the lift.")},
    };
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
}

TConstArrayView<FDirectorCutStoryCue> GetDirectorCutStoryCues(FName MapName)
{
    if (MapName == CastleMap) return MakeArrayView(CastleStory);
    if (MapName == WorkshopMap || MapName == LegacyWorkshopMap) return MakeArrayView(WorkshopStory);
    if (MapName == EditingRoomMap) return MakeArrayView(EditingRoomStory);
    if (MapName == VaultMap) return MakeArrayView(VaultStory);
    return {};
}

#undef LOCTEXT_NAMESPACE
