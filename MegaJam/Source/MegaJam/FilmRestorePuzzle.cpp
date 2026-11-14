#include "FilmRestorePuzzle.h"
#include "DirectorCutGraphics.h"
#include "Stage2ShadowPrototype.h"
#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/PostProcessVolume.h"
#include "Engine/GameViewportClient.h"
#include "Engine/Engine.h"
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

AFilmRestorePuzzle::AFilmRestorePuzzle()
{
    PrimaryActorTick.bCanEverTick=true;
    Root=CreateDefaultSubobject<USceneComponent>(TEXT("Root")); SetRootComponent(Root);
    Frame=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Frame"));Frame->SetupAttachment(Root);
    Screen=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Screen"));Screen->SetupAttachment(Root);
    ClueA=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ClueA"));ClueA->SetupAttachment(Root);
    ClueB=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ClueB"));ClueB->SetupAttachment(Root);
    ClueC=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ClueC"));ClueC->SetupAttachment(Root);
    ShadowMask=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ShadowMask"));ShadowMask->SetupAttachment(Root);
    RestoredRecord=CreateDefaultSubobject<UTextRenderComponent>(TEXT("RestoredRecord"));RestoredRecord->SetupAttachment(Root);
    RestoredRecord->SetRelativeLocation(FVector(500,-70,300));RestoredRecord->SetRelativeRotation(FRotator(0,90,0));
    RestoredRecord->SetHorizontalAlignment(EHTA_Center);RestoredRecord->SetVerticalAlignment(EVRTA_TextCenter);
    RestoredRecord->SetWorldSize(35.f);RestoredRecord->SetTextRenderColor(FColor::Black);
    RestoredRecord->SetText(FText::FromString(TEXT("MACHINE STORAGE")));RestoredRecord->SetVisibility(false);
    for (UStaticMeshComponent* M : {Frame.Get(),Screen.Get(),ClueA.Get(),ClueB.Get(),ClueC.Get(),ShadowMask.Get()}) M->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Frame->SetRelativeLocation(FVector(500,-120,300)); Screen->SetRelativeLocation(FVector(500,-115,300));
    ClueA->SetRelativeLocation(FVector(500,-100,300));ClueB->SetRelativeLocation(FVector(500,-100,300));ClueC->SetRelativeLocation(FVector(500,-100,300));
    ShadowMask->SetRelativeLocation(FVector(500,-80,300));
    PuzzleCamera=CreateDefaultSubobject<UCameraComponent>(TEXT("PuzzleCamera"));PuzzleCamera->SetupAttachment(Root);
    PuzzleCamera->SetRelativeLocation(FVector(500,1400,300));PuzzleCamera->SetRelativeRotation(FRotator(0,-90,0));PuzzleCamera->SetFieldOfView(35.f);
}
void AFilmRestorePuzzle::BeginPlay() { Super::BeginPlay(); SelectFilm(1); ApplySettings(); }
void AFilmRestorePuzzle::EndPlay(const EEndPlayReason::Type Reason) { LeavePuzzle(); Super::EndPlay(Reason); }
FText AFilmRestorePuzzle::GetSettingsText() const
{
    return FText::FromString(FString::Printf(TEXT("FILM %c  |  1 / 2 / 3: FILM    B: BLOOM %s    Q: SHADOW %s    N: EXPOSURE %s"),TEXT('A')+CurrentFilm-1,bBloomOn?TEXT("ON"):TEXT("OFF"),bShadowOn?TEXT("ON"):TEXT("OFF"),bDarkExposure?TEXT("DARK"):TEXT("BRIGHT")));
}
FText AFilmRestorePuzzle::GetChoicesText() const
{
    const TCHAR* Marks[]={TEXT("STAR"),TEXT("MOON"),TEXT("GEAR")};
    return FText::FromString(FString::Printf(TEXT("4: SCENE %d     5: %s     6: %s     |     ENTER: RESTORE     E: LEAVE"),SceneChoice,DirectionChoice?TEXT("RIGHT"):TEXT("LEFT"),Marks[FMath::Clamp(MarkChoice,0,2)]));
}
FText AFilmRestorePuzzle::GetMessageText() const
{
    if (bCompleting) return FText::FromString(TEXT("RECORD RESTORED - EXIT OPENING"));
    if (bWrong && MessageTime>0) return FText::FromString(TEXT("INCORRECT - RECHECK THE FILMS"));
    return FText::FromString(TEXT("FIND THE SCENE NUMBER, DIRECTION AND STORAGE MARK"));
}
void AFilmRestorePuzzle::EnterPuzzle()
{
    APlayerController* PC=UGameplayStatics::GetPlayerController(this,0);APawn* Pawn=PC?PC->GetPawn():nullptr;
    if (!PC || !Pawn || bActive || bSolved || FVector::Dist2D(Pawn->GetActorLocation(),GetActorLocation())>InteractDistance) return;
    PreviousView=PC->GetViewTarget();bActive=true;PC->SetIgnoreMoveInput(true);
    if (ACharacter* C=Cast<ACharacter>(Pawn)) C->GetCharacterMovement()->StopMovementImmediately();
    PC->SetViewTarget(this);
    if (GEngine && GEngine->GameViewport)
    {
        Overlay=SNew(SOverlay)+SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Top).Padding(15)
        [ SNew(SBorder).Padding(12).BorderBackgroundColor(FLinearColor(.02f,.015f,.035f,.96f))
          [ SNew(SVerticalBox)
            +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0,0,0,5)
            [ SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Bold",18)).ColorAndOpacity(FLinearColor(1,.77f,.3f)).Text_Lambda([this](){return GetSettingsText();}) ]
            +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0,0,0,5)
            [ SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",16)).ColorAndOpacity(FLinearColor::White).Text_Lambda([this](){return GetChoicesText();}) ]
            +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)
            [ SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Bold",15)).ColorAndOpacity(FLinearColor(.55f,1,.7f)).Text_Lambda([this](){return GetMessageText();}) ] ] ];
        GEngine->GameViewport->AddViewportWidgetContent(Overlay.ToSharedRef(),50);
    }
}
void AFilmRestorePuzzle::LeavePuzzle()
{
    if (!bActive) return;
    if (APlayerController* PC=UGameplayStatics::GetPlayerController(this,0))
    {
        PC->SetIgnoreMoveInput(false);if (PreviousView.IsValid()) PC->SetViewTarget(PreviousView.Get());else if (PC->GetPawn()) PC->SetViewTarget(PC->GetPawn());
    }
    if (Overlay.IsValid() && GEngine && GEngine->GameViewport) GEngine->GameViewport->RemoveViewportWidgetContent(Overlay.ToSharedRef());
    Overlay.Reset();bActive=false;
}
void AFilmRestorePuzzle::SelectFilm(int32 Film)
{
    CurrentFilm=FMath::Clamp(Film,1,3);
    ClueA->SetVisibility(CurrentFilm==1);ClueB->SetVisibility(CurrentFilm==2);ClueC->SetVisibility(CurrentFilm==3);
    ShadowMask->SetVisibility(CurrentFilm==2 && bShadowOn);
}
void AFilmRestorePuzzle::ApplySettings()
{
    if (IsValid(PostProcessVolume))
    {
        auto& S=PostProcessVolume->Settings;
        S.bOverride_BloomIntensity=true;S.BloomIntensity=bBloomOn?FMath::Max(BloomIntensity,0.f):0.f;
        S.bOverride_BloomThreshold=true;S.BloomThreshold=1.f;
        S.bOverride_AutoExposureMethod=true;S.AutoExposureMethod=AEM_Manual;
        S.bOverride_AutoExposureApplyPhysicalCameraExposure=true;S.AutoExposureApplyPhysicalCameraExposure=false;
        S.bOverride_AutoExposureBias=true;S.AutoExposureBias=bDarkExposure?DarkExposure:BrightExposure;
    }
    if (auto* Graphics=GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>()) Graphics->SetHigh(EDirectorCutGraphicsOption::Shadows,bShadowOn);
    ShadowMask->SetVisibility(CurrentFilm==2 && bShadowOn);
}
void AFilmRestorePuzzle::Submit()
{
    if (!bActive || bSolved) return;
    if (SceneChoice==3 && DirectionChoice==1 && MarkChoice==2)
    {
        bSolved=true;bCompleting=true;FinishTime=2.f;
        ClueA->SetVisibility(false);ClueB->SetVisibility(false);ClueC->SetVisibility(false);ShadowMask->SetVisibility(false);
        bBloomOn=false;bDarkExposure=false;ApplySettings();ShadowMask->SetVisibility(false);
        RestoredRecord->SetVisibility(true);
    }
    else { bWrong=true;MessageTime=2.f; }
}
void AFilmRestorePuzzle::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (MessageTime>0) MessageTime=FMath::Max(0.f,MessageTime-DeltaSeconds);
    if (bCompleting)
    {
        FinishTime-=DeltaSeconds;
        if (FinishTime<=0) { bCompleting=false; if (IsValid(ExitDoor)) ExitDoor->OpenDoor(); OnSolved(); LeavePuzzle(); }
        return;
    }
    APlayerController* PC=UGameplayStatics::GetPlayerController(this,0);if (!PC) return;
    if (PC->WasInputKeyJustPressed(EKeys::E)) { if (bActive) LeavePuzzle();else EnterPuzzle();return; }
    if (!bActive) return;
    if (PC->WasInputKeyJustPressed(EKeys::One)) SelectFilm(1);
    if (PC->WasInputKeyJustPressed(EKeys::Two)) SelectFilm(2);
    if (PC->WasInputKeyJustPressed(EKeys::Three)) SelectFilm(3);
    if (PC->WasInputKeyJustPressed(EKeys::B)) { bBloomOn=!bBloomOn;ApplySettings(); }
    if (PC->WasInputKeyJustPressed(EKeys::Q)) { bShadowOn=!bShadowOn;ApplySettings(); }
    if (PC->WasInputKeyJustPressed(EKeys::N)) { bDarkExposure=!bDarkExposure;ApplySettings(); }
    if (PC->WasInputKeyJustPressed(EKeys::Four)) SceneChoice=SceneChoice%3+1;
    if (PC->WasInputKeyJustPressed(EKeys::Five)) DirectionChoice=1-DirectionChoice;
    if (PC->WasInputKeyJustPressed(EKeys::Six)) MarkChoice=(MarkChoice+1)%3;
    if (PC->WasInputKeyJustPressed(EKeys::Enter)) Submit();
}
