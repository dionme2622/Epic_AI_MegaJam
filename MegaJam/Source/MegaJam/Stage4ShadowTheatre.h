#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Stage4ShadowTheatre.generated.h"

class ADirectorCutDragon;
class AStage2ShadowDoor;
class AStage4ShadowStandIn;
class UMaterialInterface;
class UPointLightComponent;
class USpotLightComponent;
class USoundBase;
class UStaticMeshComponent;
class SWidget;
struct FDirectorCutInteractionPrompt;

UCLASS(Blueprintable)
class MEGAJAM_API AStage4ShadowTheatre : public AActor
{
    GENERATED_BODY()

public:
    AStage4ShadowTheatre();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    bool GetInteractionPrompt(const ADirectorCutDragon& Dragon, FDirectorCutInteractionPrompt& Out) const;

    UPROPERTY(EditInstanceOnly, Category="Theatre|Connections")
    TObjectPtr<AStage2ShadowDoor> EntranceDoor;

    UPROPERTY(EditInstanceOnly, Category="Theatre|Connections")
    TObjectPtr<AStage4ShadowStandIn> StandInPuzzle;
    UPROPERTY(EditInstanceOnly, Category="Theatre|Connections")
    FVector ExhibitOffset = FVector::ZeroVector;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Theatre|Rig")
    TObjectPtr<UStaticMeshComponent> WestRig;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Theatre|Rig")
    TObjectPtr<UStaticMeshComponent> EastRig;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Theatre|Rig")
    TObjectPtr<UStaticMeshComponent> WestMarker;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Theatre|Rig")
    TObjectPtr<UStaticMeshComponent> EastMarker;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Theatre|Rig")
    TObjectPtr<UStaticMeshComponent> Glass;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Theatre|Rig")
    TObjectPtr<UStaticMeshComponent> Exhibit;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Theatre|Rig")
    TObjectPtr<UStaticMeshComponent> WestGuide;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Theatre|Rig")
    TObjectPtr<UStaticMeshComponent> EastGuide;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Theatre|Rig")
    TObjectPtr<UPointLightComponent> DisplayLight;

    UPROPERTY(EditAnywhere, Category="Theatre|Sound")
    TObjectPtr<USoundBase> RailCue;
    UPROPERTY(EditAnywhere, Category="Theatre|Sound")
    TObjectPtr<USoundBase> RecoveryCue;
    UPROPERTY(EditAnywhere, Category="Theatre|Costume")
    TObjectPtr<UStaticMesh> KnightGreave;
    UPROPERTY(EditInstanceOnly, Category="Theatre|Retake")
    TObjectPtr<USpotLightComponent> WestLamp;
    UPROPERTY(EditInstanceOnly, Category="Theatre|Retake")
    TObjectPtr<USpotLightComponent> EastLamp;
    UPROPERTY(EditInstanceOnly, Category="Theatre|Retake")
    TArray<TObjectPtr<UStaticMeshComponent>> DeckScenery;
    UPROPERTY(EditInstanceOnly, Category="Theatre|Retake")
    TArray<TObjectPtr<UStaticMeshComponent>> DeckCollision;
    UPROPERTY(EditAnywhere, Category="Theatre|Retake")
    TObjectPtr<UMaterialInterface> PreviewMaterial;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Theatre|Progress")
    int32 Checkpoint = 0;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Theatre|Progress")
    bool bRecovered = false;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Theatre|Progress")
    int32 ResetCount = 0;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Theatre|Progress")
    int32 WestCut = INDEX_NONE;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Theatre|Progress")
    int32 EastCut = INDEX_NONE;

private:
    struct FRetake
    {
        int32 Angle = INDEX_NONE;
        float CurrentAngle = .5f;
        int32 Cue = INDEX_NONE;
    };

    void InitializeDecks(UStaticMesh* Cube);
    void InitializeCues(UStaticMesh* Cube);
    void UpdateLanes(float DeltaSeconds, int32 Station, bool bShadows);
    void UpdateLamp(FRetake& Retake, USpotLightComponent* Lamp, UStaticMeshComponent& Rig,
        TObjectPtr<UStaticMeshComponent>& Projection, const TCHAR* ProjectionName, bool bWest, bool bShadows, float DeltaSeconds);
    void HandleControls(ADirectorCutDragon& Dragon, int32 Station, bool bShadows);
    void UpdatePrompt(float PositionX, int32 Station, bool bShadows);
    void UpdateDecks(float DeltaSeconds, uint32 Preview);
    void UpdateProjection(TObjectPtr<UStaticMeshComponent>& Projection, UStaticMeshComponent& Rig, const TCHAR* ComponentName,
        const FVector& SourcePosition, bool bShadows);
    void SetCheckpoint(ADirectorCutDragon& Dragon, int32 Index);
    void ReturnToMark(ADirectorCutDragon& Dragon);
    void UpdateCostume(ADirectorCutDragon& Dragon, bool bUseCostume);
    void StartRecovery(ADirectorCutDragon& Dragon);
    void UpdateRecovery(float DeltaSeconds);
    virtual void OnConstruction(const FTransform& Transform) override;

    UPROPERTY(Transient)
    TArray<TObjectPtr<UStaticMeshComponent>> Boots;
    UPROPERTY(EditAnywhere, Category="Theatre|Projection")
    TObjectPtr<UMaterialInterface> SilhouetteMaterial;
    UPROPERTY(Transient)
    TObjectPtr<UStaticMeshComponent> WestProjection;
    UPROPERTY(Transient)
    TObjectPtr<UStaticMeshComponent> EastProjection;
    UPROPERTY(Transient)
    TArray<TObjectPtr<UStaticMeshComponent>> PreviewOutlines;
    UPROPERTY(Transient)
    TArray<TObjectPtr<UStaticMeshComponent>> WorkMarks;
    UPROPERTY(Transient)
    TArray<TObjectPtr<UStaticMeshComponent>> AngleCues;
    UPROPERTY(Transient)
    TArray<TObjectPtr<UStaticMeshComponent>> CueIndicators;
    FRetake WestRetake;
    FRetake EastRetake;
    TArray<FVector> DeckRestPositions;
    TArray<float> DeckOpenness;
    TSharedPtr<SWidget> Overlay;
    FText Prompt;
    FText Heading;
    TWeakObjectPtr<ADirectorCutDragon> CostumeDragon;
    TWeakObjectPtr<APlayerController> RecoveryController;
    bool bCostumeApplied = false;
    float ResetFlash = 0.f;
    float CutFlash = 0.f;
    float InputHintTime = 0.f;
    FText InputHint;
    float RecoveryPositionX = 0.f;
    float RecoveryFloorZ = 0.f;
    float RecoveryTime = -1.f;
    float FinishMessage = 0.f;
};
