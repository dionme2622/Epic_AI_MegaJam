#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DirectorCutSequenceTransition.generated.h"

class ALevelSequenceActor;
class UWorld;

UCLASS()
class ADirectorCutSequenceTransition : public AActor
{
    GENERATED_BODY()

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(EditInstanceOnly, Category="Transition")
    TObjectPtr<ALevelSequenceActor> SequenceActor;

    UPROPERTY(EditInstanceOnly, Category="Transition")
    TSoftObjectPtr<UWorld> DestinationLevel;

    UFUNCTION()
    void TravelToDestination();
};
