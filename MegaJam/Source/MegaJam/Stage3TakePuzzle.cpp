#include "Stage3TakePuzzle.h"

#include "Camera/PlayerCameraManager.h"
#include "Components/CapsuleComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "DirectorCutGraphics.h"
#include "Engine/GameViewportClient.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"
#include "Stage2ShadowPrototype.h"
#include "Styling/CoreStyle.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"

#define LOCTEXT_NAMESPACE "Stage3TakePuzzle"

namespace
{
    constexpr float SampleInterval = 1.f / 30.f;
    constexpr float PlateHeightTolerance = 28.f;
}

AStage3TakePuzzle::AStage3TakePuzzle()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickGroup = TG_PostUpdateWork;
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Origin"));

    GhostMesh = CreateDefaultSubobject<UPoseableMeshComponent>(TEXT("ReplayDragon"));
    GhostMesh->SetupAttachment(RootComponent);
    GhostMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    GhostMesh->SetGenerateOverlapEvents(false);
    GhostMesh->SetCastShadow(false);
    GhostMesh->SetVisibility(false);

    GhostLabel = CreateDefaultSubobject<UTextRenderComponent>(TEXT("ReplayLabel"));
    GhostLabel->SetupAttachment(RootComponent);
    GhostLabel->SetHorizontalAlignment(EHTA_Center);
    GhostLabel->SetTextRenderColor(FColor(112, 237, 255));
    GhostLabel->SetWorldSize(22.f);
    GhostLabel->SetText(LOCTEXT("ReplayLabel", "TAKE 1"));
    GhostLabel->SetVisibility(false);
}

void AStage3TakePuzzle::BeginPlay()
{
    Super::BeginPlay();
    SetPlates(false, false);
    if (UGameViewportClient* Viewport = GetWorld()->GetGameViewport())
    {
        Overlay = SNew(SOverlay).Visibility(EVisibility::HitTestInvisible)
            + SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Top).Padding(18.f, 24.f)
            [
                SNew(STextBlock)
                .Text_Lambda([this] { return Hint; })
                .ColorAndOpacity(FLinearColor(1.f, .86f, .60f))
                .Font(FCoreStyle::GetDefaultFontStyle("Bold", 16))
                .ShadowOffset(FVector2D(1.f, 2.f))
                .ShadowColorAndOpacity(FLinearColor::Black)
                .Justification(ETextJustify::Center)
                .Visibility_Lambda([this]
                {
                    return Hint.IsEmpty() ? EVisibility::Collapsed : EVisibility::HitTestInvisible;
                })
            ];
        Viewport->AddViewportWidgetContent(Overlay.ToSharedRef(), 7);
    }
}

void AStage3TakePuzzle::EndPlay(EEndPlayReason::Type Reason)
{
    if (Overlay && GetWorld()->GetGameViewport())
    {
        GetWorld()->GetGameViewport()->RemoveViewportWidgetContent(Overlay.ToSharedRef());
    }
    Overlay.Reset();
    Super::EndPlay(Reason);
}

void AStage3TakePuzzle::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    ACharacter* Character = UGameplayStatics::GetPlayerCharacter(this, 0);
    APlayerController* Controller = Character ? Cast<APlayerController>(Character->GetController()) : nullptr;
    if (!Controller)
    {
        SetHint(FText::GetEmpty());
        return;
    }

    const FVector LocalPosition = GetActorTransform().InverseTransformPosition(Character->GetActorLocation());
    if (LocalPosition.X < MinRoomX || LocalPosition.X > MaxRoomX)
    {
        if (!bCompleted)
        {
            if (Phase == EStage3TakePhase::Recording)
            {
                Frames.Reset();
                RecordedSeconds = 0.f;
                Phase = EStage3TakePhase::Idle;
            }
            else if (Phase == EStage3TakePhase::Playing)
            {
                Phase = EStage3TakePhase::ReplayReady;
                SetGhostVisible(false);
            }
            SetPlates(false, false);
        }
        SetHint(FText::GetEmpty());
        return;
    }

    if (const auto* DirectorController = Cast<ADirectorCutPlayerController>(Controller);
        DirectorController && DirectorController->IsGraphicsMenuOpen())
    {
        SetHint(FText::GetEmpty());
        return;
    }

    if (bCompleted)
    {
        SetHint(LocalPosition.X <= RightMark.X + PlateHalfWidth
            ? LOCTEXT("Complete", "TWO TAKES APPROVED")
            : FText::GetEmpty());
        return;
    }

    const bool bOnLeft = IsOnPlate(*Character, LocalPosition, LeftMark);
    const bool bOnRight = IsOnPlate(*Character, LocalPosition, RightMark);
    const bool bNearCamera = IsNearCamera(LocalPosition);
    const bool bInteract = Controller->WasInputKeyJustPressed(EKeys::E);
    MessageSeconds = FMath::Max(0.f, MessageSeconds - DeltaSeconds);

    if (Phase != EStage3TakePhase::Idle && Controller->WasInputKeyJustPressed(EKeys::R))
    {
        Phase = EStage3TakePhase::Idle;
        RecordedSeconds = 0.f;
        Frames.Reset();
        SetGhostVisible(false);
        SetPlates(false, false);
        RewindPlayer(*Character);
        MessageSeconds = 1.4f;
        SetHint(LOCTEXT("Reset", "CAMERA RESET"));
        return;
    }

    if (Phase == EStage3TakePhase::Recording)
    {
        RecordedSeconds = FMath::Min(RecordedSeconds + DeltaSeconds, MaxRecordingSeconds);
        PlateHoldDuringRecording = bOnLeft ? PlateHoldDuringRecording + DeltaSeconds : 0.f;
        SetPlates(bOnLeft, false);
        if (RecordedSeconds - Frames.Last().Time >= SampleInterval)
        {
            SampleFrame(*Character, bOnLeft);
        }
        const float DesiredHold = RequiredOverlapSeconds + .45f;
        if (bInteract || RecordedSeconds >= MaxRecordingSeconds)
        {
            if (PlateHoldDuringRecording >= DesiredHold)
            {
                SampleFrame(*Character, true);
                StartPlayback(*Character);
                return;
            }
            if (RecordedSeconds >= MaxRecordingSeconds)
            {
                Phase = EStage3TakePhase::Idle;
                Frames.Reset();
                RecordedSeconds = 0.f;
                RewindPlayer(*Character);
                SetPlates(false, false);
                MessageSeconds = 2.4f;
                SetHint(LOCTEXT("TakeExpired", "TAKE 1 EXPIRED"));
                return;
            }
        }
        SetHint(FText::Format(bOnLeft && PlateHoldDuringRecording >= DesiredHold
            ? LOCTEXT("FinishTake", "REC  {0}s    •    TAKE READY    •    R  Reset")
            : LOCTEXT("FindLeft", "REC  {0}s    •    R  Reset"),
            FText::AsNumber(FMath::CeilToInt(MaxRecordingSeconds - RecordedSeconds))));
        return;
    }

    if (Phase == EStage3TakePhase::Playing)
    {
        UpdatePlayback(DeltaSeconds, bOnRight);
        return;
    }

    SetPlates(bOnLeft, bOnRight);
    if (Phase == EStage3TakePhase::ReplayReady)
    {
        if (bNearCamera && bInteract)
        {
            StartPlayback(*Character);
            return;
        }
        SetHint(LOCTEXT("Retry", "TAKE 2 MISSED    •    R  Reset"));
        return;
    }
    if (bNearCamera && bInteract)
    {
        StartRecording(*Character);
        return;
    }
    if (MessageSeconds <= 0.f)
    {
        SetHint(FText::GetEmpty());
    }
}

bool AStage3TakePuzzle::IsOnPlate(const ACharacter& Character, const FVector& LocalPosition, const FVector& Mark) const
{
    const float FootZ = LocalPosition.Z - Character.GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
    return Character.GetCharacterMovement()->IsMovingOnGround()
        && FMath::Abs(LocalPosition.X - Mark.X) <= PlateHalfWidth
        && FMath::Abs(LocalPosition.Y - Mark.Y) <= PlateHalfDepth
        && FMath::Abs(FootZ - Mark.Z) <= PlateHeightTolerance;
}

bool AStage3TakePuzzle::IsNearCamera(const FVector& LocalPosition) const
{
    return LocalPosition.X >= MinRoomX && LocalPosition.X <= MaxRoomX
        && FVector::Dist2D(LocalPosition, CameraMark) <= ConsoleDistance
        && FMath::Abs(LocalPosition.Z - CameraMark.Z) <= 160.f;
}

bool AStage3TakePuzzle::CanUseCamera(const ACharacter& Character) const
{
    return !bCompleted && (Phase == EStage3TakePhase::Idle || Phase == EStage3TakePhase::ReplayReady)
        && IsNearCamera(GetActorTransform().InverseTransformPosition(Character.GetActorLocation()));
}

bool AStage3TakePuzzle::CanFinishRecording(const ACharacter& Character) const
{
    return Phase == EStage3TakePhase::Recording && PlateHoldDuringRecording >= RequiredOverlapSeconds + .45f
        && IsOnPlate(Character, GetActorTransform().InverseTransformPosition(Character.GetActorLocation()), LeftMark);
}

void AStage3TakePuzzle::StartRecording(ACharacter& Character)
{
    MessageSeconds = 0.f;
    RecordedSeconds = 0.f;
    PlateHoldDuringRecording = 0.f;
    Frames.Reset();
    Frames.Reserve(FMath::CeilToInt(MaxRecordingSeconds / SampleInterval) + 2);
    Phase = EStage3TakePhase::Recording;
    SampleFrame(Character, false);
    SetHint(LOCTEXT("Recording", "TAKE 1 RECORDING    •    R  Reset"));
}

void AStage3TakePuzzle::SampleFrame(ACharacter& Character, bool bOnLeftPlate)
{
    USkeletalMeshComponent* Mesh = Character.GetMesh();
    FRecordedFrame& Frame = Frames.AddDefaulted_GetRef();
    Frame.Time = RecordedSeconds;
    Frame.MeshTransform = Mesh->GetComponentTransform().GetRelativeTransform(GetActorTransform());
    Frame.Bones = Mesh->GetBoneSpaceTransforms();
    Frame.bOnLeftPlate = bOnLeftPlate;
}

void AStage3TakePuzzle::StartPlayback(ACharacter& Character)
{
    if (Frames.IsEmpty())
    {
        return;
    }

    USkeletalMeshComponent* Source = Character.GetMesh();
    GhostMesh->SetSkinnedAssetAndUpdate(Source->GetSkeletalMeshAsset());
    for (int32 Slot = 0; Slot < Source->GetNumMaterials(); ++Slot)
    {
        GhostMesh->SetMaterial(Slot, GhostMaterial ? GhostMaterial.Get() : Source->GetMaterial(Slot));
    }

    PlaybackIndex = 0;
    PlaybackSeconds = 0.f;
    OverlapSeconds = 0.f;
    Phase = EStage3TakePhase::Playing;
    SetPlates(false, false);
    RewindPlayer(Character);
    ShowReplayFrame();
    SetGhostVisible(true);
    SetHint(LOCTEXT("Playback", "TAKE 2 PLAYING    •    R  Reset"));
}

void AStage3TakePuzzle::UpdatePlayback(float DeltaSeconds, bool bPlayerOnRight)
{
    const float PreviousSeconds = PlaybackSeconds;
    PlaybackSeconds = FMath::Min(PlaybackSeconds + DeltaSeconds, RecordedSeconds);
    bool bRecordedOnLeft = Frames[PlaybackIndex].bOnLeftPlate;
    float SegmentStart = PreviousSeconds;
    while (Frames.IsValidIndex(PlaybackIndex + 1) && Frames[PlaybackIndex + 1].Time <= PlaybackSeconds)
    {
        const float Boundary = Frames[PlaybackIndex + 1].Time;
        OverlapSeconds = bRecordedOnLeft && bPlayerOnRight ? OverlapSeconds + Boundary - SegmentStart : 0.f;
        if (OverlapSeconds >= RequiredOverlapSeconds)
        {
            break;
        }
        ++PlaybackIndex;
        SegmentStart = Boundary;
        bRecordedOnLeft = Frames[PlaybackIndex].bOnLeftPlate;
    }
    if (OverlapSeconds < RequiredOverlapSeconds)
    {
        OverlapSeconds = bRecordedOnLeft && bPlayerOnRight ? OverlapSeconds + PlaybackSeconds - SegmentStart : 0.f;
    }

    ShowReplayFrame();
    SetPlates(bRecordedOnLeft, bPlayerOnRight);
    if (OverlapSeconds >= RequiredOverlapSeconds)
    {
        bCompleted = true;
        Phase = EStage3TakePhase::Solved;
        if (IsValid(ExitDoor))
        {
            ExitDoor->OpenDoor();
        }
        SetGhostVisible(false);
        return;
    }

    if (PlaybackSeconds >= RecordedSeconds)
    {
        Phase = EStage3TakePhase::ReplayReady;
        SetGhostVisible(false);
        SetPlates(false, bPlayerOnRight);
        SetHint(LOCTEXT("Retry", "TAKE 2 MISSED    •    R  Reset"));
        return;
    }
    SetHint(bRecordedOnLeft && bPlayerOnRight
        ? LOCTEXT("HoldBoth", "BOTH MARKS ACTIVE")
        : LOCTEXT("Playback", "TAKE 2 PLAYING    •    R  Reset"));
}

void AStage3TakePuzzle::RewindPlayer(ACharacter& Character) const
{
    const FVector Spawn = GetActorTransform().TransformPosition(CameraMark)
        + FVector(0.f, 0.f, Character.GetCapsuleComponent()->GetScaledCapsuleHalfHeight() + 3.f);
    Character.StopJumping();
    Character.GetCharacterMovement()->StopMovementImmediately();
    Character.SetBase(static_cast<UPrimitiveComponent*>(nullptr));
    Character.TeleportTo(Spawn, Character.GetActorRotation(), false, true);
    Character.GetCharacterMovement()->SetMovementMode(MOVE_Falling);
    if (auto* Controller = Cast<APlayerController>(Character.GetController()); Controller && Controller->PlayerCameraManager)
    {
        Controller->PlayerCameraManager->StartCameraFade(.55f, 0.f, .28f, FLinearColor::Black, false, false);
    }
}

void AStage3TakePuzzle::ShowReplayFrame()
{
    const FRecordedFrame& Current = Frames[PlaybackIndex];
    const FRecordedFrame& Next = Frames.IsValidIndex(PlaybackIndex + 1) ? Frames[PlaybackIndex + 1] : Current;
    const float Duration = Next.Time - Current.Time;
    const float Alpha = Duration > KINDA_SMALL_NUMBER
        ? FMath::Clamp((PlaybackSeconds - Current.Time) / Duration, 0.f, 1.f)
        : 0.f;

    FTransform Pose;
    Pose.Blend(Current.MeshTransform, Next.MeshTransform, Alpha);
    GhostMesh->SetRelativeTransform(Pose);
    if (Current.Bones.Num() == GhostMesh->BoneSpaceTransforms.Num() && Current.Bones.Num() == Next.Bones.Num())
    {
        for (int32 Bone = 0; Bone < Current.Bones.Num(); ++Bone)
        {
            GhostMesh->BoneSpaceTransforms[Bone].Blend(Current.Bones[Bone], Next.Bones[Bone], Alpha);
        }
        GhostMesh->RefreshBoneTransforms();
    }

    GhostLabel->SetRelativeLocation(Pose.GetLocation() + FVector(0.f, 0.f, 137.f));
    GhostLabel->SetRelativeRotation(FRotator(0.f, 90.f, 0.f));
}

void AStage3TakePuzzle::SetGhostVisible(bool bVisible)
{
    GhostMesh->SetVisibility(bVisible);
    GhostLabel->SetVisibility(bVisible);
}

void AStage3TakePuzzle::SetPlates(bool bLeft, bool bRight)
{
    bLeftPressed = bLeft;
    bRightPressed = bRight;
    if (IsValid(LeftLamp))
    {
        LeftLamp->SetActorHiddenInGame(!bLeft);
    }
    if (IsValid(RightLamp))
    {
        RightLamp->SetActorHiddenInGame(!bRight);
    }
}

void AStage3TakePuzzle::SetHint(const FText& Text)
{
    Hint = Text;
}

#undef LOCTEXT_NAMESPACE
