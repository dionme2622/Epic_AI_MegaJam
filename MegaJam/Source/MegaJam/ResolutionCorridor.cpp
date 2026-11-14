#include "ResolutionCorridor.h"
#include "DirectorCutTest.h"
#include "Stage2ShadowPrototype.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/GameViewportClient.h"
#include "Engine/Engine.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "HAL/IConsoleManager.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"
#include "Widgets/SOverlay.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Text/STextBlock.h"
#include "Styling/CoreStyle.h"

namespace
{
    const FName PixelTag(TEXT("ResolutionCorridorPixelation"));
    constexpr int32 BridgeClipCount = 2;
    constexpr int32 MaxBridgeNotch = 2;
    constexpr float ClipTravelPerNotch = 21.f;
    constexpr float SlideSpeed = 225.f;
    constexpr float ProjectionDepth = 14.f;
    constexpr float ProjectedRisePerNotch = 34.f;
}

AResolutionCorridorTile::AResolutionCorridorTile()
{
    Mesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));SetRootComponent(Mesh);
    Mesh->SetMobility(EComponentMobility::Movable);
    Mesh->SetCollisionProfileName(TEXT("BlockAll"));
}
AResolutionCorridor::AResolutionCorridor()
{
    PrimaryActorTick.bCanEverTick = true;
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> Line(TEXT("/Game/Stage4Integrated/Theatre/M14_Lamp.M14_Lamp"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> Selected(TEXT("/Game/Stage4Integrated/Theatre/M21_RetakeCue.M21_RetakeCue"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> Scratch(TEXT("/Game/Stage4Integrated/Theatre/M18_Steel.M18_Steel"));
    ProjectionCube = Cube.Object;
    ProjectionLineMaterial = Line.Object;
    ProjectionSelectedMaterial = Selected.Object;
    ProjectionScratchMaterial = Scratch.Object;
}
void AResolutionCorridor::BeginPlay()
{
    Super::BeginPlay();
    Player=UGameplayStatics::GetPlayerPawn(this,0);
    if(Player.IsValid()) SpawnLocation=Player->GetActorLocation();
    if (bUseProjectedBridge)
    {
        InitializeProjectedBridge();
    }
    if (bUseStationChoices && StationCheckpointOffsets.IsValidIndex(0))
    {
        SpawnLocation = GetActorTransform().TransformPosition(StationCheckpointOffsets[0]);
    }
    for(TActorIterator<AResolutionCorridorTile> It(GetWorld());It;++It) It->InitialLocation=It->GetActorLocation();
    if(auto* Settings=GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>())
    {
        Settings->OnGraphicsChanged.AddDynamic(this,&AResolutionCorridor::GraphicsChanged);
        UpdateGuidance(Settings->IsHigh(EDirectorCutGraphicsOption::Resolution));
    }
    if(GEngine && GEngine->GameViewport)
    {
        const bool bCampaignBridge = bUseProjectedBridge && UGameplayStatics::GetCurrentLevelName(this, true) == TEXT("Stage3_");
        Overlay=SNew(SOverlay).Visibility_Lambda([this]()
          {
              if (!Player.IsValid()) return EVisibility::Collapsed;
              const float X = Player->GetActorLocation().X - GetActorLocation().X;
              if ((bRestrictOverlayStart && X < ShowOverlayFromOffsetX) || (HideOverlayBeyondX > 0.f && X > HideOverlayBeyondX)) return EVisibility::Collapsed;
              const auto* Controller = Cast<ADirectorCutPlayerController>(UGameplayStatics::GetPlayerController(this, 0));
              if (bUseProjectedBridge && Controller && Controller->IsGraphicsMenuOpen()) return EVisibility::Collapsed;
              return EVisibility::SelfHitTestInvisible;
          })
        +SOverlay::Slot().HAlign(HAlign_Center).VAlign(bCampaignBridge ? VAlign_Bottom : VAlign_Top).Padding(14)
        [SNew(SBorder).Padding(11).BorderBackgroundColor(FLinearColor(.02f,.025f,.04f,.88f))
         [SNew(SVerticalBox)
          +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)
          [SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Bold",16)).ColorAndOpacity(FLinearColor(1,.8f,.35f)).Text_Lambda([this](){return StatusText();})]
          +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0,4,0,0)
          [SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",13)).ColorAndOpacity(FLinearColor::White)
           .Visibility_Lambda([this]() { return (bUseStationChoices || bUseReelHunt || bUseProjectedBridge) ? EVisibility::Collapsed : EVisibility::Visible; })
           .Text(FText::FromString(TEXT("개발 메모: 저해상도 테스트용 안내 이미지를 배경에 남겨둠. 출시 전 삭제 필요.")))] ] ];
        GEngine->GameViewport->AddViewportWidgetContent(Overlay.ToSharedRef(),40);
    }
}
FText AResolutionCorridor::StatusText() const
{
    if (bUseProjectedBridge)
    {
        if (bCompleted) return FText::FromString(TEXT("BRIDGE LOCKED  |  CROSS TO PROP STORAGE"));
        if (!bBridgeConfigured) return FText::FromString(TEXT("PROJECTOR UNAVAILABLE"));
        if (UGameplayStatics::GetCurrentLevelName(this, true) != TEXT("Stage3_"))
        {
            if (!bBridgeConsoleOpen)
            {
                return FText::FromString(IsAtBridgeConsole()
                    ? TEXT("E: OPERATE FILM DESK  |  GRAPHICS: LOW RESOLUTION TO READ THE SCREEN")
                    : TEXT("FIND THE FILM DESK AT THE EDGE OF THE BRIDGE"));
            }
            const TCHAR* Hint = bProjectionReadable ? TEXT("JOIN THE THREE FIXED LINES") : TEXT("LOWER RESOLUTION IN GRAPHICS TO READ THE SCREEN");
            return FText::FromString(FString::Printf(TEXT("%s  |  1 / 2: SELECT CLIP  |  UP / DOWN: SLIDE  |  E: LEAVE"), Hint));
        }
        if (!bBridgeConsoleOpen)
        {
            return FText::FromString(bProjectionReadable ? TEXT("PROJECTION READY") : TEXT("PROJECTION OBSCURED"));
        }
        return FText::FromString(FString::Printf(TEXT("%s  |  CLIP %d"),
            bProjectionReadable ? TEXT("PROJECTION READY") : TEXT("PROJECTION OBSCURED"), ActiveBridgeClip + 1));
    }
    if (bUseReelHunt)
    {
        if (bCompleted) return FText::FromString(TEXT("FILM SIGNAL RESTORED - EXIT OPEN"));
        if (ReelMistakeTime > 0.f) return FText::FromString(TEXT("WRONG REEL - THE FILM REWINDS TO THE START"));
        return FText::FromString(FString::Printf(TEXT("REBUILD THE FILM  %d / 3   |   LOW RESOLUTION: DECODE ORDER   |   E: ACTIVATE NEARBY REEL"), Progress));
    }
    if(bCompleted)return FText::FromString(TEXT("경로 확인 완료 — 출구가 열렸습니다"));
    if(bFailing)return FText::FromString(TEXT("불안정한 발판! 시작점으로 돌아갑니다"));
    if (bUseStationChoices)
    {
        if (bChoiceConfirmed)
            return FText::FromString(FString::Printf(TEXT("구간 %d / 3 — 발판으로 이동하세요"), Progress + 1));
        return FText::FromString(FString::Printf(TEXT("구간 %d / 3  |  1 / 2 / 3 선택: %d  |  E 확인  |  설정 → 해상도 낮음"), Progress + 1, SelectedChoice));
    }
    return FText::FromString(FString::Printf(TEXT("안전 발판 %d / 3  |  ⚙ 그래픽 설정 → 해상도 낮음  |  A/D 이동 · Space 점프"),Progress));
}
void AResolutionCorridor::GraphicsChanged(EDirectorCutGraphicsOption Option,bool bHigh)
{
    if(Option==EDirectorCutGraphicsOption::Resolution)UpdateGuidance(bHigh);
}
void AResolutionCorridor::UpdateGuidance(bool bHigh)
{
    if (bUseProjectedBridge)
    {
        bProjectionReadable = !bHigh;
        UpdateProjection();
    }
    for(AActor* Arrow:GuidanceArrows)if(IsValid(Arrow))Arrow->SetActorHiddenInGame(bHigh);
    auto& C=IConsoleManager::Get();
    if(bHigh) C.UnsetAllConsoleVariablesWithTag(PixelTag,ECVF_SetByGameOverride);
    else
    {
        if(auto* V=C.FindConsoleVariable(TEXT("r.TemporalAA.Upsampling"))) V->Set(0,ECVF_SetByGameOverride,PixelTag);
        if(auto* V=C.FindConsoleVariable(TEXT("r.Upscale.Quality"))) V->Set(0,ECVF_SetByGameOverride,PixelTag);
        if(auto* V=C.FindConsoleVariable(TEXT("r.AntiAliasingMethod"))) V->Set(0,ECVF_SetByGameOverride,PixelTag);
    }
}
void AResolutionCorridor::EndPlay(const EEndPlayReason::Type Reason)
{
    if (bUseProjectedBridge) SetBridgeConsoleOpen(false);
    if(auto* Settings=GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>())Settings->OnGraphicsChanged.RemoveDynamic(this,&AResolutionCorridor::GraphicsChanged);
    IConsoleManager::Get().UnsetAllConsoleVariablesWithTag(PixelTag,ECVF_SetByGameOverride);
    if(bMovementLocked)if(auto* PC=UGameplayStatics::GetPlayerController(this,0))PC->SetIgnoreMoveInput(false);
    if(Overlay.IsValid() && GEngine && GEngine->GameViewport)GEngine->GameViewport->RemoveViewportWidgetContent(Overlay.ToSharedRef());
    Overlay.Reset();Super::EndPlay(Reason);
}
void AResolutionCorridor::BeginFailure(AResolutionCorridorTile* Tile)
{
    if(bFailing||bCompleted)return;
    bFailing=true;FailureElapsed=0.f;FailingTile=Tile;
    if(auto* PC=UGameplayStatics::GetPlayerController(this,0)){PC->SetIgnoreMoveInput(true);bMovementLocked=true;}
    if(ACharacter* C=Cast<ACharacter>(Player.Get()))C->GetCharacterMovement()->StopMovementImmediately();
    OnWrongTile();
}
void AResolutionCorridor::ResetPlayer()
{
    if(ACharacter* C=Cast<ACharacter>(Player.Get()))
    {
        C->GetCharacterMovement()->StopMovementImmediately();
        C->SetActorLocation(SpawnLocation,false,nullptr,ETeleportType::TeleportPhysics);
    }
    for(TActorIterator<AResolutionCorridorTile> It(GetWorld());It;++It) It->SetActorLocation(It->InitialLocation,false,nullptr,ETeleportType::TeleportPhysics);
    if (!bUseStationChoices) Progress=0;
    SelectedChoice=0;bChoiceConfirmed=false;FailingTile.Reset();bFailing=false;FailureElapsed=0.f;
    if(bMovementLocked){if(auto* PC=UGameplayStatics::GetPlayerController(this,0))PC->SetIgnoreMoveInput(false);bMovementLocked=false;}
}
void AResolutionCorridor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (bUseProjectedBridge)
    {
        TickProjectedBridge(DeltaSeconds);
        return;
    }
    if(!Player.IsValid())return;
    if (bUseLocalCheckpoint && !bCheckpointActivated && Player->GetActorLocation().X >= GetActorLocation().X + ShowOverlayFromOffsetX)
    {
        const FVector Checkpoint = bUseStationChoices && StationCheckpointOffsets.IsValidIndex(0)
            ? StationCheckpointOffsets[0] : LocalCheckpointOffset;
        SpawnLocation = GetActorTransform().TransformPosition(Checkpoint);
        if (ADirectorCutDragon* Dragon = Cast<ADirectorCutDragon>(Player.Get())) Dragon->SetPuzzleRespawnPoint(SpawnLocation);
        bCheckpointActivated = true;
    }
    if(bFailing)
    {
        FailureElapsed+=DeltaSeconds;
        if(FailingTile.IsValid())
        {
            auto* T=FailingTile.Get();
            T->SetActorLocation(T->InitialLocation-FVector(0,0,SinkDistance*FMath::Clamp(FailureElapsed/FMath::Max(SinkDuration,.1f),0.f,1.f)),false,nullptr,ETeleportType::None);
        }
        if(FailureElapsed>=FMath::Max(SinkDuration,.1f))ResetPlayer();
        return;
    }
    if(bCompleted)return;
    if(Player->GetActorLocation().Z<FallResetZ){BeginFailure(nullptr);return;}
    ACharacter* C=Cast<ACharacter>(Player.Get());
    if(!C || !C->GetCharacterMovement()->IsMovingOnGround())return;
    if (bUseReelHunt)
    {
        ReelMistakeTime = FMath::Max(0.f, ReelMistakeTime - DeltaSeconds);
        APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
        const auto* Director = Cast<ADirectorCutPlayerController>(PC);
        if (PC && (!Director || !Director->IsGraphicsMenuOpen()) && PC->WasInputKeyJustPressed(EKeys::E))
        {
            int32 Nearest = INDEX_NONE;
            double Distance = ReelInteractionDistance;
            for (int32 Index = 0; Index < ReelStations.Num(); ++Index)
            {
                if (!IsValid(ReelStations[Index])) continue;
                const double D = FVector::Dist2D(C->GetActorLocation(), ReelStations[Index]->GetActorLocation());
                if (D <= Distance) { Distance = D; Nearest = Index; }
            }
            if (Nearest != INDEX_NONE && ReelSequence.IsValidIndex(Progress))
            {
                if (Nearest + 1 == ReelSequence[Progress])
                {
                    ++Progress;
                    ReelMistakeTime = 0.f;
                    if (Progress >= ReelSequence.Num())
                    {
                        bCompleted = true;
                        if (IsValid(ExitDoor)) ExitDoor->OpenDoor();
                        OnCorridorCompleted();
                    }
                }
                else { Progress = 0; ReelMistakeTime = 2.f; OnWrongTile(); }
            }
        }
        return;
    }
    if (bUseStationChoices && StationCheckpointOffsets.IsValidIndex(Progress))
    {
        const FVector Station = GetActorTransform().TransformPosition(StationCheckpointOffsets[Progress]);
        APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
        const auto* Director = Cast<ADirectorCutPlayerController>(PC);
        if (PC && (!Director || !Director->IsGraphicsMenuOpen()) && !bChoiceConfirmed &&
            FVector::Dist2D(C->GetActorLocation(), Station) <= StationInteractionDistance)
        {
            if (PC->WasInputKeyJustPressed(EKeys::One)) SelectedChoice = 1;
            if (PC->WasInputKeyJustPressed(EKeys::Two)) SelectedChoice = 2;
            if (PC->WasInputKeyJustPressed(EKeys::Three)) SelectedChoice = 3;
            if (PC->WasInputKeyJustPressed(EKeys::E) && SelectedChoice != 0 &&
                StationAnswers.IsValidIndex(Progress))
            {
                if (SelectedChoice == StationAnswers[Progress]) bChoiceConfirmed = true;
                else { BeginFailure(nullptr); return; }
            }
        }
    }
    AResolutionCorridorTile* Tile=Cast<AResolutionCorridorTile>(C->GetCharacterMovement()->CurrentFloor.HitResult.GetActor());
    if(!Tile)return;
    if (bUseStationChoices && Tile->SafeOrder == Progress && !bChoiceConfirmed)
    {
        BeginFailure(nullptr);
        return;
    }
    if(!Tile->bSafe || Tile->SafeOrder>Progress){BeginFailure(Tile);return;}
    if(Tile->SafeOrder==Progress)
    {
        ++Progress;
        if (bUseStationChoices)
        {
            SelectedChoice = 0;
            bChoiceConfirmed = false;
            if (StationCheckpointOffsets.IsValidIndex(Progress))
            {
                SpawnLocation = GetActorTransform().TransformPosition(StationCheckpointOffsets[Progress]);
                if (ADirectorCutDragon* Dragon = Cast<ADirectorCutDragon>(Player.Get()))
                    Dragon->SetPuzzleRespawnPoint(SpawnLocation);
            }
        }
        if(Progress>=3){bCompleted=true;if(IsValid(ExitDoor))ExitDoor->OpenDoor();OnCorridorCompleted();}
    }
}

void AResolutionCorridor::InitializeProjectedBridge()
{
    if (BridgePlatforms.Num() != BridgeClipCount || BridgePlatforms[0] == BridgePlatforms[1]
        || !IsValid(ProjectionScreen) || !ProjectionScreen->GetRootComponent() || !IsValid(ProjectionCube))
    {
        UE_LOG(LogTemp, Error, TEXT("%s requires a projection screen and two different bridge platforms."), *GetPathName());
        return;
    }
    for (const AActor* Platform : BridgePlatforms)
    {
        if (!IsValid(Platform) || !Platform->GetRootComponent() || Platform->GetRootComponent()->Mobility != EComponentMobility::Movable)
        {
            UE_LOG(LogTemp, Error, TEXT("%s requires two movable bridge platform actors."), *GetPathName());
            return;
        }
    }

    bBridgeConfigured = true;
    BridgeNotches.SetNum(BridgeClipCount);
    for (int32 Index = 0; Index < BridgeClipCount; ++Index)
    {
        AActor* Platform = BridgePlatforms[Index];
        const int32 DefaultNotch = Index == 0 ? 1 : -2;
        const int32 InitialNotch = InitialBridgeNotches.IsValidIndex(Index) ? InitialBridgeNotches[Index] : DefaultNotch;
        BridgeNotches[Index] = FMath::Clamp(InitialNotch, -MaxBridgeNotch, MaxBridgeNotch);
        BridgePlatformOrigins[Index] = Platform->GetActorLocation();
        BridgeCurrentOffsets[Index] = BridgeNotches[Index] * BridgeNotchHeight;
        Platform->SetActorEnableCollision(false);
        Platform->SetActorLocation(BridgePlatformOrigins[Index] + FVector(0.f, 0.f, BridgeCurrentOffsets[Index]));

        if (BridgeClipActors.IsValidIndex(Index) && IsValid(BridgeClipActors[Index]))
        {
            AActor* Clip = BridgeClipActors[Index];
            BridgeClipOrigins[Index] = Clip->GetActorLocation();
            Clip->SetActorEnableCollision(false);
            Clip->SetActorLocation(BridgeClipOrigins[Index] + FVector(0.f, 0.f, BridgeNotches[Index] * ClipTravelPerNotch));
        }
    }
    BuildProjection();
}

void AResolutionCorridor::BuildProjection()
{
    USceneComponent* ScreenRoot = ProjectionScreen->GetRootComponent();
    const FTransform ScreenTransform = ProjectionScreen->GetActorTransform();
    const FVector Center = ScreenTransform.GetLocation();
    const FQuat ScreenRotation = ScreenTransform.GetRotation();
    const auto MakeBar = [this, ScreenRoot, Center, ScreenRotation](FVector Position, FVector Size, float Lean, UMaterialInterface* Material)
    {
        auto* Bar = NewObject<UStaticMeshComponent>(this);
        Bar->SetMobility(EComponentMobility::Movable);
        Bar->SetStaticMesh(ProjectionCube);
        Bar->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Bar->SetGenerateOverlapEvents(false);
        Bar->SetCastShadow(false);
        Bar->SetMaterial(0, Material);
        Bar->RegisterComponent();
        Bar->AttachToComponent(ScreenRoot, FAttachmentTransformRules::KeepWorldTransform);
        Bar->SetWorldTransform(FTransform(ScreenRotation * FRotator(Lean, 0.f, 0.f).Quaternion(),
            Center + ScreenRotation.RotateVector(Position), Size / 100.f));
        return Bar;
    };

    // Left bank, first span, centre support, second span, right bank.
    const float Centers[] = {-268.f, -146.f, 0.f, 146.f, 268.f};
    const float Widths[] = {92.f, 156.f, 140.f, 156.f, 92.f};
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Centers); ++Index)
    {
        UStaticMeshComponent* Bar = MakeBar({Centers[Index], ProjectionDepth, 0.f},
            {Widths[Index], 2.f, 16.f}, 0.f, ProjectionLineMaterial);
        ProjectionRoute.Add(Bar);
    }

    FRandomStream Scratches(31003);
    for (int32 Index = 0; Index < 72; ++Index)
    {
        const float X = Scratches.FRandRange(-310.f, 310.f);
        const float Z = Scratches.FRandRange(-85.f, 85.f);
        ProjectionScratches.Add(MakeBar({X, ProjectionDepth - 4.f, Z},
            {Scratches.FRandRange(8.f, 65.f), 1.f, Scratches.FRandRange(1.6f, 4.f)},
            Scratches.FRandRange(-13.f, 13.f), ProjectionScratchMaterial));
    }
    UpdateProjection();
}

void AResolutionCorridor::UpdateProjection()
{
    if (ProjectionRoute.Num() != 5 || !IsValid(ProjectionScreen)) return;
    const FVector Center = ProjectionScreen->GetActorLocation();
    const FQuat Rotation = ProjectionScreen->GetActorQuat();
    for (int32 Index = 0; Index < BridgeClipCount; ++Index)
    {
        UStaticMeshComponent* Span = ProjectionRoute[Index * 2 + 1];
        const float X = Index == 0 ? -146.f : 146.f;
        const float Z = (BridgeCurrentOffsets[Index] / BridgeNotchHeight) * ProjectedRisePerNotch;
        Span->SetWorldLocation(Center + Rotation.RotateVector({X, ProjectionDepth, Z}));
        const bool bSelected = bBridgeConsoleOpen && ActiveBridgeClip == Index;
        Span->SetMaterial(0, bSelected ? ProjectionSelectedMaterial : ProjectionLineMaterial);
    }
    for (UStaticMeshComponent* Line : ProjectionRoute) Line->SetVisibility(bProjectionReadable);
    for (UStaticMeshComponent* Scratch : ProjectionScratches) Scratch->SetVisibility(!bProjectionReadable);
}

bool AResolutionCorridor::IsAtBridgeConsole() const
{
    if (!Player.IsValid()) return false;
    const FVector Desk = IsValid(BridgeConsole) ? BridgeConsole->GetActorLocation() : GetActorLocation() + FVector(210.f, 0.f, 0.f);
    const FVector Delta = Player->GetActorLocation() - Desk;
    return FMath::Abs(Delta.X) <= BridgeInteractionDistance && FMath::Abs(Delta.Y) <= 260.f && FMath::Abs(Delta.Z) <= 180.f;
}

bool AResolutionCorridor::CanOpenBridgeConsole() const
{
    return bUseProjectedBridge && bBridgeConfigured && !bCompleted && !bBridgeConsoleOpen && IsAtBridgeConsole();
}

void AResolutionCorridor::SetBridgeConsoleOpen(bool bOpen)
{
    if (bBridgeConsoleOpen == bOpen) return;
    if (bOpen)
    {
        APlayerController* Controller = UGameplayStatics::GetPlayerController(this, 0);
        if (!Controller) return;
        BridgeInputController = Controller;
        Controller->SetIgnoreMoveInput(true);
        if (ACharacter* Character = Cast<ACharacter>(Player.Get())) Character->GetCharacterMovement()->StopMovementImmediately();
    }
    else
    {
        if (BridgeInputController.IsValid()) BridgeInputController->SetIgnoreMoveInput(false);
        BridgeInputController.Reset();
    }
    bBridgeConsoleOpen = bOpen;
    if (auto* Dragon = Cast<ADirectorCutDragon>(Player.Get()))
    {
        const float FocusX = IsValid(ProjectionScreen) ? ProjectionScreen->GetActorLocation().X : Player->GetActorLocation().X;
        Dragon->SetTheatreCameraFraming(bOpen ? 1.f : 0.f, FocusX);
    }
    UpdateProjection();
}

void AResolutionCorridor::TickProjectedBridge(float DeltaSeconds)
{
    if (!bBridgeConfigured) return;
    APawn* CurrentPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (Player.Get() != CurrentPawn)
    {
        SetBridgeConsoleOpen(false);
        Player = CurrentPawn;
        bCheckpointActivated = false;
    }
    if (!Player.IsValid()) return;

    const FVector Position = Player->GetActorLocation();
    const float LocalX = Position.X - GetActorLocation().X;
    if (!bCheckpointActivated && bUseLocalCheckpoint && LocalX >= ShowOverlayFromOffsetX
        && (HideOverlayBeyondX <= 0.f || LocalX <= HideOverlayBeyondX))
    {
        SpawnLocation = GetActorTransform().TransformPosition(LocalCheckpointOffset);
        if (auto* Dragon = Cast<ADirectorCutDragon>(Player.Get())) Dragon->SetPuzzleRespawnPoint(SpawnLocation);
        bCheckpointActivated = true;
    }
    // Once the bridge is locked, a fall still returns the player to the desk.
    if (bCheckpointActivated && LocalX >= ShowOverlayFromOffsetX
        && (HideOverlayBeyondX <= 0.f || LocalX <= HideOverlayBeyondX) && Position.Z < FallResetZ)
    {
        SetBridgeConsoleOpen(false);
        if (auto* Character = Cast<ACharacter>(Player.Get())) Character->GetCharacterMovement()->StopMovementImmediately();
        Player->SetActorLocation(SpawnLocation, false, nullptr, ETeleportType::TeleportPhysics);
        return;
    }
    if (bCompleted) return;

    if (bBridgeConsoleOpen && !IsAtBridgeConsole()) SetBridgeConsoleOpen(false);
    APlayerController* Controller = UGameplayStatics::GetPlayerController(this, 0);
    const auto* GraphicsController = Cast<ADirectorCutPlayerController>(Controller);
    const bool bCanReadInput = Controller && (!GraphicsController || !GraphicsController->IsGraphicsMenuOpen());
    if (bCanReadInput && Controller->WasInputKeyJustPressed(EKeys::E))
    {
        if (bBridgeConsoleOpen) SetBridgeConsoleOpen(false);
        else if (IsAtBridgeConsole()) SetBridgeConsoleOpen(true);
    }
    if (bCanReadInput && bBridgeConsoleOpen)
    {
        if (Controller->WasInputKeyJustPressed(EKeys::One)) ActiveBridgeClip = 0;
        if (Controller->WasInputKeyJustPressed(EKeys::Two)) ActiveBridgeClip = 1;
        const int32 Direction = static_cast<int32>(Controller->WasInputKeyJustPressed(EKeys::Up))
            - static_cast<int32>(Controller->WasInputKeyJustPressed(EKeys::Down));
        if (Direction != 0)
        {
            int32& Notch = BridgeNotches[ActiveBridgeClip];
            const int32 Previous = Notch;
            Notch = FMath::Clamp(Notch + Direction, -MaxBridgeNotch, MaxBridgeNotch);
            bBridgeAdjusted |= Notch != Previous;
        }
    }

    bool bBothAligned = true;
    Progress = 0;
    for (int32 Index = 0; Index < BridgeClipCount; ++Index)
    {
        const float Target = BridgeNotches[Index] * BridgeNotchHeight;
        float& Offset = BridgeCurrentOffsets[Index];
        if (!FMath::IsNearlyEqual(Offset, Target))
        {
            Offset = FMath::FInterpConstantTo(Offset, Target, DeltaSeconds, SlideSpeed);
            if (IsValid(BridgePlatforms[Index]))
                BridgePlatforms[Index]->SetActorLocation(BridgePlatformOrigins[Index] + FVector(0.f, 0.f, Offset));
            if (BridgeClipActors.IsValidIndex(Index) && IsValid(BridgeClipActors[Index]))
                BridgeClipActors[Index]->SetActorLocation(BridgeClipOrigins[Index] + FVector(0.f, 0.f, Offset * ClipTravelPerNotch / BridgeNotchHeight));
        }
        const bool bAligned = BridgeNotches[Index] == 0 && FMath::IsNearlyZero(Offset);
        bBothAligned &= bAligned;
        if (bAligned) ++Progress;
    }
    UpdateProjection();
    if (bBridgeAdjusted && bBothAligned)
    {
        bCompleted = true;
        for (AActor* Platform : BridgePlatforms) if (IsValid(Platform)) Platform->SetActorEnableCollision(true);
        SetBridgeConsoleOpen(false);
        if (IsValid(ExitDoor)) ExitDoor->OpenDoor();
        OnCorridorCompleted();
    }
}
