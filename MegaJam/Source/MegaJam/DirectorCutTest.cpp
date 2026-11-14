#include "DirectorCutTest.h"
#include "Kismet/GameplayStatics.h"
#include "DirectorCutGraphics.h"

#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Engine/World.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/Engine.h"
#include "EngineUtils.h"
#include "Engine/SkeletalMesh.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
    constexpr float MeshHeightOffset = 53.f;
    // Frames 1–8 are anticipation. Frames 9–28 are takeoff through contact.
    constexpr float TakeoffFraction = 8.f / 27.f;
    constexpr float LandingPlayRate = 1.75f;
}

ADirectorCutDragon::ADirectorCutDragon()
{
    PrimaryActorTick.bCanEverTick = true;
    bUseControllerRotationYaw = false;
    GetCapsuleComponent()->InitCapsuleSize(25.f, MeshHeightOffset);
    GetMesh()->SetRelativeLocation(FVector(0.f, 0.f, -MeshHeightOffset));
    GetMesh()->SetAnimationMode(EAnimationMode::AnimationSingleNode);

    static ConstructorHelpers::FObjectFinder<USkeletalMesh> MeshAsset(
        TEXT("/Game/DirectorCut/Dragon/Origin/SK_Dragon_Origin.SK_Dragon_Origin"));
    if (MeshAsset.Succeeded())
    {
        GetMesh()->SetSkeletalMesh(MeshAsset.Object);
    }

    static ConstructorHelpers::FObjectFinder<UAnimSequence> Idle(
        TEXT("/Game/DirectorCut/Dragon/Origin/SK_Dragon_OriginArmature_Idle.SK_Dragon_OriginArmature_Idle"));
    static ConstructorHelpers::FObjectFinder<UAnimSequence> Run(
        TEXT("/Game/DirectorCut/Dragon/Origin/SK_Dragon_OriginArmature_Run.SK_Dragon_OriginArmature_Run"));
    static ConstructorHelpers::FObjectFinder<UAnimSequence> Jump(
        TEXT("/Game/DirectorCut/Dragon/Origin/SK_Dragon_OriginArmature_Jump.SK_Dragon_OriginArmature_Jump"));
    static ConstructorHelpers::FObjectFinder<UAnimSequence> Land(
        TEXT("/Game/DirectorCut/Dragon/Origin/SK_Dragon_OriginArmature_Land.SK_Dragon_OriginArmature_Land"));
    IdleMotion = Idle.Object;
    RunMotion = Run.Object;
    JumpMotion = Jump.Object;
    LandMotion = Land.Object;

    auto* Movement = GetCharacterMovement();
    PrimaryActorTick.AddPrerequisite(Movement, Movement->PrimaryComponentTick);
    Movement->bOrientRotationToMovement = false;
    Movement->SetPlaneConstraintNormal(FVector::YAxisVector);
    Movement->SetPlaneConstraintEnabled(true);
    Movement->MaxWalkSpeed = 340.f;
    Movement->JumpZVelocity = 445.f;
    Movement->AirControl = .85f;
    Movement->BrakingDecelerationWalking = 2100.f;

    SideCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("SideCamera"));
    SideCamera->SetupAttachment(GetCapsuleComponent());
    SideCamera->SetAbsolute(true, true, false);
    SideCamera->bUsePawnControlRotation = false;
    SideCamera->SetFieldOfView(49.f);
    SideCamera->SetWorldRotation(FRotator(-17.f, -90.f, 0.f));
}

void ADirectorCutDragon::BeginPlay()
{
    Super::BeginPlay();
    // Stage 3 is a broad theatre set.  Keep the dedicated focus-puzzle camera
    // unchanged, but give the normal side view room for the arches and rigging.
    if (UGameplayStatics::GetCurrentLevelName(this, true) == TEXT("Stage3_"))
    {
        CameraDistance = 1120.f;
        CameraElevation = 320.f;
        CameraPitch = -11.f;
        CameraFieldOfView = 53.f;
    }
    SpawnPoint = GetActorLocation();
    UpdateSideCamera(SpawnPoint.X);
    PlayMotion(IdleMotion, true);
    if (IsLocallyControlled() && GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 9.f, FColor::White,
            TEXT("A / D or Left / Right: Move     Space: Jump"));
    }
}

void ADirectorCutDragon::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);
    Input->BindAxis(TEXT("DragonMove"), this, &ADirectorCutDragon::Move);
    Input->BindAction(TEXT("DragonJump"), IE_Pressed, this, &ADirectorCutDragon::StartJump);
    // Fixed-height jump: the movement tick consumes the press even if it was a tap.
}

void ADirectorCutDragon::Move(float Amount)
{
    if (!FMath::IsNearlyZero(Amount))
    {
        AddMovementInput(FVector::XAxisVector, FMath::Clamp(Amount, -1.f, 1.f));
        GetMesh()->SetRelativeRotation(FRotator(0.f, Amount < 0.f ? 180.f : 0.f, 0.f));
    }
}

void ADirectorCutDragon::StartJump()
{
    if ((!Controller || !Controller->IsMoveInputIgnored()) && CanJump())
    {
        Jump();
        AirPhase = 0.f;
    }
}

void ADirectorCutDragon::Landed(const FHitResult& Hit)
{
    Super::Landed(Hit);
    GetMesh()->SetRelativeLocation(FVector(0.f, 0.f, -MeshHeightOffset));
    AirPhase = 0.f;
    PlayMotion(LandMotion, false);
    if (LandMotion)
    {
        auto* Player = GetMesh()->GetSingleNodeInstance();
        Player->SetPlayRate(LandingPlayRate);
        LandUntil = GetWorld()->GetTimeSeconds() + LandMotion->GetPlayLength() / LandingPlayRate;
    }
}

void ADirectorCutDragon::PlayMotion(UAnimSequence* Motion, bool bLoop)
{
    if (Motion && Motion != CurrentMotion)
    {
        GetMesh()->PlayAnimation(Motion, bLoop);
        GetMesh()->GetSingleNodeInstance()->SetPlayRate(1.f);
        CurrentMotion = Motion;
    }
}

void ADirectorCutDragon::UpdateAirPose(float DeltaSeconds)
{
    if (!JumpMotion)
    {
        return;
    }

    const auto* Movement = GetCharacterMovement();
    const float VerticalSpeed = GetVelocity().Z;
    const float LaunchSpeed = Movement->JumpZVelocity;
    float TargetPhase = .5f * (1.f - FMath::Clamp(VerticalSpeed / LaunchSpeed, -1.f, 1.f));

    if (VerticalSpeed < 0.f)
    {
        // Probe along the trajectory so a raised platform can trigger the
        // contact pose before the character's capsule actually lands.
        const FVector Position = GetActorLocation();
        const float HalfHeight = GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
        const float LookAhead = .13f;
        const float Drop = -VerticalSpeed * LookAhead + .5f * FMath::Abs(Movement->GetGravityZ()) * FMath::Square(LookAhead);
        const FVector End = Position + FVector(GetVelocity().X * LookAhead, 0.f, -Drop);
        FHitResult Floor;
        FCollisionQueryParams Params(SCENE_QUERY_STAT(DragonLanding), false, this);
        const auto Shape = FCollisionShape::MakeCapsule(GetCapsuleComponent()->GetScaledCapsuleRadius() - 1.f,
            HalfHeight - 1.f);
        if (GetWorld()->SweepSingleByChannel(Floor, Position, End, FQuat::Identity, ECC_Pawn, Shape, Params)
            && Movement->IsWalkable(Floor))
        {
            TargetPhase = FMath::Max(TargetPhase, 1.f - .20f * Floor.Time);
        }
    }

    const bool bEnteringAir = CurrentMotion != JumpMotion;
    PlayMotion(JumpMotion, false);
    auto* Player = GetMesh()->GetSingleNodeInstance();
    Player->SetPlaying(false);
    AirPhase = bEnteringAir && VerticalSpeed <= 0.f ? TargetPhase :
        FMath::Max(AirPhase, FMath::FInterpTo(AirPhase, TargetPhase, DeltaSeconds, 28.f));

    const float Time = JumpMotion->GetPlayLength() * FMath::Lerp(TakeoffFraction, 1.f, AirPhase);
    Player->SetPosition(Time, false);

    // The clip has its own vertical root arc. The capsule already supplies
    // world height, so cancel that translation while preserving the leg pose.
    const FTransform Root = JumpMotion->ExtractRootTrackTransform(FAnimExtractContext(static_cast<double>(Time)), nullptr);
    const FTransform Reference = JumpMotion->ExtractRootTrackTransform(FAnimExtractContext(0.0), nullptr);
    GetMesh()->SetRelativeLocation(FVector(0.f, 0.f, -MeshHeightOffset - (Root.GetTranslation().Z - Reference.GetTranslation().Z)));
}

void ADirectorCutDragon::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (GetActorLocation().Z < SpawnPoint.Z - 310.f)
    {
        GetCharacterMovement()->StopMovementImmediately();
        SetActorLocation(SpawnPoint, false, nullptr, ETeleportType::TeleportPhysics);
        GetCharacterMovement()->SetMovementMode(MOVE_Walking);
        LandUntil = 0.f;
        AirPhase = 0.f;
        GetMesh()->SetRelativeLocation(FVector(0.f, 0.f, -MeshHeightOffset));
    }

    if (GetCharacterMovement()->IsFalling())
    {
        UpdateAirPose(DeltaSeconds);
    }
    else if (GetWorld()->GetTimeSeconds() >= LandUntil)
    {
        PlayMotion(FMath::Abs(GetVelocity().X) > 12.f ? RunMotion : IdleMotion, true);
    }

    const FVector Position = GetActorLocation();
    TheatreCameraBlend = FMath::FInterpTo(TheatreCameraBlend, TheatreCameraTarget, DeltaSeconds, 3.5f);
    const float TargetX = FMath::Lerp(static_cast<float>(Position.X), TheatreCameraFocusX, TheatreCameraBlend);
    const float DesiredX = FMath::FInterpTo(SideCamera->GetComponentLocation().X, TargetX, DeltaSeconds, 6.f);
    UpdateSideCamera(DesiredX);
}

void ADirectorCutDragon::UpdateSideCamera(float FollowX)
{
    const float Distance = FMath::Lerp(CameraDistance, 1310.f, TheatreCameraBlend);
    const float Height = FMath::Lerp(CameraElevation, 305.f, TheatreCameraBlend);
    const float Pitch = FMath::Lerp(CameraPitch, -6.f, TheatreCameraBlend);
    SideCamera->SetWorldLocation(FVector(FollowX, SpawnPoint.Y + Distance, SpawnPoint.Z + Height));
    SideCamera->SetWorldRotation(FRotator(Pitch, -90.f, 0.f));
    SideCamera->SetFieldOfView(FMath::Lerp(CameraFieldOfView, 61.f, TheatreCameraBlend));
}

ADirectorCutTestMode::ADirectorCutTestMode()
{
    DefaultPawnClass = ADirectorCutDragon::StaticClass();
    PlayerControllerClass = ADirectorCutPlayerController::StaticClass();
}
APawn* ADirectorCutTestMode::SpawnDefaultPawnAtTransform_Implementation(AController* NewPlayer, const FTransform& SpawnTransform)
{
    for (TActorIterator<ADirectorCutDragon> It(GetWorld()); It; ++It)
    {
        if (It->ActorHasTag(TEXT("PlayerDragon")) && !It->GetController())
        {
            return *It;
        }
    }
    return Super::SpawnDefaultPawnAtTransform_Implementation(NewPlayer, SpawnTransform);
}

