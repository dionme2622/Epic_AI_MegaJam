#include "ResolutionCorridor.h"
#include "DirectorCutTest.h"
#include "Stage2ShadowPrototype.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/GameViewportClient.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "HAL/IConsoleManager.h"
#include "Widgets/SOverlay.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Text/STextBlock.h"
#include "Styling/CoreStyle.h"

namespace { const FName PixelTag(TEXT("ResolutionCorridorPixelation")); }

AResolutionCorridorTile::AResolutionCorridorTile()
{
    Mesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));SetRootComponent(Mesh);
    Mesh->SetMobility(EComponentMobility::Movable);
    Mesh->SetCollisionProfileName(TEXT("BlockAll"));
}
AResolutionCorridor::AResolutionCorridor(){PrimaryActorTick.bCanEverTick=true;}
void AResolutionCorridor::BeginPlay()
{
    Super::BeginPlay();
    Player=UGameplayStatics::GetPlayerPawn(this,0);
    if(Player.IsValid()) SpawnLocation=Player->GetActorLocation();
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
        Overlay=SNew(SOverlay).Visibility_Lambda([this]()
          {
              if (!Player.IsValid()) return EVisibility::Collapsed;
              const float X = Player->GetActorLocation().X - GetActorLocation().X;
              if ((bRestrictOverlayStart && X < ShowOverlayFromOffsetX) || (HideOverlayBeyondX > 0.f && X > HideOverlayBeyondX)) return EVisibility::Collapsed;
              return EVisibility::SelfHitTestInvisible;
          })
        +SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Top).Padding(14)
        [SNew(SBorder).Padding(11).BorderBackgroundColor(FLinearColor(.02f,.025f,.04f,.88f))
         [SNew(SVerticalBox)
          +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)
          [SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Bold",16)).ColorAndOpacity(FLinearColor(1,.8f,.35f)).Text_Lambda([this](){return StatusText();})]
          +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0,4,0,0)
          [SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",13)).ColorAndOpacity(FLinearColor::White)
           .Visibility_Lambda([this]() { return bUseStationChoices ? EVisibility::Collapsed : EVisibility::Visible; })
           .Text(FText::FromString(TEXT("개발 메모: 저해상도 테스트용 안내 이미지를 배경에 남겨둠. 출시 전 삭제 필요.")))] ] ];
        GEngine->GameViewport->AddViewportWidgetContent(Overlay.ToSharedRef(),40);
    }
}
FText AResolutionCorridor::StatusText() const
{
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
