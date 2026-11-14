#pragma once

#include "CoreMinimal.h"

class APlayerController;
class UWorld;

struct FDirectorCutInteractionPrompt
{
    FText Key;
    FText Korean;
    FText English;
    FVector Anchor = FVector::ZeroVector;
};

bool IsDirectorCutWorkshopMenuOpen(FName MapName, UWorld& World);
void SetDirectorCutWorkshopMenuOpen(UWorld& World, bool bOpen);
bool CanChangeDirectorCutWorkshopDetail(UWorld& World);
void ApplyDirectorCutWorkshopDetail(UWorld& World, bool bHigh);
bool GetDirectorCutInteractionPrompt(FName MapName, APlayerController& Controller, FDirectorCutInteractionPrompt& Out);
