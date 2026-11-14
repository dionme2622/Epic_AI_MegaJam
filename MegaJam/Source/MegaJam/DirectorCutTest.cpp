#include "DirectorCutTest.h"
#include "DirectorCutGraphics.h"
#include "DirectorCutDragonAnimInstance.h"
#include "DirectorCutWheelchair.h"

#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Engine/World.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "EngineUtils.h"
#include "Engine/SkeletalMesh.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
    constexpr float CartDeckHeight = 31.9f;
    constexpr float MeshHeightOffset = 53.f;
    // Frames 1–8 are anticipation. Frames 9–28 are takeoff through contact.
    constexpr float TakeoffFraction = 8.f / 27.f;
    constexpr float LandingPlayRate = 2.1f;
    constexpr float LandingDuration = .13f;
    constexpr double JumpBufferDuration = .13;
    // Centroids of the cut surfaces in the two authored meshes' reference poses.
    const FVector DragonWaist(4.91, .01, 41.);
    const FVector KnightWaist(-.01, -.80, 40.5);
    const FVector EquippedLegScale(1.16, 1.16, 1.);
    const FRotator EquippedLegFacing(0., -90., 0.);

    FTransform ComponentBonePose(const FReferenceSkeleton& Skeleton, TConstArrayView<FTransform> LocalPose, int32 Bone)
    {
        FTransform Pose = LocalPose[Bone];
        for (int32 Parent = Skeleton.GetParentIndex(Bone); Parent != INDEX_NONE; Parent = Skeleton.GetParentIndex(Parent))
        {
            Pose *= LocalPose[Parent];
        }
        return Pose;
    }
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
    StandingDragonMesh = MeshAsset.Object;
    if (StandingDragonMesh)
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
    StandingMotions[0] = IdleMotion;
    StandingMotions[1] = RunMotion;
    StandingMotions[2] = JumpMotion;
    StandingMotions[3] = LandMotion;

    static ConstructorHelpers::FObjectFinder<USkeletalMesh> UpperMesh(
        TEXT("/Game/DirectorCut/Dragon/Upper/SK_Dragon_Upper.SK_Dragon_Upper"));
    static ConstructorHelpers::FObjectFinder<UAnimSequence> UpperIdle(
        TEXT("/Game/DirectorCut/Dragon/Upper/SK_Dragon_UpperArmature_Idle.SK_Dragon_UpperArmature_Idle"));
    static ConstructorHelpers::FObjectFinder<UAnimSequence> UpperJump(
        TEXT("/Game/DirectorCut/Dragon/Upper/SK_Dragon_UpperArmature_Jump.SK_Dragon_UpperArmature_Jump"));
    static ConstructorHelpers::FObjectFinder<UAnimSequence> UpperRun(
        TEXT("/Game/DirectorCut/Dragon/Upper/SK_Dragon_UpperArmature_Run_Upright.SK_Dragon_UpperArmature_Run_Upright"));
    static ConstructorHelpers::FObjectFinder<UAnimSequence> UpperLand(
        TEXT("/Game/DirectorCut/Dragon/Upper/SK_Dragon_UpperArmature_Land.SK_Dragon_UpperArmature_Land"));
    HeroUpperMesh = UpperMesh.Object;
    UnmountedCartIdleMotion = UpperIdle.Object;
    UnmountedCartJumpMotion = UpperJump.Object;
    HeroRunMotion = UpperRun.Object;
    HeroLandMotion = UpperLand.Object;

    HeroLegsMesh = CreateDefaultSubobject<UPoseableMeshComponent>(TEXT("EquippedHeroLegs"));
    HeroLegsMesh->SetupAttachment(GetMesh());
    HeroLegsMesh->SetRelativeScale3D(EquippedLegScale);
    HeroLegsMesh->SetRelativeLocation(DragonWaist - EquippedLegFacing.RotateVector(KnightWaist * EquippedLegScale)
        + FVector(0., 0., 3.0));
    HeroLegsMesh->SetRelativeRotation(EquippedLegFacing);
    HeroLegsMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    HeroLegsMesh->SetVisibility(false);
    static ConstructorHelpers::FObjectFinder<USkeletalMesh> KnightLower(
        TEXT("/Game/DirectorCut/Dragon/KnightLegs/SK_Knight_LowerBody.SK_Knight_LowerBody"));
    HeroLegsMesh->SetSkinnedAssetAndUpdate(KnightLower.Object);

    auto* Movement = GetCharacterMovement();
    PrimaryActorTick.AddPrerequisite(Movement, Movement->PrimaryComponentTick);
    Movement->bOrientRotationToMovement = false;
    Movement->SetPlaneConstraintNormal(FVector::YAxisVector);
    Movement->SetPlaneConstraintEnabled(true);
    Movement->MaxWalkSpeed = 340.f;
    Movement->JumpZVelocity = 445.f;
    Movement->AirControl = .85f;
    Movement->BrakingDecelerationWalking = 2100.f;

    CartBody = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RideCartBody"));
    CartBody->SetupAttachment(GetCapsuleComponent());
    CartBody->SetRelativeLocation(FVector(0.f, 0.f, -MeshHeightOffset));
    CartBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    for (int32 Index = 0; Index < UE_ARRAY_COUNT(DirectorCutCart::WheelCenters); ++Index)
    {
        auto* Wheel = CreateDefaultSubobject<UStaticMeshComponent>(*FString::Printf(TEXT("RideCartWheel%d"), Index + 1));
        Wheel->SetupAttachment(CartBody);
        Wheel->SetRelativeLocation(DirectorCutCart::WheelCenters[Index]);
        Wheel->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    }

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
    const FString LevelName = UGameplayStatics::GetCurrentLevelName(this, true);
    if (LevelName == TEXT("Stage3_"))
    {
        CameraDistance = 1120.f;
        CameraElevation = 320.f;
        CameraPitch = -11.f;
        CameraFieldOfView = 53.f;
    }
    SpawnPoint = GetActorLocation();
    UpdateSideCamera(SpawnPoint.X);
    auto* Game = GetGameInstance();
    auto* Travel = Game ? Game->GetSubsystem<UDirectorCutWheelchairTravel>() : nullptr;
    if (bAwaitWheelchair && Travel)
    {
        Travel->BeginCastle();
    }
    const bool bStartMounted = bContinueCartFromCastle && Travel
        ? Travel->EnterWorkshop(bRideCart) : bRideCart && !bAwaitWheelchair;
    if (bContinueCartFromCastle && Travel)
    {
        Travel->StartWorkshop();
    }
    bRideCart = false;
    if ((bAwaitWheelchair || bContinueCartFromCastle) && CartRiderMesh && CartMotion)
    {
        GetMesh()->SetSkeletalMesh(CartRiderMesh);
        IdleMotion = UnmountedCartIdleMotion ? UnmountedCartIdleMotion.Get() : CartMotion.Get();
        RunMotion = CartMotion;
        JumpMotion = UnmountedCartJumpMotion ? UnmountedCartJumpMotion.Get() : CartMotion.Get();
        LandMotion = nullptr;
    }
    CartBody->SetRelativeLocation(FVector(0.f, 0.f, -GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()));
    GetMesh()->SetAnimInstanceClass(UDirectorCutDragonAnimInstance::StaticClass());
    if ((LevelName == TEXT("Stage3_") || LevelName == TEXT("Stage4")) && (!Travel || Travel->HasHeroLegs(true)))
    {
        EquipHeroLegs();
    }
    else if (!bStartMounted || !MountCart())
    {
        CartBody->SetVisibility(false, true);
        PlayMotion(IdleMotion, 0.f, 0.f);
    }
    if (IsLocallyControlled() && GEngine && !bAwaitWheelchair && !bContinueCartFromCastle
        && LevelName != TEXT("Stage3_") && LevelName != TEXT("Stage4") && LevelName != TEXT("L_Stage1")
        && !(LevelName == TEXT("Stage1") && GetWorld()->GetOutermost()->GetName().Contains(TEXT("/DirectorCut/Stage/"))))
    {
        GEngine->AddOnScreenDebugMessage(-1, 9.f, FColor::White,
            TEXT("A / D or Left / Right: Move     Space: Jump"));
    }
}

bool ADirectorCutDragon::CanMountCart() const
{
    return !bRideCart && !bHeroLegsEquipped && CartRiderMesh && CartMotion && CartBody->GetStaticMesh();
}

bool ADirectorCutDragon::MountCart()
{
    if (!CanMountCart())
    {
        return false;
    }

    for (USceneComponent* Child : CartBody->GetAttachChildren())
    {
        if (auto* Wheel = Cast<UStaticMeshComponent>(Child); Wheel && Wheel->GetStaticMesh())
        {
            CartWheels.Add(Wheel);
        }
    }
    if (GetMesh()->GetSkeletalMeshAsset() != CartRiderMesh)
    {
        GetMesh()->SetSkeletalMesh(CartRiderMesh);
    }
    bRideCart = true;
    StopJumping();
    BufferedJumpUntil = -1.0;
    if (bAwaitWheelchair)
    {
        auto* Game = GetGameInstance();
        if (auto* Travel = Game ? Game->GetSubsystem<UDirectorCutWheelchairTravel>() : nullptr)
        {
            Travel->RecordMount();
        }
    }
    LastCartLocation = GetActorLocation();
    CartBody->SetVisibility(true, true);
    UpdateCart(0.f);
    return true;
}

bool ADirectorCutDragon::EquipHeroLegs()
{
    if (bHeroLegsEquipped || !HeroUpperMesh || !HeroLegsMesh->GetSkinnedAsset())
    {
        return false;
    }

    bHeroLegsEquipped = true;
    bRideCart = false;
    StopJumping();
    BufferedJumpUntil = -1.0;
    CartBody->SetVisibility(false, true);
    GetMesh()->SetSkeletalMesh(HeroUpperMesh);
    GetMesh()->SetRelativeLocation(FVector(0.f, 0.f, -GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()));
    GetMesh()->SetAnimInstanceClass(UDirectorCutDragonAnimInstance::StaticClass());
    CurrentMotion = nullptr;
    IdleMotion = UnmountedCartIdleMotion;
    RunMotion = HeroRunMotion;
    JumpMotion = UnmountedCartJumpMotion;
    LandMotion = HeroLandMotion;
    GroundMotionTime = 0.f;
    LandingElapsed = LandingDuration;
    AirPhase = 0.f;
    PlayMotion(IdleMotion, 0.f, 0.f);
    HeroLegsMesh->SetVisibility(true);
    UpdateHeroLegsPose(0.f);

    if (bContinueCartFromCastle)
    {
        auto* Game = GetGameInstance();
        if (auto* Travel = Game ? Game->GetSubsystem<UDirectorCutWheelchairTravel>() : nullptr)
        {
            Travel->RecordHeroLegs();
        }
    }
    return true;
}

void ADirectorCutDragon::RestoreOriginalLegs()
{
    if (!bHeroLegsEquipped || !StandingDragonMesh) return;

    bHeroLegsEquipped = false;
    HeroLegsMesh->SetVisibility(false);
    GetMesh()->SetSkeletalMesh(StandingDragonMesh);
    GetMesh()->SetRelativeLocation(FVector(0.f, 0.f, -GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()));
    GetMesh()->SetAnimInstanceClass(UDirectorCutDragonAnimInstance::StaticClass());
    CurrentMotion = nullptr;
    IdleMotion = StandingMotions[0];
    RunMotion = StandingMotions[1];
    JumpMotion = StandingMotions[2];
    LandMotion = StandingMotions[3];
    PlayMotion(IdleMotion, 0.f, 0.f);
}

bool ADirectorCutDragon::CanJumpInternal_Implementation() const
{
    return !bRideCart && (!bContinueCartFromCastle || bHeroLegsEquipped) && Super::CanJumpInternal_Implementation();
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
    if (bRideCart || (bContinueCartFromCastle && !bHeroLegsEquipped) || (Controller && Controller->IsMoveInputIgnored()))
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
    if (bRideCart)
    {
        StopJumping();
        BufferedJumpUntil = -1.0;
        return;
    }
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
            const TOptional<FVector> Waist = bHeroLegsEquipped ? TOptional<FVector>(DragonWaist) : TOptional<FVector>();
            Instance->SetMotion(Motion, Time, BlendDuration, RootHeightOffset, Waist);
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
    if (bHeroLegsEquipped)
    {
        PlayMotion(JumpMotion, Time, .065f);
        return;
    }

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
        LastCartLocation = SpawnPoint;
        GetCharacterMovement()->SetMovementMode(MOVE_Walking);
        BufferedJumpUntil = -1.0;
        LandingElapsed = LandingDuration;
        AirPhase = 0.f;
        if (!bHeroLegsEquipped)
        {
            GetMesh()->SetRelativeLocation(FVector(0.f, 0.f, -GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()));
        }
    }

    if (bRideCart)
    {
        UpdateCart(DeltaSeconds);
    }
    else if (GetCharacterMovement()->IsFalling())
    {
        UpdateAirPose(DeltaSeconds);
    }
    else
    {
        if (!bHeroLegsEquipped)
        {
            GetMesh()->SetRelativeLocation(FVector(0.f, 0.f, -GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()));
        }
        const float Speed = FMath::Abs(GetVelocity().X);
        const bool bMoving = Speed > 12.f || !FMath::IsNearlyZero(MoveInput);
        if (LandMotion && LandingElapsed < LandingDuration && (bHeroLegsEquipped || !bMoving))
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

    if (bHeroLegsEquipped)
    {
        UpdateHeroLegsPose(DeltaSeconds);
    }
    const FVector Position = GetActorLocation();
    TheatreCameraBlend = FMath::FInterpTo(TheatreCameraBlend, TheatreCameraTarget, DeltaSeconds, 3.5f);
    const float TargetX = FMath::Lerp(static_cast<float>(Position.X) + (bContinueCartFromCastle ? 175.f : 0.f),
        TheatreCameraFocusX, TheatreCameraBlend);
    const float DesiredX = FMath::FInterpTo(SideCamera->GetComponentLocation().X, TargetX, DeltaSeconds, 6.f);
    UpdateSideCamera(DesiredX);
}

void ADirectorCutDragon::UpdateCart(float DeltaSeconds)
{
    const FVector Position = GetActorLocation();
    const bool bGrounded = GetCharacterMovement()->IsMovingOnGround();
    if (bGrounded && bCartWasGrounded)
    {
        const double Distance = Position.X - LastCartLocation.X;
        WheelAngle = FMath::UnwindDegrees(WheelAngle - FMath::RadiansToDegrees(Distance / DirectorCutCart::WheelRadius));
        for (UStaticMeshComponent* Wheel : CartWheels)
        {
            Wheel->SetRelativeRotation(FRotator(WheelAngle, 0.f, 0.f));
        }
    }
    LastCartLocation = Position;
    bCartWasGrounded = bGrounded;

    // Align the center of the cut waist with the center of the cart deck.
    const FVector SeatAnchor(14.1f, 0.f, 30.f);
    const FRotator Facing(0.f, GetMesh()->GetRelativeRotation().Yaw, 0.f);
    GetMesh()->SetRelativeRotation(Facing);
    const FVector DeckCenter = CartBody->GetRelativeLocation() + FVector(0.f, 0.f, CartDeckHeight);
    GetMesh()->SetRelativeLocation(DeckCenter - Facing.RotateVector(SeatAnchor * GetMesh()->GetRelativeScale3D()));
    const float Speed = FMath::Abs(GetVelocity().X);
    bCartDriving = Speed > (bCartDriving ? 9.f : 18.f);
    UAnimSequence* Motion = bCartDriving ? CartDriveMotion.Get() : CartIdleMotion.Get();
    if (!Motion)
    {
        PlayMotion(CartMotion, .33f, 0.f);
        return;
    }

    if (Motion != CurrentMotion)
    {
        CartMotionTime = 0.f;
    }
    const float PlayRate = bCartDriving
        ? FMath::GetMappedRangeValueClamped(FVector2D(0.f, GetCharacterMovement()->MaxWalkSpeed), FVector2D(.65f, 1.15f), Speed)
        : 1.f;
    CartMotionTime = FMath::Fmod(CartMotionTime + DeltaSeconds * PlayRate, Motion->GetPlayLength());
    PlayMotion(Motion, CartMotionTime, .18f);
}

void ADirectorCutDragon::UpdateHeroLegsPose(float DeltaSeconds)
{
    const auto* LowerAsset = Cast<USkeletalMesh>(HeroLegsMesh->GetSkinnedAsset());
    if (!LowerAsset) return;
    const auto& Skeleton = LowerAsset->GetRefSkeleton();
    const auto& Reference = Skeleton.GetRefBonePose();
    if (HeroLegsMesh->BoneSpaceTransforms.Num() != Reference.Num()) return;

    const auto* Movement = GetCharacterMovement();
    const bool bAirborne = Movement->IsFalling();
    const float Speed = FMath::Min(FMath::Abs(GetVelocity().X) / Movement->MaxWalkSpeed, 1.);
    const float Cycle = RunMotion && RunMotion->GetPlayLength() > 0.f
        ? GroundMotionTime / RunMotion->GetPlayLength() * UE_TWO_PI : 0.f;
    const float Tuck = FMath::SmoothStep(.03f, .43f, AirPhase) * (1.f - FMath::SmoothStep(.58f, 1.f, AirPhase));
    const float Landing = CurrentMotion == LandMotion && !bAirborne
        ? FMath::Sin(UE_PI * FMath::Clamp(LandingElapsed / LandingDuration, 0.f, 1.f)) : 0.f;
    static const FName Joints[2][3] = {
        {TEXT("LeftUpLeg"), TEXT("LeftLeg"), TEXT("LeftFoot")},
        {TEXT("RightUpLeg"), TEXT("RightLeg"), TEXT("RightFoot")}
    };
    double LowestSole = TNumericLimits<double>::Max();
    for (int32 Leg = 0; Leg < 2; ++Leg)
    {
        const float Side = Leg == 0 ? 1.f : -1.f;
        const float Stride = Side * FMath::Cos(Cycle);
        const float Swing = FMath::Max(0.f, Side * FMath::Sin(Cycle));
        const FVector Stance(-4.f * Side, 4.f, 0.f);
        FVector Target = Stance + FVector(31.f * Stride, 49.f * Swing, -18.f * Swing) * Speed;
        if (bAirborne)
        {
            const FVector Tucked(Leg == 0 ? -46.f : -23.f, Leg == 0 ? 82.f : 66.f, -28.f);
            Target = FMath::Lerp(Stance, Tucked, Tuck);
        }
        else if (Landing > 0.f)
        {
            Target = Stance + FVector(-19.f, 39.f, -19.f) * Landing;
        }
        FVector& Angles = HeroLegAngles[Leg];
        Angles = DeltaSeconds > 0.f ? FMath::VInterpTo(Angles, Target, DeltaSeconds, 26.f) : Target;
        for (int32 Joint = 0; Joint < 3; ++Joint)
        {
            const int32 Bone = Skeleton.FindBoneIndex(Joints[Leg][Joint]);
            if (Bone == INDEX_NONE) continue;
            const FTransform Parent = ComponentBonePose(Skeleton, Reference, Skeleton.GetParentIndex(Bone));
            // Knight feet face +Y in their bind pose. Negative pitch raises the thigh forward.
            const FVector Axis = Parent.InverseTransformVectorNoScale(-FVector::XAxisVector);
            FTransform Pose = Reference[Bone];
            Pose.SetRotation(FQuat(Axis, FMath::DegreesToRadians(Angles[Joint])) * Pose.GetRotation());
            HeroLegsMesh->BoneSpaceTransforms[Bone] = Pose;
        }

        const int32 Foot = Skeleton.FindBoneIndex(Joints[Leg][2]);
        if (Foot != INDEX_NONE)
        {
            const FTransform RestFoot = ComponentBonePose(Skeleton, Reference, Foot);
            const FTransform PosedFoot = ComponentBonePose(Skeleton, HeroLegsMesh->BoneSpaceTransforms, Foot);
            const FVector Ankle = RestFoot.GetTranslation();
            // Sample the heel and toe of each sole so the supporting boot tracks the floor.
            for (const double Offset : {-6., 12.})
            {
                const FVector Point = PosedFoot.TransformPosition(RestFoot.InverseTransformPosition({Ankle.X, Ankle.Y + Offset, 0.}));
                LowestSole = FMath::Min(LowestSole, Point.Z);
            }
        }
    }
    HeroLegsMesh->RefreshBoneTransforms();

    const float Contact = bAirborne ? FMath::SmoothStep(.86f, 1.f, AirPhase) : 1.f;
    const double SoleOffset = LowestSole == TNumericLimits<double>::Max()
        ? 0. : LowestSole * EquippedLegScale.Z + HeroLegsMesh->GetRelativeLocation().Z;
    GetMesh()->SetRelativeLocation(FVector(0., 0., -GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight() - SoleOffset * Contact));
}

void ADirectorCutDragon::UpdateSideCamera(float FollowX)
{
    const float Distance = FMath::Lerp(CameraDistance, 1310.f, TheatreCameraBlend);
    const float Height = FMath::Lerp(CameraElevation, 305.f, TheatreCameraBlend);
    const float Pitch = FMath::Lerp(CameraPitch, -6.f, TheatreCameraBlend);
    const double AnchorZ = bContinueCartFromCastle ? GetActorLocation().Z : SpawnPoint.Z;
    SideCamera->SetWorldLocation(FVector(FollowX, SpawnPoint.Y + Distance, AnchorZ + Height));
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







