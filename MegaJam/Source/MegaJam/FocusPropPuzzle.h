#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Styling/SlateColor.h"
#include "FocusPropPuzzle.generated.h"

class UCameraComponent;
class UStaticMeshComponent;
class SWidget;
class AStage2ShadowDoor;

UCLASS(Blueprintable)
class MEGAJAM_API AFocusPropPuzzle : public AActor
{
    GENERATED_BODY()
public:
    AFocusPropPuzzle();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Focus Puzzle") TObjectPtr<USceneComponent> Root;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Focus Puzzle") TObjectPtr<UStaticMeshComponent> NearPiece;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Focus Puzzle") TObjectPtr<UStaticMeshComponent> FarPiece;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Focus Puzzle") TObjectPtr<UCameraComponent> PuzzleCamera;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Focus Puzzle") TObjectPtr<AStage2ShadowDoor> ExitDoor;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Focus Puzzle") float InteractDistance = 250.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Focus Puzzle") float PieceSpeed = 100.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Focus Puzzle") float AlignmentTolerance = .006f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Focus Puzzle", meta=(ClampMin="0")) float FocusTransitionSpeed = 5.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Focus Puzzle", meta=(ClampMin="0")) float CompletionDelay = 1.25f;
    UPROPERTY(BlueprintReadOnly, Category="Focus Puzzle") bool bActive = false;
    UPROPERTY(BlueprintReadOnly, Category="Focus Puzzle") bool bNearSelected = true;
    UPROPERTY(BlueprintReadOnly, Category="Focus Puzzle") bool bSolved = false;
    UFUNCTION(BlueprintCallable, Category="Focus Puzzle") void EnterPuzzle();
    UFUNCTION(BlueprintCallable, Category="Focus Puzzle") void LeavePuzzle();
    UFUNCTION(BlueprintCallable, Category="Focus Puzzle") void SelectNear(bool bNear);
    UFUNCTION(BlueprintPure, Category="Focus Puzzle") bool IsAligned() const;
    UFUNCTION(BlueprintPure, Category="Focus Puzzle") float GetAlignmentProgress() const;
    UFUNCTION(BlueprintImplementableEvent, Category="Focus Puzzle") void OnSolved();
private:
    TWeakObjectPtr<AActor> PreviousView;
    TSharedPtr<SWidget> Overlay;
    FText GetStatusText() const;
    FText GetProgressText() const;
    FSlateColor GetProgressColor() const;
    FVector InitialNearPosition = FVector::ZeroVector;
    FVector InitialFarPosition = FVector::ZeroVector;
    float DesiredFocusDistance = 1300.f;
    float FinishTime = 0.f;
    bool bCompleting = false;
};
