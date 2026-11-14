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
        {-420.f, 390.f,
            LOCTEXT("CastleChairKo", "용: 저 의자엔 바퀴가 달렸네. 앞발만 있어도 움직일 수 있겠어."),
            LOCTEXT("CastleChairEn", "Dragon: That chair has wheels. I could move it with just my front paws.")},
        {1050.f, 1620.f,
            LOCTEXT("CastleWorkshopKo", "용: 커튼 너머에서 기계 소리가 나. 저쪽이 제작소인가 봐."),
            LOCTEXT("CastleWorkshopEn", "Dragon: I hear machinery past the curtain. That must be the workshop.")},
    };
    const FDirectorCutStoryCue WorkshopStory[] = {
        {-1300.f, -670.f,
            LOCTEXT("WorkshopArrivalKo", "용: 다리 운반 기록이 여기 어딘가에 있겠지."),
            LOCTEXT("WorkshopArrivalEn", "Dragon: The transfer record must be here somewhere.")},
        {7500.f, 8890.f,
            LOCTEXT("WorkshopLiftKo", "용: 톱니끼리 닿지도 않네. 원래 모형에는 저 틈에도 톱니가 있었을 텐데."),
            LOCTEXT("WorkshopLiftEn", "Dragon: Those teeth don't even touch. The original gear must have had teeth in those gaps.")},
        {9080.f, 9900.f,
            LOCTEXT("WorkshopLegsKo", "용: 용사의 다리잖아! 내 다리를 찾을 때까지만 빌려 쓰자."),
            LOCTEXT("WorkshopLegsEn", "Dragon: The hero’s legs! I’ll borrow them until I find mine.")},
    };
    const FDirectorCutStoryCue EditingRoomStory[] = {
        {-140.f, 350.f,
            LOCTEXT("EditingArrivalKo", "용: 여기가 편집실이군. 운반 기록을 따라 내 다리가 든 상자를 찾자."),
            LOCTEXT("EditingArrivalEn", "Dragon: This is the editing room. I'll follow the transfer record to my crate.")},
        {6550.f, 6770.f,
            LOCTEXT("EditingCrateKo", "용: 운반 기록에 나온 상자야. 드디어 찾았네."),
            LOCTEXT("EditingCrateEn", "Dragon: That's the crate from the transfer record. I finally found it.")},
    };
    const FDirectorCutStoryCue VaultStory[] = {
        {-280.f, 220.f,
            LOCTEXT("VaultArrivalKo", "용: 진짜 다리는 이 보관소에 있어. 조명대 오른쪽에 메모지가 붙어 있네."),
            LOCTEXT("VaultArrivalEn", "Dragon: My legs are in this vault. There's a note to the right of the lighting console.")},
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
