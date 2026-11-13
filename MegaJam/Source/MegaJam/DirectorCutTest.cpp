#include "DirectorCutTest.h"
#include "DirectorCutGraphics.h"
#include "DirectorCutDragonAnimInstance.h"

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
    constexpr float LandingPlayRate = 2.1f;
    constexpr float LandingDuration = .13f;
    constexpr double JumpBufferDuration = .13;
}

ADirectorCutDragon::ADirectorCutDragon()
{
    PrimaryActorTick.bCanEverTick = true;
    bUseControllerRotationYaw = false;
    GetCapsuleComponent()->InitCapsuleSize(25.f, MeshHeightOffset);
    GetMesh()->SetRelativeLocation(FVector(0.f, 0.f, -MeshHeightOffset));
    GetMesh()->PrimaryComponentTick.AddPrerequisite(this, PrimaryActorTick);

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
    SpawnPoint = GetActorLocation();
    UpdateSideCamera(SpawnPoint.X);
    GetMesh()->SetAnimInstanceClass(UDirectorCutDragonAnimInstance::StaticClass());
    PlayMotion(IdleMotion, 0.f, 0.f);
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
    MoveInput = Controller && Controller->IsMoveInputIgnored() ? 0.f : Amount;
    if (!FMath::IsNearlyZero(Amount))
    {
        AddMovementInput(FVector::XAxisVector, FMath::Clamp(Amount, -1.f, 1.f));
        GetMesh()->SetRelativeRotation(FRotator(0.f, Amount < 0.f ? 180.f : 0.f, 0.f));
    }
}

void ADirectorCutDragon::StartJump()
{
    if (Controller && Controller->IsMoveInputIgnored())
    {
        return;
    }

    if (CanJump())
    {
        BufferedJumpUntil = -1.0;
        Jump();
    }
    else if (GetCharacterMovement()->IsFalling())
    {
        BufferedJumpUntil = GetWorld()->GetTimeSeconds() + JumpBufferDuration;
    }
}

void ADirectorCutDragon::CheckJumpInput(float DeltaTime)
{
    if (BufferedJumpUntil >= 0.0)
    {
        if (GetWorld()->GetTimeSeconds() > BufferedJumpUntil || (Controller && Controller->IsMoveInputIgnored()))
        {
            BufferedJumpUntil = -1.0;
        }
        else if (CanJump())
        {
            BufferedJumpUntil = -1.0;
            Jump();
        }
    }
    Super::CheckJumpInput(DeltaTime);
}

void ADirectorCutDragon::Landed(const FHitResult& Hit)
{
    Super::Landed(Hit);
    LandingElapsed = 0.f;
    AirPhase = 0.f;
}

void ADirectorCutDragon::PlayMotion(UAnimSequence* Motion, float Time, float BlendDuration, float RootHeightOffset)
{
    if (Motion)
    {
        if (auto* Instance = Cast<UDirectorCutDragonAnimInstance>(GetMesh()->GetAnimInstance()))
        {
            Instance->SetMotion(Motion, Time, BlendDuration, RootHeightOffset);
            CurrentMotion = Motion;
        }
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
    AirPhase = bEnteringAir && VerticalSpeed <= 0.f ? TargetPhase :
        FMath::Max(AirPhase, FMath::FInterpTo(AirPhase, TargetPhase, DeltaSeconds, 28.f));

    const float Time = JumpMotion->GetPlayLength() * FMath::Lerp(TakeoffFraction, 1.f, AirPhase);

    // The clip has its own vertical root arc. The capsule already supplies
    // world height, so cancel that translation while preserving the leg pose.
    const FTransform Root = JumpMotion->ExtractRootTrackTransform(FAnimExtractContext(static_cast<double>(Time)), nullptr);
    const FTransform Reference = JumpMotion->ExtractRootTrackTransform(FAnimExtractContext(0.0), nullptr);
    PlayMotion(JumpMotion, Time, .065f, Reference.GetTranslation().Z - Root.GetTranslation().Z);
}

void ADirectorCutDragon::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (GetActorLocation().Z < SpawnPoint.Z - 310.f)
    {
        GetCharacterMovement()->StopMovementImmediately();
        SetActorLocation(SpawnPoint, false, nullptr, ETeleportType::TeleportPhysics);
        GetCharacterMovement()->SetMovementMode(MOVE_Walking);
        BufferedJumpUntil = -1.0;
        LandingElapsed = LandingDuration;
        AirPhase = 0.f;
        GetMesh()->SetRelativeLocation(FVector(0.f, 0.f, -MeshHeightOffset));
    }

    if (GetCharacterMovement()->IsFalling())
    {
        UpdateAirPose(DeltaSeconds);
    }
    else
    {
        GetMesh()->SetRelativeLocation(FVector(0.f, 0.f, -MeshHeightOffset));
        const float Speed = FMath::Abs(GetVelocity().X);
        const bool bMoving = Speed > 12.f || !FMath::IsNearlyZero(MoveInput);
        if (!bMoving && LandMotion && LandingElapsed < LandingDuration)
        {
            PlayMotion(LandMotion, FMath::Min(LandingElapsed * LandingPlayRate, LandMotion->GetPlayLength()), .045f);
            LandingElapsed += DeltaSeconds;
        }
        else
        {
            LandingElapsed = LandingDuration;
            UAnimSequence* GroundMotion = bMoving ? RunMotion.Get() : IdleMotion.Get();
            if (GroundMotion && GroundMotion->GetPlayLength() > 0.f)
            {
                if (GroundMotion != CurrentMotion)
                {
                    GroundMotionTime = 0.f;
                }
                const float PlayRate = bMoving ? Speed / GetCharacterMovement()->MaxWalkSpeed : 1.f;
                GroundMotionTime = FMath::Fmod(GroundMotionTime + DeltaSeconds * PlayRate, GroundMotion->GetPlayLength());
                PlayMotion(GroundMotion, GroundMotionTime, .095f);
            }
        }
    }

    const FVector Position = GetActorLocation();
    const float DesiredX = FMath::FInterpTo(SideCamera->GetComponentLocation().X, Position.X, DeltaSeconds, 6.f);
    UpdateSideCamera(DesiredX);
}

void ADirectorCutDragon::UpdateSideCamera(float FollowX)
{
    SideCamera->SetWorldLocation(FVector(FollowX, SpawnPoint.Y + CameraDistance, SpawnPoint.Z + CameraElevation));
    SideCamera->SetWorldRotation(FRotator(CameraPitch, -90.f, 0.f));
    SideCamera->SetFieldOfView(CameraFieldOfView);
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



