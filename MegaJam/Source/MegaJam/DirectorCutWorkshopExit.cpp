#include "DirectorCutWorkshopExit.h"

#include "Camera/PlayerCameraManager.h"
#include "DirectorCutGraphics.h"
#include "DirectorCutTest.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "TimerManager.h"

ADirectorCutWorkshopExit::ADirectorCutWorkshopExit()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickGroup = TG_PostUpdateWork;
}

void ADirectorCutWorkshopExit::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    auto* Controller = UGameplayStatics::GetPlayerController(this, 0);
    const auto* GraphicsController = Cast<ADirectorCutPlayerController>(Controller);
    if (!Controller || Controller->IsMoveInputIgnored() || (GraphicsController && GraphicsController->IsGraphicsMenuOpen())
        || DestinationLevel.IsNull())
    {
        return;
    }

    auto* Dragon = Cast<ADirectorCutDragon>(Controller->GetPawn());
    if (!Dragon || !Dragon->HasHeroLegs() || Dragon->GetActorLocation().X <= ExitX)
    {
        return;
    }

    SetActorTickEnabled(false);
    Controller->SetIgnoreMoveInput(true);
    Dragon->GetCharacterMovement()->StopMovementImmediately();
    if (APlayerCameraManager* Camera = Controller->PlayerCameraManager)
    {
        Camera->StartCameraFade(0.f, 1.f, 1.5f, FLinearColor::Black, false, true);
    }

    FTimerHandle TravelTimer;
    GetWorldTimerManager().SetTimer(TravelTimer, this, &ADirectorCutWorkshopExit::TravelToDestination, 1.6f, false);
}

void ADirectorCutWorkshopExit::TravelToDestination()
{
    UGameplayStatics::OpenLevelBySoftObjectPtr(this, DestinationLevel);
}
