#include "DirectorCutSequenceTransition.h"

#include "Kismet/GameplayStatics.h"
#include "LevelSequenceActor.h"
#include "LevelSequencePlayer.h"

void ADirectorCutSequenceTransition::BeginPlay()
{
    Super::BeginPlay();

    if (SequenceActor && !DestinationLevel.IsNull())
    {
        if (ULevelSequencePlayer* Player = SequenceActor->GetSequencePlayer())
        {
            Player->OnFinished.AddUniqueDynamic(this, &ADirectorCutSequenceTransition::TravelToDestination);
        }
    }
}

void ADirectorCutSequenceTransition::TravelToDestination()
{
    UGameplayStatics::OpenLevelBySoftObjectPtr(this, DestinationLevel);
}
