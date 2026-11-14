#pragma once

#include "CoreMinimal.h"

class APlayerController;

struct FDirectorCutInteractionPrompt
{
    FText Key;
    FText Korean;
    FText English;
    FVector Anchor = FVector::ZeroVector;
};

bool GetDirectorCutInteractionPrompt(FName MapName, APlayerController& Controller, FDirectorCutInteractionPrompt& Out);
