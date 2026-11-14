#pragma once

#include "CoreMinimal.h"
#include "DirectorCutStoryData.h"
#include "Subsystems/WorldSubsystem.h"
#include "DirectorCutPlayHUD.generated.h"

class AStage4ShadowTheatre;
class AColorSignalPuzzle;
class AFocusPropPuzzle;
class SOverlay;

UCLASS()
class UDirectorCutPlayHUD : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual void OnWorldBeginPlay(UWorld& World) override;
    virtual void Deinitialize() override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;

    void ShowSubtitle(const FText& Korean, const FText& English, float Duration);
    void ClearSubtitle();

private:
    void BuildOverlay();

    TSharedPtr<SOverlay> Overlay;
    TWeakObjectPtr<AStage4ShadowTheatre> FinalTheatre;
    TWeakObjectPtr<AColorSignalPuzzle> ColorConsole;
    TWeakObjectPtr<AFocusPropPuzzle> FocusPuzzle;
    FName MapName;
    TSet<int32> PlayedStoryCues;
    FText SubtitleKorean;
    FText SubtitleEnglish;
    FDirectorCutPuzzleGuide Guide;
    FText PromptKey;
    FText PromptKorean;
    FText PromptEnglish;
    FVector PromptWorldPosition = FVector::ZeroVector;
    FVector2D PromptScreenPosition = FVector2D::ZeroVector;
    float SubtitleRemaining = 0.f;
    float QueryRemaining = 0.f;
    float RecoveryElapsed = 0.f;
    bool bPromptVisible = false;
    bool bHasPrompt = false;
    bool bMenuOpen = false;
    bool bGuideVisible = false;
    bool bEndingShown = false;
};
