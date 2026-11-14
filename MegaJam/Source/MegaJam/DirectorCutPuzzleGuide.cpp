#include "DirectorCutStoryData.h"

#include "EngineUtils.h"
#include "FocusPropPuzzle.h"
#include "GameFramework/PlayerController.h"
#include "ResolutionCorridor.h"

#define LOCTEXT_NAMESPACE "DirectorCutPuzzleGuide"

bool HasDirectorCutPlayHUD(FName MapName)
{
    return MapName == TEXT("L_Stage1") || MapName == TEXT("Stage1") || MapName == TEXT("Stage2")
        || MapName == TEXT("Stage3_") || MapName == TEXT("Stage4");
}

FDirectorCutPuzzleGuide GetDirectorCutPuzzleGuide(FName MapName, APlayerController& Controller)
{
    UWorld* World = Controller.GetWorld();
    if (MapName != TEXT("Stage3_") || !World) return {};

    const FDirectorCutGuideControl Exit = {TEXT("E"), LOCTEXT("ExitKo", "나가기"), LOCTEXT("Exit", "Exit")};
    for (TActorIterator<AFocusPropPuzzle> It(World); It; ++It)
    {
        const AFocusPropPuzzle& Focus = **It;
        if (!Focus.bActive) continue;

        return {
            LOCTEXT("FocusTitleKo", "렌즈 조작"), LOCTEXT("FocusTitle", "Lens controls"),
            {
                {TEXT("1 / 2"), LOCTEXT("PiecesKo", "앞 / 뒤 조각"), LOCTEXT("Pieces", "Near / far piece")},
                {TEXT("A / D"), LOCTEXT("SlideKo", "좌우 이동"), LOCTEXT("Slide", "Slide left / right")},
                {TEXT("Shift"), LOCTEXT("FineKo", "미세 조절"), LOCTEXT("Fine", "Fine adjustment")},
                {TEXT("Enter"), LOCTEXT("ConfirmKo", "확정"), LOCTEXT("Confirm", "Confirm")},
                {TEXT("R"), LOCTEXT("ResetKo", "초기화"), LOCTEXT("Reset", "Reset")}, Exit
            }
        };
    }
    for (TActorIterator<AResolutionCorridor> It(World); It; ++It)
    {
        if (!It->bBridgeConsoleOpen) continue;

        return {
            LOCTEXT("FilmTitleKo", "검수대 조작"), LOCTEXT("FilmTitle", "Film desk controls"),
            {
                {TEXT("1 / 2"), LOCTEXT("ClipKo", "필름 선택"), LOCTEXT("Clip", "Select clip")},
                {TEXT("↑ / ↓"), LOCTEXT("ClipSlideKo", "필름 위아래 이동"), LOCTEXT("ClipSlide", "Slide clip up / down")}, Exit
            }
        };
    }
    return {};
}

#undef LOCTEXT_NAMESPACE
