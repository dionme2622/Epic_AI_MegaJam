#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DirectorCutGraphics.h"
#include "ResolutionCorridor.generated.h"

class UStaticMeshComponent;
class AStage2ShadowDoor;
class SWidget;

UCLASS(Blueprintable)
class MEGAJAM_API AResolutionCorridorTile : public AActor
{
    GENERATED_BODY()
public:
    AResolutionCorridorTile();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Resolution Corridor") TObjectPtr<UStaticMeshComponent> Mesh;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor") bool bSafe = false;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor", meta=(ClampMin="0", ClampMax="2")) int32 SafeOrder = 0;
    FVector InitialLocation;
};

UCLASS(Blueprintable)
class MEGAJAM_API AResolutionCorridor : public AActor
{
    GENERATED_BODY()
public:
    AResolutionCorridor();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void Tick(float DeltaSeconds) override;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor") TArray<TObjectPtr<AActor>> GuidanceArrows;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor") TObjectPtr<AStage2ShadowDoor> ExitDoor;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Resolution Corridor", meta=(ClampMin="0.1")) float SinkDuration = 1.2f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Resolution Corridor", meta=(ClampMin="0")) float SinkDistance = 85.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Resolution Corridor") float FallResetZ = -250.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Resolution Corridor|Integration", meta=(ClampMin="0")) float HideOverlayBeyondX = 0.f;
    UPROPERTY(BlueprintReadOnly, Category="Resolution Corridor") int32 Progress = 0;
    UPROPERTY(BlueprintReadOnly, Category="Resolution Corridor") bool bCompleted = false;
    UPROPERTY(BlueprintReadOnly, Category="Resolution Corridor") bool bFailing = false;
    UFUNCTION(BlueprintImplementableEvent, Category="Resolution Corridor") void OnCorridorCompleted();
    UFUNCTION(BlueprintImplementableEvent, Category="Resolution Corridor") void OnWrongTile();
private:
    UFUNCTION() void GraphicsChanged(EDirectorCutGraphicsOption Option, bool bHigh);
    void UpdateGuidance(bool bHigh);
    void BeginFailure(AResolutionCorridorTile* Tile);
    void ResetPlayer();
    FText StatusText() const;
    TWeakObjectPtr<AResolutionCorridorTile> FailingTile;
    TWeakObjectPtr<APawn> Player;
    TSharedPtr<SWidget> Overlay;
    FVector SpawnLocation = FVector::ZeroVector;
    float FailureElapsed = 0.f;
    bool bMovementLocked = false;
};
