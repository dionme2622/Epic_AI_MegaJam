#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DirectorCutWorkshopGate.generated.h"

class FBoolProperty;
class ADirectorCutDragon;
class UAudioComponent;
class USoundBase;

UCLASS()
class ADirectorCutWorkshopGate : public AActor
{
    GENERATED_BODY()

public:
    ADirectorCutWorkshopGate();
    virtual void Tick(float DeltaSeconds) override;

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(EditInstanceOnly, Category="Workshop Gate")
    TObjectPtr<AActor> WorkshopDirector;

    UPROPERTY(EditInstanceOnly, Category="Workshop Gate")
    TObjectPtr<AActor> Wheel;

    UPROPERTY(EditInstanceOnly, Category="Workshop Gate")
    TObjectPtr<AActor> GateVisual;

    UPROPERTY(EditInstanceOnly, Category="Workshop Gate")
    TObjectPtr<AActor> GateBarrier;

    UPROPERTY(EditInstanceOnly, Category="Workshop Gate|Sound")
    TObjectPtr<USoundBase> WheelRoll;

    UPROPERTY(EditInstanceOnly, Category="Workshop Gate|Sound")
    TObjectPtr<USoundBase> GateRise;

    UPROPERTY(EditInstanceOnly, Category="Workshop Gate|Sound")
    TObjectPtr<USoundBase> GateLatch;

    UPROPERTY()
    TObjectPtr<UAudioComponent> WheelAudio;

    UPROPERTY()
    TObjectPtr<UAudioComponent> GateAudio;

    const FBoolProperty* WheelSolvedProperty = nullptr;
    TWeakObjectPtr<ADirectorCutDragon> FramedDragon;
    FVector ClosedGatePosition = FVector::ZeroVector;
    double PreviousWheelX = 0.;
    float OpeningElapsed = 0.f;
    int32 PreviousWheelDirection = 0;
    bool bOpeningStarted = false;
};
