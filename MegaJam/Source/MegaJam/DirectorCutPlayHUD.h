#pragma once

#include "CoreMinimal.h"
#include "DirectorCutInteractionData.h"
#include "DirectorCutStoryData.h"
#include "Subsystems/WorldSubsystem.h"
#include "DirectorCutPlayHUD.generated.h"

class AStage4ShadowTheatre;
class AColorSignalPuzzle;
class AFocusPropPuzzle;
class ADirectorCutWallNote;
class APlayerController;
class APawn;
class SOverlay;
class UAudioComponent;

UCLASS()
class UDirectorCutPlayHUD : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual void OnWorldBeginPlay(UWorld& World) override;
    virtual void Deinitialize() override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;

    float ShowSubtitle(const FText& Korean, const FText& English, float Duration);
    void ClearSubtitle();

private:
    void BuildOverlay();
    ADirectorCutWallNote* UpdateWallNote(const FVector& Position, bool bCanRead, bool bInteract);

    TSharedPtr<SOverlay> Overlay;
    UPROPERTY(Transient)
    TObjectPtr<UAudioComponent> SubtitleVoice;
    TWeakObjectPtr<AStage4ShadowTheatre> FinalTheatre;
    TWeakObjectPtr<AColorSignalPuzzle> ColorConsole;
    TWeakObjectPtr<AFocusPropPuzzle> FocusPuzzle;
    TArray<TWeakObjectPtr<ADirectorCutWallNote>> WallNotes;
    TWeakObjectPtr<ADirectorCutWallNote> OpenWallNote;
    FName MapName;
    TSet<int32> PlayedStoryCues;
    FText SubtitleSpeaker;
    FText SubtitleKorean;
    FText SubtitleEnglish;
    FText WallNoteKorean;
    FText WallNoteEnglish;
    FDirectorCutPuzzleGuide Guide;
    FDirectorCutInteractionPrompt ActionPrompt;
    FText PromptKey;
    FText PromptKorean;
    FText PromptEnglish;
    FVector PromptWorldPosition = FVector::ZeroVector;
    FVector2D PromptScreenPosition = FVector2D::ZeroVector;
    float SubtitleRemaining = 0.f;
    float QueryRemaining = 0.f;
    float RecoveryElapsed = 0.f;
    bool bPromptVisible = false;
    bool bMenuOpen = false;
    bool bGuideVisible = false;

    bool bEndingShown = false;
    bool bEndingTravelStarted = false;
};
