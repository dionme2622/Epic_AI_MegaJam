#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Stage3TakePuzzle.generated.h"

class ACharacter;
class AStage2ShadowDoor;
class UPoseableMeshComponent;
class UMaterialInterface;
class UTextRenderComponent;
class SWidget;

UENUM(BlueprintType)
enum class EStage3TakePhase : uint8
{
    Idle,
    Recording,
    Playing,
    ReplayReady,
    Solved
};

UCLASS(Blueprintable)
class MEGAJAM_API AStage3TakePuzzle : public AActor
{
    GENERATED_BODY()

public:
    AStage3TakePuzzle();
    void BeginPlay() override;
    void EndPlay(EEndPlayReason::Type Reason) override;
    void Tick(float DeltaSeconds) override;

    bool CanUseCamera(const ACharacter& Character) const;
    bool CanFinishRecording(const ACharacter& Character) const;

    // Floor-level marks in this actor's local coordinates.
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Two Takes|Setup")
    FVector CameraMark = FVector(1050.f, 0.f, 0.f);

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Two Takes|Setup")
    FVector LeftMark = FVector(690.f, 0.f, 0.f);

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Two Takes|Setup")
    FVector RightMark = FVector(1420.f, 0.f, 0.f);

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Two Takes|Setup")
    TObjectPtr<AStage2ShadowDoor> ExitDoor;

    // Place the lit meshes over the unlit lamps. They are shown as the plates are pressed.
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Two Takes|Setup")
    TObjectPtr<AActor> LeftLamp;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Two Takes|Setup")
    TObjectPtr<AActor> RightLamp;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Two Takes|Setup")
    TObjectPtr<UMaterialInterface> GhostMaterial;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Two Takes|Setup", meta=(ClampMin="20"))
    float PlateHalfWidth = 85.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Two Takes|Setup", meta=(ClampMin="20"))
    float PlateHalfDepth = 72.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Two Takes|Setup", meta=(ClampMin="20"))
    float ConsoleDistance = 165.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Two Takes|Setup")
    float MinRoomX = -230.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Two Takes|Setup")
    float MaxRoomX = 2250.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Two Takes|Timing", meta=(ClampMin="4.0", ClampMax="30.0"))
    float MaxRecordingSeconds = 14.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Two Takes|Timing", meta=(ClampMin="0.1", ClampMax="3.0"))
    float RequiredOverlapSeconds = .55f;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Two Takes|State")
    EStage3TakePhase Phase = EStage3TakePhase::Idle;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Two Takes|State")
    float RecordedSeconds = 0.f;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Two Takes|State")
    bool bLeftPressed = false;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Two Takes|State")
    bool bRightPressed = false;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Two Takes|State")
    bool bCompleted = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Two Takes|State")
    TObjectPtr<UPoseableMeshComponent> GhostMesh;

private:
    struct FRecordedFrame
    {
        float Time = 0.f;
        FTransform MeshTransform;
        TArray<FTransform> Bones;
        bool bOnLeftPlate = false;
    };

    void StartRecording(ACharacter& Character);
    void SampleFrame(ACharacter& Character, bool bOnLeftPlate);
    void StartPlayback(ACharacter& Character);
    void UpdatePlayback(float DeltaSeconds, bool bPlayerOnRight);
    void RewindPlayer(ACharacter& Character) const;
    void ShowReplayFrame();
    void SetGhostVisible(bool bVisible);
    void SetPlates(bool bLeft, bool bRight);
    void SetHint(const FText& Text);
    bool IsNearCamera(const FVector& LocalPosition) const;
    bool IsOnPlate(const ACharacter& Character, const FVector& LocalPosition, const FVector& Mark) const;

    UPROPERTY()
    TObjectPtr<UTextRenderComponent> GhostLabel;

    TArray<FRecordedFrame> Frames;
    FText Hint;
    TSharedPtr<SWidget> Overlay;
    float PlateHoldDuringRecording = 0.f;
    float PlaybackSeconds = 0.f;
    float OverlapSeconds = 0.f;
    float MessageSeconds = 0.f;
    int32 PlaybackIndex = 0;
};
