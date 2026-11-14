#pragma once

#include "Containers/ArrayView.h"
#include "CoreMinimal.h"

struct FDirectorCutStoryCue
{
    float MinX;
    float MaxX;
    FText Korean;
    FText English;
    float Duration = 4.f;
};

struct FDirectorCutGuideControl
{
    const TCHAR* Key;
    FText Korean;
    FText English;
};

struct FDirectorCutPuzzleGuide
{
    FText TitleKorean;
    FText TitleEnglish;
    TArray<FDirectorCutGuideControl> Controls;
};

class APlayerController;

TConstArrayView<FDirectorCutStoryCue> GetDirectorCutStoryCues(FName MapName);
bool HasDirectorCutPlayHUD(FName MapName);
FDirectorCutPuzzleGuide GetDirectorCutPuzzleGuide(FName MapName, APlayerController& Controller);
