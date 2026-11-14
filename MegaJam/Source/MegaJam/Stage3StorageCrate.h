#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TimerManager.h"
#include "Stage3StorageCrate.generated.h"

class APlayerController;
class AResolutionCorridor;
class USceneComponent;
class UStaticMeshComponent;
class UTextRenderComponent;

UCLASS(Blueprintable)
class MEGAJAM_API AStage3StorageCrate : public AActor
{
    GENERATED_BODY()

public:
    AStage3StorageCrate();
    virtual void BeginPlay() override;
    virtual void EndPlay(EEndPlayReason::Type Reason) override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Storage")
    TObjectPtr<USceneComponent> Root;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Storage")
    TObjectPtr<USceneComponent> LidPivot;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Storage")
    TObjectPtr<UTextRenderComponent> Label;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Storage")
    TObjectPtr<AResolutionCorridor> Corridor;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Storage")
    float InteractionDistance = 200.f;
    UPROPERTY(EditInstanceOnly, BlueprintReadOnly, Category="Storage|Transition")
    TSoftObjectPtr<UWorld> DestinationLevel;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Storage")
    bool bOpened = false;

private:
    void BeginTransition(APlayerController& Controller);
    void ShowTransferNotice();
    void FadeOut();
    void LoadDestination();

    float OpenAmount = 0.f;
    FTimerHandle TransitionTimer;
    TWeakObjectPtr<APlayerController> TransitionController;
};
