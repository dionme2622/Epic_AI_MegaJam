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

enum class EDirectorCutWorkshopPhase : uint8
{
    Unavailable,
    Wheel,
    WheelNeedsHigh,
    WheelNeedsLow,
    Hall,
    LiftNeedsHigh,
    LiftReady,
    LiftMoving,
    Exit
};

EDirectorCutWorkshopPhase GetDirectorCutWorkshopPhase(FName MapName, UWorld& World, const FVector& Player);
bool IsDirectorCutWorkshopMenuOpen(FName MapName, UWorld& World);
void SetDirectorCutWorkshopMenuOpen(UWorld& World, bool bOpen);
bool CanChangeDirectorCutWorkshopDetail(UWorld& World);
void ApplyDirectorCutWorkshopDetail(UWorld& World, bool bHigh);
bool GetDirectorCutInteractionPrompt(FName MapName, APlayerController& Controller, FDirectorCutInteractionPrompt& Out);
