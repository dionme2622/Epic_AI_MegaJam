#include "ColorSignalPuzzle.h"
#include "DirectorCutGraphics.h"
#include "DirectorCutPuzzleAudio.h"
#include "Stage4RgbPanel.h"
#include "Stage2ShadowPrototype.h"
#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
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
#include "Styling/CoreStyle.h"

namespace
{
    constexpr int32 RgbTargets[AColorSignalPuzzle::RgbChannelCount] = {2, 1, 3};
}

AColorSignalPuzzle::AColorSignalPuzzle()
{
    PrimaryActorTick.bCanEverTick=true;
    Root=CreateDefaultSubobject<USceneComponent>(TEXT("Root"));SetRootComponent(Root);
    Frame=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Frame"));Frame->SetupAttachment(Root);
    SignalPanel=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("SignalPanel"));SignalPanel->SetupAttachment(Root);
    RecordBackground=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RecordBackground"));RecordBackground->SetupAttachment(Root);
    Dial1=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Dial1"));Dial1->SetupAttachment(Root);
    Dial2=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Dial2"));Dial2->SetupAttachment(Root);
    Dial3=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Dial3"));Dial3->SetupAttachment(Root);
    Dial4=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Dial4"));Dial4->SetupAttachment(Root);
    for (UStaticMeshComponent* M : {Frame.Get(),SignalPanel.Get(),RecordBackground.Get(),Dial1.Get(),Dial2.Get(),Dial3.Get(),Dial4.Get()}) M->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Frame->SetRelativeLocation(FVector(500,-140,325)); SignalPanel->SetRelativeLocation(FVector(500,-125,430));
    RecordBackground->SetRelativeLocation(FVector(500,-125,325));RecordBackground->SetVisibility(false);
    Dial1->SetRelativeLocation(FVector(245,-95,250));Dial2->SetRelativeLocation(FVector(415,-95,250));Dial3->SetRelativeLocation(FVector(585,-95,250));Dial4->SetRelativeLocation(FVector(755,-95,250));
    RestoredRecord=CreateDefaultSubobject<UTextRenderComponent>(TEXT("RestoredRecord"));RestoredRecord->SetupAttachment(Root);
    RestoredRecord->SetRelativeLocation(FVector(500,-70,325));RestoredRecord->SetRelativeRotation(FRotator(0,90,0));
    RestoredRecord->SetHorizontalAlignment(EHTA_Center);RestoredRecord->SetVerticalAlignment(EVRTA_TextCenter);
    RestoredRecord->SetWorldSize(35.f);RestoredRecord->SetTextRenderColor(FColor::Black);
    RestoredRecord->SetText(FText::FromString(TEXT("MACHINE STORAGE")));RestoredRecord->SetVisibility(false);
    PuzzleCamera=CreateDefaultSubobject<UCameraComponent>(TEXT("PuzzleCamera"));PuzzleCamera->SetupAttachment(Root);
    PuzzleCamera->SetRelativeLocation(FVector(500,1400,325));PuzzleCamera->SetRelativeRotation(FRotator(0,-90,0));PuzzleCamera->SetFieldOfView(35.f);
    PuzzleCamera->PostProcessBlendWeight=1.f;
    auto& PP=PuzzleCamera->PostProcessSettings;PP.bOverride_ColorGain=true;PP.ColorGain=FVector4(1,1,1,1);
    PP.bOverride_BloomIntensity=true;PP.BloomIntensity=0.f;PP.bOverride_DepthOfFieldEnabled=true;PP.DepthOfFieldEnabled=false;
    PP.bOverride_AutoExposureMethod=true;PP.AutoExposureMethod=AEM_Manual;
    PP.bOverride_AutoExposureApplyPhysicalCameraExposure=true;PP.AutoExposureApplyPhysicalCameraExposure=false;
    PP.bOverride_AutoExposureBias=true;PP.AutoExposureBias=0.f;
}
void AColorSignalPuzzle::BeginPlay()
{
    Super::BeginPlay();
    ResetDials();
    SetFilter(0);
    if (bUseRgbCalibration)
    {
        SignalPanel->SetVisibility(false);
        RecordBackground->SetVisibility(true);
        RestoredRecord->SetText(FText::FromString(TEXT("RGB LIGHT PANEL")));
        RestoredRecord->SetVisibility(true);
        Dial4->SetVisibility(false);
    }
}
void AColorSignalPuzzle::EndPlay(const EEndPlayReason::Type Reason){LeavePuzzle();Super::EndPlay(Reason);}
FText AColorSignalPuzzle::GetHeaderText() const
{
    const TCHAR* Modes[]={TEXT("FULL"),TEXT("RED"),TEXT("GREEN"),TEXT("BLUE")};
    return FText::FromString(FString::Printf(TEXT("FILTER: %s  |  Q: CHANGE   1/2/3/4: ROTATE   R: RESET"),Modes[FMath::Clamp(FilterMode,0,3)]));
}
FText AColorSignalPuzzle::GetMessageText() const
{
    if (bCompleting) return FText::FromString(TEXT("SIGNAL RESTORED - EXIT OPENING"));
    if (bWrong && MessageTime>0) return FText::FromString(TEXT("NOT ALIGNED - CHECK EACH COLOR LAYER"));
    return FText::FromString(TEXT("MATCH EACH POINTER TO ITS LABEL COLOR  |  1/2/3/4: ROTATE  |  SPACE: CHECK   E: LEAVE"));
}
void AColorSignalPuzzle::EnterPuzzle()
{
    APlayerController* PC=UGameplayStatics::GetPlayerController(this,0);APawn* Pawn=PC?PC->GetPawn():nullptr;
    if (!PC || !Pawn || bActive || bSolved || FVector::Dist2D(Pawn->GetActorLocation(),GetActorLocation())>InteractDistance) return;
    PreviousView=PC->GetViewTarget();bActive=true;PC->SetIgnoreMoveInput(true);
    if (ACharacter* C=Cast<ACharacter>(Pawn)) C->GetCharacterMovement()->StopMovementImmediately();
    if (bUseRgbCalibration)
    {
        PC->SetViewTargetWithBlend(this, .22f);
        DirectorCutPuzzleAudio::Play(this, DirectorCutPuzzleAudio::ECue::ControlTick, GetActorLocation());
    }
    else PC->SetViewTarget(this);
    if (GEngine && GEngine->GameViewport)
    {
        if (bUseRgbCalibration)
        {
            Overlay = BuildStage4RgbPanel(*this);
            GEngine->GameViewport->AddViewportWidgetContent(Overlay.ToSharedRef(), 9);
            return;
        }
        Overlay=SNew(SOverlay)+SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Top).Padding(15)
        [ SNew(SBorder).Padding(12).BorderBackgroundColor(FLinearColor(.02f,.015f,.035f,.97f))
          [ SNew(SVerticalBox)
            +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0,0,0,5)
            [ SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Bold",18)).ColorAndOpacity(FLinearColor(1,.77f,.3f)).Text_Lambda([this](){return GetHeaderText();}) ]
            +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)
            [ SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",15)).ColorAndOpacity(FLinearColor::White).Text_Lambda([this](){return GetMessageText();}) ] ] ];
        GEngine->GameViewport->AddViewportWidgetContent(Overlay.ToSharedRef(),50);
    }
}
void AColorSignalPuzzle::LeavePuzzle()
{
    if (!bActive) return;
    if (APlayerController* PC=UGameplayStatics::GetPlayerController(this,0))
    {
        PC->SetIgnoreMoveInput(false);
        if (AActor* View = PreviousView.IsValid() ? PreviousView.Get() : PC->GetPawn())
        {
            if (bUseRgbCalibration && !IsActorBeingDestroyed()) PC->SetViewTargetWithBlend(View, .25f);
            else PC->SetViewTarget(View);
        }
    }
    if (Overlay.IsValid() && GEngine && GEngine->GameViewport) GEngine->GameViewport->RemoveViewportWidgetContent(Overlay.ToSharedRef());
    Overlay.Reset();bActive=false;
}
void AColorSignalPuzzle::SetFilter(int32 Mode)
{
    FilterMode=bUseRgbCalibration ? 0 : FMath::Clamp(Mode,0,3);
    const FVector4 Gain[]={FVector4(1,1,1,1),FVector4(1,0,0,1),FVector4(0,1,0,1),FVector4(0,0,1,1)};
    PuzzleCamera->PostProcessSettings.ColorGain=Gain[FilterMode];
}
void AColorSignalPuzzle::UpdateDialVisuals()
{
    UStaticMeshComponent* Dials[]={Dial1.Get(),Dial2.Get(),Dial3.Get(),Dial4.Get()};
    for (int32 Index = 0; Index < DialValues.Num() && Index < UE_ARRAY_COUNT(Dials); ++Index)
    {
        Dials[Index]->SetRelativeRotation(FRotator(90.f * DialValues[Index], 0, 0));
    }
}
void AColorSignalPuzzle::ResetDials()
{
    if (bSolved) return;
    if (bUseRgbCalibration)
    {
        const bool bWasAdjusted = DialValues.ContainsByPredicate([](int32 Value) { return Value != 0; });
        DialValues.Init(0, RgbChannelCount);
        if (bActive && bWasAdjusted)
        {
            DirectorCutPuzzleAudio::Play(this, DirectorCutPuzzleAudio::ECue::ControlTick, GetActorLocation());
        }
    }
    else DialValues = {0, 1, 0, 2};
    bWrong = false;
    MessageTime = 0.f;
    UpdateDialVisuals();
}

void AColorSignalPuzzle::RotateDial(int32 Index)
{
    if (bUseRgbCalibration)
    {
        if (!bActive || bSolved || !DialValues.IsValidIndex(Index)) return;
        DialValues[Index] = (DialValues[Index] + 1) % (RgbMaxLevel + 1);
        UpdateDialVisuals();
        if (AreDialsAligned())
        {
            Submit();
        }
        else
        {
            DirectorCutPuzzleAudio::Play(this, DirectorCutPuzzleAudio::ECue::RgbDial, GetActorLocation());
        }
        return;
    }
    if(!bActive||bSolved||Index<0||Index>=4||DialValues.Num()!=4)return;
    DialValues[Index]=(DialValues[Index]+1)%4;
    bWrong=false;UpdateDialVisuals();
}
bool AColorSignalPuzzle::AreDialsAligned() const
{
    if (bUseRgbCalibration)
    {
        return DialValues.Num() == RgbChannelCount &&
            DialValues[0] == RgbTargets[0] && DialValues[1] == RgbTargets[1] && DialValues[2] == RgbTargets[2];
    }
    return DialValues.Num()==4 && DialValues[0]==2 && DialValues[1]==3 && DialValues[2]==1 && DialValues[3]==2;
}
void AColorSignalPuzzle::Submit()
{
    if(!bActive||bSolved)return;
    if (bUseRgbCalibration)
    {
        if (!AreDialsAligned()) return;
        bSolved = true;
        bCompleting = true;
        FinishTime = 2.5f;
        DirectorCutPuzzleAudio::Play(this, DirectorCutPuzzleAudio::ECue::RgbLock, GetActorLocation());
        return;
    }
    if(AreDialsAligned())
    {
        bSolved=true;bCompleting=true;FinishTime=2.f;SetFilter(0);
        SignalPanel->SetVisibility(false);Dial1->SetVisibility(false);Dial2->SetVisibility(false);Dial3->SetVisibility(false);Dial4->SetVisibility(false);
        RecordBackground->SetVisibility(true);RestoredRecord->SetVisibility(true);
    }
    else {bWrong=true;MessageTime=2.f;}
}
void AColorSignalPuzzle::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);if(MessageTime>0)MessageTime=FMath::Max(0.f,MessageTime-DeltaSeconds);
    if (bCompleting)
    {
        FinishTime -= DeltaSeconds;
        if (FinishTime <= 0.f)
        {
            bCompleting = false;
            if (bUseRgbCalibration)
            {
                RestoredRecord->SetText(FText::FromString(TEXT("RGB SIGNAL RESTORED")));
            }
            if (IsValid(ExitDoor)) ExitDoor->OpenDoor();
            OnSolved();
            LeavePuzzle();
        }
        return;
    }
    APlayerController* PC=UGameplayStatics::GetPlayerController(this,0);if(!PC)return;
    if (bUseRgbCalibration)
    {
        const ADirectorCutPlayerController* Director = Cast<ADirectorCutPlayerController>(PC);
        if (Director && Director->IsGraphicsMenuOpen()) return;
    }
    if(PC->WasInputKeyJustPressed(EKeys::E)){if(bActive)LeavePuzzle();else EnterPuzzle();return;}if(!bActive)return;
    if (PC->WasInputKeyJustPressed(EKeys::One)) RotateDial(0);
    if (PC->WasInputKeyJustPressed(EKeys::Two)) RotateDial(1);
    if (PC->WasInputKeyJustPressed(EKeys::Three)) RotateDial(2);
    if (PC->WasInputKeyJustPressed(EKeys::R)) ResetDials();
    if (!bUseRgbCalibration)
    {
        if (PC->WasInputKeyJustPressed(EKeys::Q)) SetFilter((FilterMode + 1) % 4);
        if (PC->WasInputKeyJustPressed(EKeys::Four)) RotateDial(3);
        if (PC->WasInputKeyJustPressed(EKeys::SpaceBar) || PC->WasInputKeyJustPressed(EKeys::Enter)) Submit();
    }
}
