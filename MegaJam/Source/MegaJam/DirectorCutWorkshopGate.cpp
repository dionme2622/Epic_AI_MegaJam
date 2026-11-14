#include "DirectorCutWorkshopGate.h"

#include "Components/AudioComponent.h"
#include "Components/SceneComponent.h"
#include "DirectorCutGraphics.h"
#include "DirectorCutTest.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundAttenuation.h"
#include "Sound/SoundBase.h"
#include "UObject/UnrealType.h"

namespace
{
    constexpr double WorkshopOpenRise = 350.;
    constexpr float WorkshopOpeningDuration = 1.75f;

    void PlayWorkshopSound(UAudioComponent& Audio, USoundBase* Sound, float Volume, float Pitch)
    {
        if (!Sound) return;
        Audio.SetSound(Sound);
        Audio.SetVolumeMultiplier(Volume);
        Audio.SetPitchMultiplier(Pitch);
        Audio.Play();
    }
}

ADirectorCutWorkshopGate::ADirectorCutWorkshopGate()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickGroup = TG_PostUpdateWork;
    SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));

    WheelAudio = CreateDefaultSubobject<UAudioComponent>(TEXT("WheelAudio"));
    GateAudio = CreateDefaultSubobject<UAudioComponent>(TEXT("GateAudio"));
    for (UAudioComponent* Audio : {WheelAudio.Get(), GateAudio.Get()})
    {
        Audio->SetupAttachment(RootComponent);
        Audio->bAutoActivate = false;
        Audio->bOverrideAttenuation = true;
        Audio->AttenuationOverrides.AttenuationShapeExtents = FVector(500.);
        Audio->AttenuationOverrides.FalloffDistance = 2600.f;
    }
}

void ADirectorCutWorkshopGate::BeginPlay()
{
    Super::BeginPlay();
    if (IsValid(WorkshopDirector))
    {
        WheelSolvedProperty = FindFProperty<FBoolProperty>(WorkshopDirector->GetClass(), TEXT("WheelSolved"));
    }
    if (!WheelSolvedProperty || !IsValid(Wheel) || !IsValid(GateVisual) || !IsValid(GateBarrier))
    {
        SetActorTickEnabled(false);
        return;
    }

    ClosedGatePosition = GateVisual->GetActorLocation();
    PreviousWheelX = Wheel->GetActorLocation().X;
    GateBarrier->SetActorHiddenInGame(true);
    GateBarrier->SetActorEnableCollision(true);
    GateAudio->SetWorldLocation(ClosedGatePosition);
}

void ADirectorCutWorkshopGate::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!IsValid(WorkshopDirector) || !IsValid(Wheel) || !IsValid(GateVisual) || !IsValid(GateBarrier))
    {
        SetActorTickEnabled(false);
        return;
    }

    const FVector WheelPosition = Wheel->GetActorLocation();
    const double WheelStep = WheelPosition.X - PreviousWheelX;
    const int32 WheelDirection = FMath::IsNearlyZero(WheelStep, .01) ? 0 : (WheelStep > 0. ? 1 : -1);
    PreviousWheelX = WheelPosition.X;
    WheelAudio->SetWorldLocation(WheelPosition);

    const bool bSecured = WheelSolvedProperty->GetPropertyValue_InContainer(WorkshopDirector.Get());
    if (!bSecured && WheelDirection != 0 && WheelDirection != PreviousWheelDirection)
    {
        PlayWorkshopSound(*WheelAudio, WheelRoll, .70f, 1.35f);
    }
    PreviousWheelDirection = WheelDirection;

    if (!bSecured) return;

    if (!bOpeningStarted)
    {
        const auto* Controller = Cast<ADirectorCutPlayerController>(UGameplayStatics::GetPlayerController(this, 0));
        if (Controller && Controller->IsGraphicsMenuOpen()) return;

        bOpeningStarted = true;
        if (auto* Dragon = Cast<ADirectorCutDragon>(UGameplayStatics::GetPlayerPawn(this, 0));
            Dragon && FMath::Abs(Dragon->GetActorLocation().X - ClosedGatePosition.X) > 420.)
        {
            FramedDragon = Dragon;
            // Keep the wheel and gate in frame in the wide shot.
            Dragon->SetTheatreCameraFraming(1.f, static_cast<float>(ClosedGatePosition.X - 380.));
        }
        PlayWorkshopSound(*GateAudio, GateRise, .72f, 1.f);
    }

    OpeningElapsed = FMath::Min(OpeningElapsed + DeltaSeconds, WorkshopOpeningDuration);
    const double Height = WorkshopOpenRise * FMath::SmoothStep(0.f, WorkshopOpeningDuration, OpeningElapsed);
    GateVisual->SetActorLocation(ClosedGatePosition + FVector(0., 0., Height), false, nullptr, ETeleportType::TeleportPhysics);
    GateAudio->SetWorldLocation(GateVisual->GetActorLocation());

    if (OpeningElapsed >= WorkshopOpeningDuration)
    {
        GateBarrier->SetActorEnableCollision(false);
        PlayWorkshopSound(*GateAudio, GateLatch, .82f, 1.f);
        if (auto* Dragon = FramedDragon.Get())
        {
            Dragon->SetTheatreCameraFraming(0.f, 0.f);
        }
        SetActorTickEnabled(false);
    }
}
