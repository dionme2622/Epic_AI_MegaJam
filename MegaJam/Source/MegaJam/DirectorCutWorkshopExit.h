#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DirectorCutWorkshopExit.generated.h"

UCLASS()
class ADirectorCutWorkshopExit : public AActor
{
    GENERATED_BODY()

public:
    ADirectorCutWorkshopExit();
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(EditInstanceOnly, Category="Transition")
    float ExitX = 9900.f;

    UPROPERTY(EditInstanceOnly, Category="Transition")
    TSoftObjectPtr<UWorld> DestinationLevel;

private:
    void TravelToDestination();
};
