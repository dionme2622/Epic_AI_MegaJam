#include "Stage4ShadowStandIn.h"

#include "Camera/PlayerCameraManager.h"
#include "Components/CapsuleComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "DirectorCutGraphics.h"
#include "DirectorCutTest.h"
#include "Engine/GameViewportClient.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"

#define LOCTEXT_NAMESPACE "Stage4ShadowStandIn"

namespace
{
    constexpr double WallY = -271.;
    constexpr float FerryNear = 333.f;
    constexpr float FerryFar = 816.f;
    constexpr float BridgeStowed = -176.f;
    constexpr float BridgeRaised = 84.f;
    const FVector FirstLamp(95., 490., 192.);
    const FVector SecondLamp(1050., 470., 254.);
    const FVector CheckpointMarks[] = {{155.,0.,0.}, {1100.,0.,0.}, {1850.,0.,118.}};
    bool In(double X, double Left, double Right) { return X >= Left && X <= Right; }
}

AStage4ShadowStandIn::AStage4ShadowStandIn()
{
    PrimaryActorTick.bCanEverTick = true;
    // Set the platform transform before character movement evaluates its base.
    PrimaryActorTick.TickGroup = TG_PrePhysics;
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Origin"));
}

void AStage4ShadowStandIn::BeginPlay()
{
    Super::BeginPlay();
    for (UStaticMeshComponent* Lamp : SwitchLamps)
    {
        LampOffMaterials.Add(Lamp ? Lamp->GetMaterial(0) : nullptr);
    }
    if (UGameViewportClient* Viewport = GetWorld()->GetGameViewport())
    {
        Overlay = SNew(SOverlay).Visibility(EVisibility::HitTestInvisible)
            + SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Bottom).Padding(14.f, 13.f)
            [
                SNew(SBorder)
                .Padding(FMargin(18.f, 9.f))
                .Visibility_Lambda([this] { return Hint.IsEmpty() ? EVisibility::Collapsed : EVisibility::HitTestInvisible; })
                .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                .BorderBackgroundColor(FLinearColor(.047f, .023f, .033f, .95f))
                [
                    SNew(SBox).WidthOverride(570.f)
                    [
                        SNew(STextBlock)
                        .Text_Lambda([this] { return Hint; })
                        .ColorAndOpacity(FLinearColor(.98f,.83f,.57f))
                        .Font(FCoreStyle::GetDefaultFontStyle("Regular", 15))
                        .Justification(ETextJustify::Center)
                        .WrapTextAt(560.f)
                    ]
                ]
            ];
        Viewport->AddViewportWidgetContent(Overlay.ToSharedRef(), 7);
    }
}

bool AStage4ShadowStandIn::OwnsRecovery(double WorldX) const
{
    return In(WorldX - GetActorLocation().X, -35., 2240.);
}

FVector AStage4ShadowStandIn::Project(const FVector& Point, const FVector& Light) const
{
    const double Stretch = (WallY - Light.Y) / (Point.Y - Light.Y);
    return Light + (Point - Light) * Stretch;
}

void AStage4ShadowStandIn::UpdateShadow(ADirectorCutDragon& Dragon, const FVector& Light, bool bVisible)
{
    USkeletalMeshComponent* Mesh = Dragon.GetMesh();
    if (bVisible && !Shadow && ShadowMaterial && Mesh && Mesh->GetSkeletalMeshAsset())
    {
        Shadow = NewObject<UPoseableMeshComponent>(this, TEXT("StandInWallShadow"));
        Shadow->SetupAttachment(RootComponent);
        Shadow->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Shadow->SetCastShadow(false);
        Shadow->bAffectDistanceFieldLighting = false;
        Shadow->SetSkeletalMesh(Mesh->GetSkeletalMeshAsset());
        for (int32 Slot = 0; Slot < Shadow->GetNumMaterials(); ++Slot)
        {
            Shadow->SetMaterial(Slot, ShadowMaterial);
        }
        Shadow->RegisterComponent();
    }
    if (!Shadow)
    {
        return;
    }
    Shadow->SetVisibility(bVisible);
    if (!bVisible)
    {
        return;
    }

    const FTransform Stage = GetActorTransform();
    const FVector MeshPosition = Stage.InverseTransformPosition(Mesh->GetComponentLocation());
    const FVector Projected = Project(MeshPosition, Light);
    const double Magnification = (WallY - Light.Y) / (MeshPosition.Y - Light.Y);
    const FVector MeshScale = Mesh->GetComponentScale();
    Shadow->SetRelativeTransform(FTransform(Stage.InverseTransformRotation(Mesh->GetComponentQuat()),
        Projected, MeshScale * FVector(Magnification, .012, Magnification)));
    Shadow->CopyPoseFromSkeletalComponent(Mesh);
}

void AStage4ShadowStandIn::MoveMechanism(UStaticMeshComponent* Collider, UStaticMeshComponent* Art, const FVector& Delta)
{
    if (Collider)
    {
        Collider->AddWorldOffset(Delta);
    }
    if (Art && Art != Collider)
    {
        Art->AddWorldOffset(Delta);
    }
}

void AStage4ShadowStandIn::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    auto* Dragon = Cast<ADirectorCutDragon>(UGameplayStatics::GetPlayerCharacter(this, 0));
    if (!Dragon)
    {
        return;
    }
    const FVector P = GetActorTransform().InverseTransformPosition(Dragon->GetActorLocation());
    const bool bInPuzzle = OwnsRecovery(Dragon->GetActorLocation().X);
    const auto* Graphics = GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>();
    const auto* Controller = Cast<ADirectorCutPlayerController>(Dragon->GetController());
    const bool bShadows = !Graphics || Graphics->IsHigh(EDirectorCutGraphicsOption::Shadows);
    const bool bGrounded = Dragon->GetCharacterMovement()->IsMovingOnGround();
    const bool bOnFerry = Ferry && Dragon->GetMovementBase() == Ferry;
    const bool bWest = P.X < 905.;
    const FVector& Light = bWest ? FirstLamp : SecondLamp;
    const FVector Mark = Project(P - FVector(0., 0., 13.), Light);

    // The projected center of the body is the pressure point. Its coordinates
    // use the same source and receiver plane as the moving silhouette.
    bCallSwitch = bShadows && bWest && In(Mark.X, 158., 525.) && In(Mark.Z, -45., 130.);
    bLowSwitch = bShadows && !bWest && In(Mark.X, 1190., 1370.) && In(Mark.Z, -150., -35.);
    bHighSwitch = bShadows && !bWest && In(Mark.X, 1320., 1575.) && In(Mark.Z, -33., 80.);
    const bool bOnHighMark = bGrounded && P.Z > 121. && In(P.X, 1210., 1380.);
    UpdateShadow(*Dragon, Light, bShadows && bInPuzzle && In(P.X, 76., 1500.));

    if (bOnFerry && !bShadows && FerryX >= FerryNear && FerryX <= FerryFar - 1.f)
    {
        bFerryReturning = true;
        bFerryCarrying = true;
    }
    if (!bOnFerry && FerryX >= FerryFar - 1.f)
    {
        bFerryReturning = false;
    }

    const float PreviousX = FerryX;
    const float FerryTarget = !bFerryReturning && bCallSwitch ? FerryNear : FerryFar;
    FerryX = FMath::FInterpConstantTo(FerryX, FerryTarget, DeltaSeconds, 225.f);
    if (FerryX != PreviousX)
    {
        MoveMechanism(Ferry, FerryArt, GetActorTransform().TransformVectorNoScale({FerryX - PreviousX, 0., 0.}));
    }

    if (bHighSwitch && bOnHighMark && !bLastShadows)
    {
        bRaisedBridge = true;
    }
    if (!bShadows && P.X < 1410.)
    {
        bRaisedBridge = false;
    }
    bLastShadows = bShadows;
    const float TargetZ = bRaisedBridge ? BridgeRaised : bLowSwitch && !bHighSwitch ? 3.f : BridgeStowed;
    const float PreviousZ = BridgeZ;
    BridgeZ = FMath::FInterpConstantTo(BridgeZ, TargetZ, DeltaSeconds, 260.f);
    if (BridgeZ != PreviousZ)
    {
        MoveMechanism(Bridge, BridgeArt, GetActorTransform().TransformVectorNoScale({0., 0., BridgeZ - PreviousZ}));
    }

    const bool Pressed[] = {bCallSwitch, bLowSwitch, bHighSwitch};
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Pressed); ++Index)
    {
        if (SwitchLamps.IsValidIndex(Index) && SwitchLamps[Index])
        {
            UMaterialInterface* Material = Pressed[Index] && LampOnMaterial ? LampOnMaterial.Get() : LampOffMaterials[Index].Get();
            if (SwitchLamps[Index]->GetMaterial(0) != Material)
            {
                SwitchLamps[Index]->SetMaterial(0, Material);
            }
        }
    }

    if (!bInPuzzle)
    {
        Hint = FText::GetEmpty();
        return;
    }
    if (P.Z < -180.)
    {
        Respawn(*Dragon);
        return;
    }
    if (bGrounded && In(P.X, 70., 230.) && Checkpoint == 0)
    {
        SetCheckpoint(*Dragon, 0);
    }
    else if (bFerryCarrying && bGrounded && In(P.X, 926., 1200.) && Checkpoint < 1)
    {
        SetCheckpoint(*Dragon, 1);
    }
    else if (Checkpoint == 1 && bRaisedBridge && bGrounded && P.X >= 1710.)
    {
        bReachedExhibit = true;
        SetCheckpoint(*Dragon, 2);
    }
    if (Controller && Controller->IsGraphicsMenuOpen())
    {
        Hint = FText::GetEmpty();
    }
    else
    {
        UpdateHint(P.X, bShadows, bOnFerry);
    }
}

void AStage4ShadowStandIn::SetCheckpoint(ADirectorCutDragon& Dragon, int32 Index)
{
    Checkpoint = Index;
    const float HalfHeight = Dragon.GetCapsuleComponent()->GetScaledCapsuleHalfHeight() + 2.f;
    Dragon.SetPuzzleRespawnPoint(GetActorTransform().TransformPosition(CheckpointMarks[Index] + FVector(0.,0.,HalfHeight)));
}

void AStage4ShadowStandIn::Respawn(ADirectorCutDragon& Dragon)
{
    SetCheckpoint(Dragon, Checkpoint);
    const FVector Position = GetActorTransform().TransformPosition(CheckpointMarks[Checkpoint] +
        FVector(0., 0., Dragon.GetCapsuleComponent()->GetScaledCapsuleHalfHeight() + 3.f));
    Dragon.StopJumping();
    Dragon.GetCharacterMovement()->StopMovementImmediately();
    Dragon.SetBase(static_cast<UPrimitiveComponent*>(nullptr));
    Dragon.TeleportTo(Position, Dragon.GetActorRotation(), false, true);
    Dragon.GetCharacterMovement()->SetMovementMode(MOVE_Falling);
    if (auto* Controller = Cast<APlayerController>(Dragon.GetController()); Controller && Controller->PlayerCameraManager)
    {
        Controller->PlayerCameraManager->StartCameraFade(.65f, 0.f, .35f, FLinearColor::Black, false, false);
    }
}

void AStage4ShadowStandIn::UpdateHint(double X, bool bShadows, bool bOnFerry)
{
    if (bOnFerry && X < 740.)
    {
        Hint = LOCTEXT("Release", "SHADOW STAND-IN\nStay aboard and turn Shadows OFF to release the wall switch.");
    }
    else if (X < 280.)
    {
        Hint = bShadows
            ? LOCTEXT("Call", "SHADOW STAND-IN\nStand on the brass mark. Your shadow calls the ferry.")
            : LOCTEXT("Power", "SHADOW STAND-IN\nStand on the brass mark and turn Shadows ON (High).");
    }
    else if (bOnFerry)
    {
        Hint = LOCTEXT("LeaveFerry", "Step off when the ferry reaches the far ledge.");
    }
    else if (In(X, 930., 1200.) && Checkpoint >= 1)
    {
        Hint = LOCTEXT("Lower", "CHECKPOINT\nTry the lower switch from the floor. Watch what changes when you jump.");
    }
    else if (In(X, 1210., 1380.) && Checkpoint >= 1)
    {
        Hint = bRaisedBridge ? LOCTEXT("Cross", "HIGH SWITCH LATCHED\nCross the raised bridge.")
            : bShadows ? LOCTEXT("UpperRelease", "At the raised brass mark, switch Shadows OFF, then ON.")
                       : LOCTEXT("Upper", "At the raised brass mark, switch Shadows ON to latch the high switch.");
    }
    else
    {
        Hint = FText::GetEmpty();
    }
}

void AStage4ShadowStandIn::EndPlay(EEndPlayReason::Type Reason)
{
    if (Overlay && GetWorld() && GetWorld()->GetGameViewport())
    {
        GetWorld()->GetGameViewport()->RemoveViewportWidgetContent(Overlay.ToSharedRef());
    }
    Overlay.Reset();
    Super::EndPlay(Reason);
}

#undef LOCTEXT_NAMESPACE
