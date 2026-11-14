#include "Stage2ShadowPrototype.h"
#include "DirectorCutGraphics.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SpotLightComponent.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "InputCoreTypes.h"

AStage2ShadowCrate::AStage2ShadowCrate()
{
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    SetRootComponent(Mesh);
    Mesh->SetMobility(EComponentMobility::Movable);
    Mesh->SetCollisionProfileName(TEXT("BlockAllDynamic"));
    Mesh->SetCollisionResponseToChannel(ECC_Pawn, ECR_Ignore);
}
float AStage2ShadowCrate::MoveAlongRail(float Axis, float DeltaSeconds)
{
    FVector P = GetActorLocation();
    const float Old = P.X;
    P.X = FMath::Clamp(Old + FMath::Clamp(Axis, -1.f, 1.f) * MoveSpeed * DeltaSeconds, RailMinX, RailMaxX);
    SetActorLocation(P, false);
    return P.X - Old;
}

AStage2ShadowDoor::AStage2ShadowDoor()
{
    PrimaryActorTick.bCanEverTick = true;
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh")); SetRootComponent(Mesh);
    Mesh->SetMobility(EComponentMobility::Movable);
    Mesh->SetCollisionProfileName(TEXT("BlockAllDynamic"));
}
void AStage2ShadowDoor::BeginPlay() { Super::BeginPlay(); ClosedPosition = GetActorLocation(); }
void AStage2ShadowDoor::OpenDoor() { bOpen = true; }
void AStage2ShadowDoor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (bOpen) SetActorLocation(FMath::VInterpConstantTo(GetActorLocation(), ClosedPosition + FVector(0,0,OpenHeight), DeltaSeconds, OpenSpeed));
}

AStage2ShadowLever::AStage2ShadowLever()
{
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh")); SetRootComponent(Mesh);
    Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}
void AStage2ShadowLever::Activate() { if (!bActivated) { bActivated = true; OnActivated(); } }

AStage2ShadowSpotlight::AStage2ShadowSpotlight()
{
    PrimaryActorTick.bCanEverTick = true;
    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root")); SetRootComponent(Root);
    Fixture = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Fixture")); Fixture->SetupAttachment(Root);
    Fixture->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Light = CreateDefaultSubobject<USpotLightComponent>(TEXT("Light")); Light->SetupAttachment(Root);
    Light->SetMobility(EComponentMobility::Movable); Light->SetIntensity(30000.f);
    Light->SetAttenuationRadius(1100.f); Light->SetOuterConeAngle(24.f); Light->SetInnerConeAngle(18.f);
}
void AStage2ShadowSpotlight::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    Clock += DeltaSeconds;
    const float Phase = SweepPeriod > KINDA_SMALL_NUMBER ? 2.f * PI * Clock / SweepPeriod : 0.f;
    Light->SetRelativeRotation(FRotator(-90.f + SweepAngle * FMath::Sin(Phase), 0, 0));
    APawn* Pawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (!bDetectionEnabled || !IsValid(Pawn)) { ExposureTime = 0; bTriggered = false; bPlayerInBeam = false; bPlayerCovered = false; return; }
    const FVector ToPlayer = Pawn->GetActorLocation() - Light->GetComponentLocation();
    const float Dist = ToPlayer.Size();
    const float Threshold = FMath::Cos(FMath::DegreesToRadians(HalfAngle));
    bPlayerInBeam = Dist <= Range && Dist > KINDA_SMALL_NUMBER && FVector::DotProduct(Light->GetForwardVector(), ToPlayer / Dist) >= Threshold;
    const auto* Graphics = GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>();
    const bool bShadows = !Graphics || Graphics->IsHigh(EDirectorCutGraphicsOption::Shadows);
    bPlayerCovered = false;
    if (bPlayerInBeam && bShadows)
    {
        FHitResult Hit;
        FCollisionQueryParams Params(SCENE_QUERY_STAT(Stage2ShadowDetection), false, this);
        Params.AddIgnoredActor(Pawn);
        const bool bHit = GetWorld()->LineTraceSingleByChannel(Hit, Light->GetComponentLocation(), Pawn->GetActorLocation(), ECC_Visibility, Params);
        bPlayerCovered = bHit && Hit.GetActor() && Hit.GetActor()->ActorHasTag(TEXT("S2Cover"));
    }
    if (bPlayerInBeam && !bPlayerCovered)
    {
        ExposureTime += DeltaSeconds;
        if (!bTriggered && ExposureTime >= FMath::Max(DetectionDelay, 0.1f))
        {
            bTriggered = true;
            OnPlayerDetected.Broadcast();
            // Retry if the manager ignored detection during its grace period.
            ExposureTime = 0.f;
            bTriggered = false;
        }
    }
    else { ExposureTime = 0.f; bTriggered = false; }
}

AStage2ShadowSectionManager::AStage2ShadowSectionManager() { PrimaryActorTick.bCanEverTick = true; }
void AStage2ShadowSectionManager::BeginPlay()
{
    Super::BeginPlay();
    if (IsValid(Spotlight)) Spotlight->OnPlayerDetected.AddDynamic(this, &AStage2ShadowSectionManager::HandlePlayerDetected);
    if (IsValid(SecondSpotlight)) SecondSpotlight->OnPlayerDetected.AddDynamic(this, &AStage2ShadowSectionManager::HandlePlayerDetected);
    if (IsValid(Lever)) Lever->SetActorHiddenInGame(true);
    if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 15.f, FColor::Yellow, TEXT("E: Grab / release / lever   Q: Shadow ON/OFF   A/D: Move"));
}
void AStage2ShadowSectionManager::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
    APawn* Pawn = PC ? PC->GetPawn() : nullptr;
    if (ProtectionLeft > 0.f) ProtectionLeft = FMath::Max(0.f, ProtectionLeft - DeltaSeconds);
    if (!PC || !Pawn) return;
    if (IsValid(Lever) && !Lever->ActorHasTag(TEXT("S2Revealed")))
    {
        const auto* Graphics = GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>();
        if (Graphics && !Graphics->IsHigh(EDirectorCutGraphicsOption::Shadows)
            && FVector::Dist2D(Pawn->GetActorLocation(), Lever->GetActorLocation()) <= 500.f)
        {
            Lever->Tags.AddUnique(TEXT("S2Revealed"));
            Lever->SetActorHiddenInGame(false);
            if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 4.f, FColor::Cyan, TEXT("LEVER FOUND - TURN SHADOWS ON TO USE COVER"));
        }
    }
    if (bUsePrototypeKeys && PC->WasInputKeyJustPressed(EKeys::E)) Interact();
    if (bUsePrototypeKeys && PC->WasInputKeyJustPressed(EKeys::Q)) ToggleShadow();
    if (bHoldingCrate && IsValid(Crate))
    {
        float Axis = (PC->IsInputKeyDown(EKeys::D) || PC->IsInputKeyDown(EKeys::Right) ? 1.f : 0.f) - (PC->IsInputKeyDown(EKeys::A) || PC->IsInputKeyDown(EKeys::Left) ? 1.f : 0.f);
        if (!FMath::IsNearlyZero(Axis))
        {
            const float Moved = Crate->MoveAlongRail(Axis, DeltaSeconds);
            Pawn->AddActorWorldOffset(FVector(Moved, 0, 0), true);
        }
    }
}
void AStage2ShadowSectionManager::Interact()
{
    APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
    APawn* Pawn = PC ? PC->GetPawn() : nullptr;
    if (!Pawn) return;
    if (bHoldingCrate) { ReleaseCrate(); return; }
    if (IsValid(Lever) && Lever->ActorHasTag(TEXT("S2Revealed")) && !Lever->bActivated && FVector::Dist2D(Pawn->GetActorLocation(), Lever->GetActorLocation()) <= InteractionDistance)
    {
        Lever->Activate(); if (IsValid(Door)) Door->OpenDoor(); bSectionCompleted = true;
        if (IsValid(Spotlight)) Spotlight->bDetectionEnabled = false;
        if (IsValid(SecondSpotlight)) SecondSpotlight->bDetectionEnabled = false;
        OnSectionComplete();
        if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 4.f, FColor::Green, TEXT("LEVER ACTIVATED - EXIT OPEN"));
        return;
    }
    if (IsValid(Crate) && FVector::Dist2D(Pawn->GetActorLocation(), Crate->GetActorLocation()) <= InteractionDistance)
    {
        bHoldingCrate = true; PC->SetIgnoreMoveInput(true);
        if (ACharacter* Character = Cast<ACharacter>(Pawn)) Character->GetCharacterMovement()->StopMovementImmediately();
        if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 3.f, FColor::Yellow, TEXT("HOLDING CRATE - A/D MOVE, E RELEASE"));
    }
}
void AStage2ShadowSectionManager::ReleaseCrate()
{
    if (!bHoldingCrate) return;
    bHoldingCrate = false;
    if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0)) PC->SetIgnoreMoveInput(false);
}
void AStage2ShadowSectionManager::ToggleShadow()
{
    if (auto* Graphics = GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>())
    {
        const bool bNew = !Graphics->IsHigh(EDirectorCutGraphicsOption::Shadows);
        Graphics->SetHigh(EDirectorCutGraphicsOption::Shadows, bNew);
        if (!bNew) ProtectionLeft = FMath::Max(ProtectionLeft, 1.f);
        if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.f, FColor::Yellow, bNew ? TEXT("SHADOW ON - COVER WORKS") : TEXT("SHADOW OFF - COVER DISABLED"));
    }
}
void AStage2ShadowSectionManager::HandlePlayerDetected()
{
    if (ProtectionLeft > 0.f || bSectionCompleted) return;
    APawn* Pawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (!Pawn || !IsValid(Checkpoint)) return;
    ReleaseCrate();
    if (ACharacter* Character = Cast<ACharacter>(Pawn)) Character->GetCharacterMovement()->StopMovementImmediately();
    Pawn->SetActorLocation(Checkpoint->GetActorLocation(), false, nullptr, ETeleportType::TeleportPhysics);
    ProtectionLeft = RespawnProtection;
    OnDetection();
    if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 3.f, FColor::Red, TEXT("DETECTED - RETURNING TO CHECKPOINT"));
}
