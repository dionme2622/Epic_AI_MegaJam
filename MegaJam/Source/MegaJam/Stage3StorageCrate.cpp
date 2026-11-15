#include "Stage3StorageCrate.h"

#include "Camera/PlayerCameraManager.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "DirectorCutGraphics.h"
#include "DirectorCutPlayHUD.h"
#include "DirectorCutPuzzleAudio.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "ResolutionCorridor.h"
#include "UObject/ConstructorHelpers.h"

#define LOCTEXT_NAMESPACE "Stage3StorageCrate"

namespace
{
    constexpr float LidRevealDelay = .75f;
    constexpr float FadeDuration = 1.5f;
    constexpr float BlackHoldDuration = .1f;
}

AStage3StorageCrate::AStage3StorageCrate()
{
    PrimaryActorTick.bCanEverTick = true;
    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(Root);
    LidPivot = CreateDefaultSubobject<USceneComponent>(TEXT("LidPivot"));
    LidPivot->SetupAttachment(Root);
    LidPivot->SetRelativeLocation(FVector(0.f, -40.f, 104.f));

    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> Wood(TEXT("/Game/Stage4Integrated/Theatre/M10_Plank.M10_Plank"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> Brass(TEXT("/Game/Stage4Integrated/Theatre/M06_Gold.M06_Gold"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> Packing(TEXT("/Game/Stage4Integrated/Theatre/M05_Capstone.M05_Capstone"));

    auto Board = [&](const TCHAR* Name, USceneComponent* Parent, FVector Location, FVector Scale, UMaterialInterface* Material)
    {
        UStaticMeshComponent* Component = CreateDefaultSubobject<UStaticMeshComponent>(FName(Name));
        Component->SetupAttachment(Parent);
        Component->SetStaticMesh(Cube.Object);
        Component->SetRelativeLocation(Location);
        Component->SetRelativeScale3D(Scale);
        Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        if (Material) Component->SetMaterial(0, Material);
    };

    Board(TEXT("Floor"), Root, FVector(0,0,28), FVector(1.4,.8,.12), Wood.Object);
    Board(TEXT("Front"), Root, FVector(0,38,62), FVector(1.4,.08,.76), Wood.Object);
    Board(TEXT("Back"), Root, FVector(0,-38,62), FVector(1.4,.08,.76), Wood.Object);
    Board(TEXT("Left"), Root, FVector(-66,0,62), FVector(.08,.7,.76), Wood.Object);
    Board(TEXT("Right"), Root, FVector(66,0,62), FVector(.08,.7,.76), Wood.Object);
    Board(TEXT("Packing"), Root, FVector(0,0,39), FVector(1.22,.64,.08), Packing.Object);
    Board(TEXT("PackingImpression"), Root, FVector(0,0,44), FVector(.66,.31,.012), Wood.Object);
    Board(TEXT("Lid"), LidPivot, FVector(0,40,0), FVector(1.45,.85,.11), Wood.Object);
    Board(TEXT("LidBandLeft"), LidPivot, FVector(-48,40,6), FVector(.1,.85,.018), Brass.Object);
    Board(TEXT("LidBandRight"), LidPivot, FVector(48,40,6), FVector(.1,.85,.018), Brass.Object);
    Board(TEXT("FrontBand"), Root, FVector(0,42,67), FVector(1.42,.018,.07), Brass.Object);

    Label = CreateDefaultSubobject<UTextRenderComponent>(TEXT("Label"));
    Label->SetupAttachment(Root);
    Label->SetRelativeLocation(FVector(0.f, 10.f, 175.f));
    Label->SetRelativeRotation(FRotator(0.f, 90.f, 0.f));
    Label->SetHorizontalAlignment(EHTA_Center);
    Label->SetTextRenderColor(FColor(255, 219, 153));
    Label->SetWorldSize(17.f);
    Label->SetVisibility(false);
}

void AStage3StorageCrate::BeginPlay()
{
    Super::BeginPlay();
    if (!IsValid(Corridor))
    {
        double ClosestDistance = TNumericLimits<double>::Max();
        for (TActorIterator<AResolutionCorridor> It(GetWorld()); It; ++It)
        {
            const double Distance = FVector::DistSquared(It->GetActorLocation(), GetActorLocation());
            if (Distance < ClosestDistance)
            {
                ClosestDistance = Distance;
                Corridor = *It;
            }
        }
    }
    Label->SetText(LOCTEXT("OpenPrompt", "E  OPEN CRATE"));
    Label->SetVisibility(false);
}

void AStage3StorageCrate::EndPlay(EEndPlayReason::Type Reason)
{
    GetWorldTimerManager().ClearTimer(TransitionTimer);
    if (APlayerController* Controller = TransitionController.Get())
    {
        Controller->SetIgnoreMoveInput(false);
    }
    Super::EndPlay(Reason);
}

void AStage3StorageCrate::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
    auto* Controller = Cast<ADirectorCutPlayerController>(UGameplayStatics::GetPlayerController(this, 0));
    const bool bNearby = IsValid(Player) && FVector::Dist2D(Player->GetActorLocation(), GetActorLocation()) <= InteractionDistance
        && FMath::Abs(Player->GetActorLocation().Z - GetActorLocation().Z) < 175.f;
    const bool bReady = !IsValid(Corridor) || Corridor->bCompleted;
    const bool bCanInteract = bNearby && bReady && (!Controller || !Controller->IsGraphicsMenuOpen());
    Label->SetVisibility(bCanInteract && (!bOpened || DestinationLevel.IsNull()));
    if (bCanInteract && Controller && Controller->WasInputKeyJustPressed(EKeys::E) && !bOpened)
    {
        bOpened = true;
        DirectorCutPuzzleAudio::Play(this, DirectorCutPuzzleAudio::ECue::ArchiveCrate, GetActorLocation());
        if (DestinationLevel.IsNull())
        {
            Label->SetText(LOCTEXT("EmptyCrate", "EMPTY - TRANSFERRED TO FINAL VAULT"));
        }
        else
        {
            Label->SetVisibility(false);
            BeginTransition(*Controller);
        }
    }
    OpenAmount = FMath::FInterpConstantTo(OpenAmount, bOpened ? 1.f : 0.f, DeltaSeconds, 1.3f);
    LidPivot->SetRelativeRotation(FRotator(0.f, 0.f, -105.f * OpenAmount));
}

void AStage3StorageCrate::BeginTransition(APlayerController& Controller)
{
    TransitionController = &Controller;
    Controller.SetIgnoreMoveInput(true);
    if (ACharacter* Character = Controller.GetCharacter())
    {
        Character->GetCharacterMovement()->StopMovementImmediately();
    }
    GetWorldTimerManager().SetTimer(TransitionTimer, this, &AStage3StorageCrate::ShowTransferNotice, LidRevealDelay);
}

void AStage3StorageCrate::ShowTransferNotice()
{
    if (auto* HUD = GetWorld()->GetSubsystem<UDirectorCutPlayHUD>(); HUD && HUD->ShowProductionNote(
        LOCTEXT("LegsTransferredNoteKo", "상자는 비어 있습니다. 드래곤의 원래 다리는 최종 보관소로 옮겼습니다."),
        LOCTEXT("LegsTransferredNoteEn", "The crate is empty. The dragon's original legs have been moved to the final vault."),
        FSimpleDelegate::CreateUObject(this, &AStage3StorageCrate::FadeOut)))
    {
        return;
    }
    FadeOut();
}

void AStage3StorageCrate::FadeOut()
{
    if (auto* HUD = GetWorld()->GetSubsystem<UDirectorCutPlayHUD>()) HUD->ClearSubtitle();
    if (APlayerController* Controller = TransitionController.Get(); Controller && Controller->PlayerCameraManager)
    {
        Controller->PlayerCameraManager->StartCameraFade(0.f, 1.f, FadeDuration, FLinearColor::Black, false, true);
    }
    GetWorldTimerManager().SetTimer(TransitionTimer, this, &AStage3StorageCrate::LoadDestination, FadeDuration + BlackHoldDuration);
}

void AStage3StorageCrate::LoadDestination()
{
    UGameplayStatics::OpenLevelBySoftObjectPtr(this, DestinationLevel);
}

#undef LOCTEXT_NAMESPACE
