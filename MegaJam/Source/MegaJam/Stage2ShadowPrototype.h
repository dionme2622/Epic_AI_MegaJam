#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Stage2ShadowPrototype.generated.h"

class UStaticMeshComponent;
class USpotLightComponent;
class AStage2ShadowSpotlight;
class AStage2ShadowCrate;
class AStage2ShadowLever;
class AStage2ShadowDoor;

UCLASS(Blueprintable)
class MEGAJAM_API AStage2ShadowCrate : public AActor
{
    GENERATED_BODY()
public:
    AStage2ShadowCrate();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Mesh;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Puzzle|Crate") float RailMinX = 200.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Puzzle|Crate") float RailMaxX = 850.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Puzzle|Crate", meta=(ClampMin="0")) float MoveSpeed = 140.f;
    UFUNCTION(BlueprintCallable, Category="Puzzle|Crate") float MoveAlongRail(float Axis, float DeltaSeconds);
};

UCLASS(Blueprintable)
class MEGAJAM_API AStage2ShadowDoor : public AActor
{
    GENERATED_BODY()
public:
    AStage2ShadowDoor();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Mesh;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Puzzle|Door") float OpenHeight = 260.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Puzzle|Door") float OpenSpeed = 140.f;
    UPROPERTY(BlueprintReadOnly, Category="Puzzle|Door") bool bOpen = false;
    UFUNCTION(BlueprintCallable, Category="Puzzle|Door") void OpenDoor();
private:
    FVector ClosedPosition;
};

UCLASS(Blueprintable)
class MEGAJAM_API AStage2ShadowLever : public AActor
{
    GENERATED_BODY()
public:
    AStage2ShadowLever();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Mesh;
    UPROPERTY(BlueprintReadOnly, Category="Puzzle|Lever") bool bActivated = false;
    UFUNCTION(BlueprintCallable, Category="Puzzle|Lever") void Activate();
    UFUNCTION(BlueprintImplementableEvent, Category="Puzzle|Lever") void OnActivated();
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FStage2PlayerDetected);
UCLASS(Blueprintable)
class MEGAJAM_API AStage2ShadowSpotlight : public AActor
{
    GENERATED_BODY()
public:
    AStage2ShadowSpotlight();
    virtual void Tick(float DeltaSeconds) override;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<USceneComponent> Root;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Fixture;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<USpotLightComponent> Light;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Puzzle|Detection") float Range = 1100.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Puzzle|Detection", meta=(ClampMin="1",ClampMax="89")) float HalfAngle = 24.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Puzzle|Detection") float DetectionDelay = .7f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Puzzle|Detection") float SweepAngle = 20.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Puzzle|Detection") float SweepPeriod = 6.f;
    UPROPERTY(BlueprintReadOnly, Category="Puzzle|Detection") bool bPlayerInBeam = false;
    UPROPERTY(BlueprintReadOnly, Category="Puzzle|Detection") bool bPlayerCovered = false;
    UPROPERTY(BlueprintReadOnly, Category="Puzzle|Detection") float ExposureTime = 0.f;
    UPROPERTY(BlueprintReadWrite, Category="Puzzle|Detection") bool bDetectionEnabled = true;
    UPROPERTY(BlueprintAssignable, Category="Puzzle|Detection") FStage2PlayerDetected OnPlayerDetected;
    UFUNCTION(BlueprintPure, Category="Puzzle|Detection") bool IsPlayerCovered() const { return bPlayerCovered; }
private:
    float Clock = 0.f;
    bool bTriggered = false;
};

UCLASS(Blueprintable)
class MEGAJAM_API AStage2ShadowSectionManager : public AActor
{
    GENERATED_BODY()
public:
    AStage2ShadowSectionManager();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Puzzle|References") TObjectPtr<AStage2ShadowSpotlight> Spotlight;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Puzzle|References") TObjectPtr<AStage2ShadowSpotlight> SecondSpotlight;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Puzzle|References") TObjectPtr<AStage2ShadowCrate> Crate;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Puzzle|References") TObjectPtr<AStage2ShadowLever> Lever;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Puzzle|References") TObjectPtr<AStage2ShadowDoor> Door;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Puzzle|References") TObjectPtr<AActor> Checkpoint;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Puzzle|Interaction") float InteractionDistance = 220.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Puzzle|Interaction") float RespawnProtection = 1.5f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Puzzle|Interaction") bool bUsePrototypeKeys = true;
    UPROPERTY(BlueprintReadOnly, Category="Puzzle|State") bool bHoldingCrate = false;
    UPROPERTY(BlueprintReadOnly, Category="Puzzle|State") bool bSectionCompleted = false;
    UFUNCTION(BlueprintCallable, Category="Puzzle|Interaction") void Interact();
    UFUNCTION(BlueprintCallable, Category="Puzzle|Interaction") void ToggleShadow();
    UFUNCTION(BlueprintCallable, Category="Puzzle|Interaction") void ReleaseCrate();
    UFUNCTION(BlueprintCallable, Category="Puzzle|Interaction") void HandlePlayerDetected();
    UFUNCTION(BlueprintImplementableEvent, Category="Puzzle|Events") void OnSectionComplete();
    UFUNCTION(BlueprintImplementableEvent, Category="Puzzle|Events") void OnDetection();
private:
    float ProtectionLeft = 0.f;
};
