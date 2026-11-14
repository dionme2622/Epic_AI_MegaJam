#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DirectorCutGraphics.h"
#include "ResolutionCorridor.generated.h"

class UStaticMeshComponent;
class UStaticMesh;
class UMaterialInterface;
class AStage2ShadowDoor;
class APlayerController;
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
    bool CanOpenBridgeConsole() const;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor") TArray<TObjectPtr<AActor>> GuidanceArrows;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor") TObjectPtr<AStage2ShadowDoor> ExitDoor;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Resolution Corridor", meta=(ClampMin="0.1")) float SinkDuration = 1.2f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Resolution Corridor", meta=(ClampMin="0")) float SinkDistance = 85.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Resolution Corridor") float FallResetZ = -250.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Resolution Corridor|Integration", meta=(ClampMin="0")) float HideOverlayBeyondX = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Resolution Corridor|Integration") bool bRestrictOverlayStart = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Resolution Corridor|Integration") float ShowOverlayFromOffsetX = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Resolution Corridor|Integration") bool bUseLocalCheckpoint = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Resolution Corridor|Integration", meta=(EditCondition="bUseLocalCheckpoint")) FVector LocalCheckpointOffset = FVector(-400.f, 0.f, 92.f);
    // Optional side-view variant. Each station offers three numbered choices,
    // followed by one physical tile. Values are 1, 2, or 3.
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Station Puzzle") bool bUseStationChoices = false;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Station Puzzle", meta=(EditCondition="bUseStationChoices"))
    TArray<int32> StationAnswers = {1, 2, 3};
    // Relative to this controller. Each point is the safe floor before that station.
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Station Puzzle", meta=(EditCondition="bUseStationChoices"))
    TArray<FVector> StationCheckpointOffsets;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Station Puzzle", meta=(EditCondition="bUseStationChoices", ClampMin="20"))
    float StationInteractionDistance = 200.f;
    // Three separate physical reel stations must be activated in the decoded order.
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Reel Hunt") bool bUseReelHunt = false;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Reel Hunt", meta=(EditCondition="bUseReelHunt"))
    TArray<TObjectPtr<AActor>> ReelStations;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Reel Hunt", meta=(EditCondition="bUseReelHunt"))
    TArray<int32> ReelSequence = {2, 1, 3};
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Reel Hunt", meta=(EditCondition="bUseReelHunt", ClampMin="30"))
    float ReelInteractionDistance = 210.f;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Projected Bridge")
    bool bUseProjectedBridge = false;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Projected Bridge")
    TObjectPtr<AActor> BridgeConsole;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Projected Bridge")
    TObjectPtr<AActor> ProjectionScreen;
    // Place both platforms at their finished elevation before assigning them here.
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Projected Bridge")
    TArray<TObjectPtr<AActor>> BridgePlatforms;
    // Optional props at their finished positions on the console, in the same order.
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Projected Bridge")
    TArray<TObjectPtr<AActor>> BridgeClipActors;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Projected Bridge")
    TArray<int32> InitialBridgeNotches = {1, -2};
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Projected Bridge", meta=(ClampMin="30"))
    float BridgeNotchHeight = 85.f;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Projected Bridge", meta=(ClampMin="40"))
    float BridgeInteractionDistance = 100.f;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Projected Bridge")
    TObjectPtr<UMaterialInterface> ProjectionLineMaterial;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Projected Bridge")
    TObjectPtr<UMaterialInterface> ProjectionSelectedMaterial;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Resolution Corridor|Projected Bridge")
    TObjectPtr<UMaterialInterface> ProjectionScratchMaterial;
    UPROPERTY(BlueprintReadOnly, Category="Resolution Corridor|Projected Bridge")
    TArray<int32> BridgeNotches;
    UPROPERTY(BlueprintReadOnly, Category="Resolution Corridor|Projected Bridge")
    bool bProjectionReadable = false;
    UPROPERTY(BlueprintReadOnly, Category="Resolution Corridor|Projected Bridge")
    bool bBridgeConsoleOpen = false;
    UPROPERTY(BlueprintReadOnly, Category="Resolution Corridor|Station Puzzle") int32 SelectedChoice = 0;
    UPROPERTY(BlueprintReadOnly, Category="Resolution Corridor|Station Puzzle") bool bChoiceConfirmed = false;
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
    void InitializeProjectedBridge();
    void TickProjectedBridge(float DeltaSeconds);
    void SetBridgeConsoleOpen(bool bOpen);
    void BuildProjection();
    void UpdateProjection();
    bool IsAtBridgeConsole() const;
    FText StatusText() const;
    TWeakObjectPtr<AResolutionCorridorTile> FailingTile;
    TWeakObjectPtr<APawn> Player;
    TSharedPtr<SWidget> Overlay;
    FVector SpawnLocation = FVector::ZeroVector;
    float FailureElapsed = 0.f;
    bool bMovementLocked = false;
    bool bCheckpointActivated = false;
    float ReelMistakeTime = 0.f;
    UPROPERTY() TObjectPtr<UStaticMesh> ProjectionCube;
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> ProjectionRoute;
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> ProjectionScratches;
    FVector BridgePlatformOrigins[2];
    FVector BridgeClipOrigins[2];
    float BridgeCurrentOffsets[2] = {0.f, 0.f};
    int32 ActiveBridgeClip = 0;
    bool bBridgeConfigured = false;
    bool bBridgeAdjusted = false;
    TWeakObjectPtr<APlayerController> BridgeInputController;
};
