#include "FocusPropPuzzle.h"
#include "DirectorCutGraphics.h"
#include "Stage2ShadowPrototype.h"
#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "InputCoreTypes.h"
#include "Widgets/SOverlay.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Images/SImage.h"
#include "Styling/CoreStyle.h"

AFocusPropPuzzle::AFocusPropPuzzle()
{
    PrimaryActorTick.bCanEverTick = true;
    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root")); SetRootComponent(Root);
    NearPiece = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("NearPiece")); NearPiece->SetupAttachment(Root);
    NearPiece->SetMobility(EComponentMobility::Movable); NearPiece->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    NearPiece->SetRelativeLocation(FVector(300, 200, 300));
    FarPiece = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("FarPiece")); FarPiece->SetupAttachment(Root);
    FarPiece->SetMobility(EComponentMobility::Movable); FarPiece->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    FarPiece->SetRelativeLocation(FVector(650, -200, 300));
    PuzzleCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("PuzzleCamera")); PuzzleCamera->SetupAttachment(Root);
    PuzzleCamera->SetRelativeLocation(FVector(500,1500,300)); PuzzleCamera->SetRelativeRotation(FRotator(0,-90,0));
    PuzzleCamera->SetFieldOfView(35.f);
    PuzzleCamera->PostProcessBlendWeight = 1.f;
    auto& PP = PuzzleCamera->PostProcessSettings;
    PP.bOverride_DepthOfFieldFocalDistance = true;
    PP.bOverride_DepthOfFieldFstop = true;
    PP.DepthOfFieldFocalDistance = 1300.f;
    PP.DepthOfFieldFstop = .5f;
}
void AFocusPropPuzzle::BeginPlay()
{
    Super::BeginPlay();
    InitialNearPosition = NearPiece->GetRelativeLocation();
    InitialFarPosition = FarPiece->GetRelativeLocation();
}
void AFocusPropPuzzle::EndPlay(const EEndPlayReason::Type Reason) { LeavePuzzle(); Super::EndPlay(Reason); }
FText AFocusPropPuzzle::GetStatusText() const
{
    if (bCompleting) return FText::FromString(TEXT("KEY ALIGNED  -  OPENING THE EXIT"));
    if (UGameplayStatics::GetCurrentLevelName(this, true) == TEXT("Stage3_"))
    {
        if (IsAligned()) return FText::FromString(TEXT("KEY ALIGNED"));
        return FText::FromString(bNearSelected ? TEXT("NEAR PIECE SELECTED") : TEXT("FAR PIECE SELECTED"));
    }
    if (IsAligned()) return FText::FromString(TEXT("KEY ALIGNED  |  ENTER: CONFIRM   R: RESET   E: LEAVE"));
    return FText::FromString(bNearSelected ? TEXT("NEAR  |  A/D: MOVE   SHIFT: FINE   Q: FOCUS   R: RESET   E: LEAVE") : TEXT("FAR  |  A/D: MOVE   SHIFT: FINE   Q: FOCUS   R: RESET   E: LEAVE"));
}
FText AFocusPropPuzzle::GetProgressText() const
{
    return FText::FromString(FString::Printf(TEXT("ALIGN THE TWO KEY PIECES     %d%%"), FMath::RoundToInt(GetAlignmentProgress()*100.f)));
}
FSlateColor AFocusPropPuzzle::GetProgressColor() const { return IsAligned() ? FSlateColor(FLinearColor(.35f,1.f,.56f,1.f)) : FSlateColor(FLinearColor(1.f,.76f,.35f,1.f)); }
void AFocusPropPuzzle::EnterPuzzle()
{
    APlayerController* PC = UGameplayStatics::GetPlayerController(this,0);
    APawn* Pawn = PC ? PC->GetPawn() : nullptr;
    if (!PC || !Pawn || bActive || bSolved || FVector::Dist2D(Pawn->GetActorLocation(), GetActorLocation()) > InteractDistance) return;
    PreviousView = PC->GetViewTarget(); bActive = true;
    PC->SetIgnoreMoveInput(true);
    if (ACharacter* C = Cast<ACharacter>(Pawn)) C->GetCharacterMovement()->StopMovementImmediately();
    PC->SetViewTarget(this);
    SelectNear(true);
    if (GEngine && GEngine->GameViewport)
    {
        const bool bCampaign = UGameplayStatics::GetCurrentLevelName(this, true) == TEXT("Stage3_");
        Overlay = SNew(SOverlay)
        .Visibility_Lambda([this]
        {
            const auto* Director = Cast<ADirectorCutPlayerController>(UGameplayStatics::GetPlayerController(this, 0));
            return Director && Director->IsGraphicsMenuOpen() ? EVisibility::Collapsed : EVisibility::HitTestInvisible;
        })
        + SOverlay::Slot().HAlign(HAlign_Center).VAlign(bCampaign ? VAlign_Bottom : VAlign_Top).Padding(15)
        [ SNew(SBorder).Padding(14).BorderBackgroundColor(FLinearColor(.025f,.018f,.04f,.94f))
          [ SNew(SVerticalBox)
            + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0,0,0,7)
            [ SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Bold",20))
              .ColorAndOpacity_Lambda([this]() { return GetProgressColor(); }).Text_Lambda([this]() { return GetProgressText(); }) ]
            + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)
            [ SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",16)).ColorAndOpacity(FLinearColor::White)
              .Text_Lambda([this]() { return GetStatusText(); }) ] ] ];
        GEngine->GameViewport->AddViewportWidgetContent(Overlay.ToSharedRef(), 50);
    }
}
void AFocusPropPuzzle::LeavePuzzle()
{
    if (!bActive) return;
    if (APlayerController* PC = UGameplayStatics::GetPlayerController(this,0))
    {
        PC->SetIgnoreMoveInput(false);
        if (PreviousView.IsValid()) PC->SetViewTarget(PreviousView.Get());
        else if (PC->GetPawn()) PC->SetViewTarget(PC->GetPawn());
    }
    if (Overlay.IsValid() && GEngine && GEngine->GameViewport) GEngine->GameViewport->RemoveViewportWidgetContent(Overlay.ToSharedRef());
    Overlay.Reset(); bActive = false;
}
void AFocusPropPuzzle::SelectNear(bool bNear)
{
    bNearSelected = bNear;
    const FVector Cam = PuzzleCamera->GetComponentLocation();
    const FVector Pos = bNear ? NearPiece->GetComponentLocation() : FarPiece->GetComponentLocation();
    DesiredFocusDistance = FVector::DotProduct(Pos-Cam, PuzzleCamera->GetForwardVector());
}
bool AFocusPropPuzzle::IsAligned() const
{
    const FTransform Inv = PuzzleCamera->GetComponentTransform().Inverse();
    const FVector Near = Inv.TransformPosition(NearPiece->GetComponentTransform().TransformPosition(FVector(50,0,0)));
    const FVector Far = Inv.TransformPosition(FarPiece->GetComponentLocation());
    if (Near.X <= 1.f || Far.X <= 1.f) return false;
    return FMath::Abs(Near.Y/Near.X - Far.Y/Far.X) <= FMath::Max(AlignmentTolerance, 0.f)
        && FMath::Abs(Near.Z/Near.X - Far.Z/Far.X) <= FMath::Max(AlignmentTolerance, 0.f);
}
float AFocusPropPuzzle::GetAlignmentProgress() const
{
    const FTransform Inv = PuzzleCamera->GetComponentTransform().Inverse();
    const FVector Near = Inv.TransformPosition(NearPiece->GetComponentTransform().TransformPosition(FVector(50,0,0)));
    const FVector Far = Inv.TransformPosition(FarPiece->GetComponentLocation());
    if (Near.X <= 1.f || Far.X <= 1.f) return 0.f;
    const float Error = FVector2D::Distance(FVector2D(Near.Y/Near.X,Near.Z/Near.X), FVector2D(Far.Y/Far.X,Far.Z/Far.X));
    if (IsAligned()) return 1.f;
    return FMath::Clamp(1.f - Error / .22f, 0.f, .99f);
}
void AFocusPropPuzzle::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    APlayerController* PC = UGameplayStatics::GetPlayerController(this,0);
    if (!PC) return;
    if (bCompleting)
    {
        FinishTime -= DeltaSeconds;
        if (FinishTime <= 0.f) { bCompleting = false; if (IsValid(ExitDoor)) ExitDoor->OpenDoor(); OnSolved(); LeavePuzzle(); }
        return;
    }
    if (const auto* Director = Cast<ADirectorCutPlayerController>(PC))
        if (Director->IsGraphicsMenuOpen()) return;
    if (PC->WasInputKeyJustPressed(EKeys::E)) { if (bActive) LeavePuzzle(); else EnterPuzzle(); return; }
    if (!bActive) return;
    if (PC->WasInputKeyJustPressed(EKeys::Q)) SelectNear(!bNearSelected);
    if (PC->WasInputKeyJustPressed(EKeys::One)) SelectNear(true);
    if (PC->WasInputKeyJustPressed(EKeys::Two)) SelectNear(false);
    if (PC->WasInputKeyJustPressed(EKeys::R))
    {
        NearPiece->SetRelativeLocation(InitialNearPosition); FarPiece->SetRelativeLocation(InitialFarPosition); SelectNear(true);
    }
    PuzzleCamera->PostProcessSettings.DepthOfFieldFocalDistance = FMath::FInterpTo(PuzzleCamera->PostProcessSettings.DepthOfFieldFocalDistance, DesiredFocusDistance, DeltaSeconds, FocusTransitionSpeed);
    const float Axis = (PC->IsInputKeyDown(EKeys::D) || PC->IsInputKeyDown(EKeys::Right) ? 1.f : 0.f) - (PC->IsInputKeyDown(EKeys::A) || PC->IsInputKeyDown(EKeys::Left) ? 1.f : 0.f);
    if (!FMath::IsNearlyZero(Axis))
    {
        auto* Piece = bNearSelected ? NearPiece.Get() : FarPiece.Get();
        const float Precision = PC->IsInputKeyDown(EKeys::LeftShift) || PC->IsInputKeyDown(EKeys::RightShift) ? .3f : 1.f;
        FVector P = Piece->GetRelativeLocation(); P.X = FMath::Clamp(P.X + Axis * PieceSpeed * Precision * DeltaSeconds, 150.f, 850.f); Piece->SetRelativeLocation(P);
    }
    if (PC->WasInputKeyJustPressed(EKeys::Enter) && IsAligned())
    {
        bSolved = true; bCompleting = true; FinishTime = FMath::Max(CompletionDelay, 0.f);
        // Show the complete key in focus before returning to the level camera.
        auto& PP = PuzzleCamera->PostProcessSettings;
        PP.bOverride_DepthOfFieldEnabled = true; PP.DepthOfFieldEnabled = false;
        PP.bOverride_DepthOfFieldScale = true; PP.DepthOfFieldScale = 0.f;
    }
}
