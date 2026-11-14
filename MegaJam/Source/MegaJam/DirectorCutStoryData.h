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

struct FDirectorCutAreaHint
{
    float MinX;
    float MaxX;
    FText Korean;
    FText English;
};

TConstArrayView<FDirectorCutStoryCue> GetDirectorCutStoryCues(FName MapName);
TConstArrayView<FDirectorCutAreaHint> GetDirectorCutAreaHints(FName MapName);
