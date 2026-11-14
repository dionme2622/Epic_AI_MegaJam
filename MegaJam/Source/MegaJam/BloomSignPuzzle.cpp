#include "BloomSignPuzzle.h"
#include "Stage2ShadowPrototype.h"
#include "Components/StaticMeshComponent.h"
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

ABloomPuzzleSign::ABloomPuzzleSign()
{
    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root")); SetRootComponent(Root);
    Frame = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Frame")); Frame->SetupAttachment(Root);
    Face = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Face")); Face->SetupAttachment(Root);
    Symbol = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Symbol")); Symbol->SetupAttachment(Root);
    Frame->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Face->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Symbol->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Face->SetRelativeLocation(FVector(0,0,0));
    Symbol->SetRelativeLocation(FVector(0,10,0));
}

ABloomSignPuzzle::ABloomSignPuzzle()
{
    PrimaryActorTick.bCanEverTick = true;
    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root")); SetRootComponent(Root);
    ConsoleMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ConsoleMesh")); ConsoleMesh->SetupAttachment(Root);
    ConsoleMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}
void ABloomSignPuzzle::BeginPlay() { Super::BeginPlay(); SetBloomEnabled(bBloomOn); }
void ABloomSignPuzzle::EndPlay(const EEndPlayReason::Type Reason) { CloseConsole(); Super::EndPlay(Reason); }
void ABloomSignPuzzle::SetBloomEnabled(bool bEnabled)
{
    bBloomOn = bEnabled;
    if (IsValid(PostProcessVolume))
    {
        auto& S=PostProcessVolume->Settings;
        S.bOverride_BloomIntensity = true; S.BloomIntensity = bEnabled ? FMath::Max(BloomIntensity,0.f) : 0.f;
        S.bOverride_BloomThreshold = true; S.BloomThreshold = 1.f;
        S.bOverride_AutoExposureMethod = true; S.AutoExposureMethod = AEM_Manual;
        S.bOverride_AutoExposureBias = true; S.AutoExposureBias = 0.f;
    }
}
FText ABloomSignPuzzle::GetProgressText() const
{
    if (bSolved) return FText::FromString(TEXT("SEQUENCE COMPLETE"));
    if (bWrong && MessageTime > 0) return FText::FromString(TEXT("INCORRECT - TRY AGAIN"));
    return FText::FromString(FString::Printf(TEXT("INPUT: %d / 3"),SequenceProgress));
}
FText ABloomSignPuzzle::GetStatusText() const
{
    return FText::FromString(TEXT("1: STAR     2: MOON     3: SUN     |     E: LEAVE"));
}
void ABloomSignPuzzle::OpenConsole()
{
    APlayerController* PC=UGameplayStatics::GetPlayerController(this,0); APawn* Pawn=PC?PC->GetPawn():nullptr;
    if (!PC || !Pawn || bSolved || bConsoleOpen || FVector::Dist2D(Pawn->GetActorLocation(),GetActorLocation())>InteractDistance) return;
    bConsoleOpen=true; PC->SetIgnoreMoveInput(true);
    if (ACharacter* C=Cast<ACharacter>(Pawn)) C->GetCharacterMovement()->StopMovementImmediately();
    if (GEngine && GEngine->GameViewport)
    {
        Overlay=SNew(SOverlay)+SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Top).Padding(15)
        [ SNew(SBorder).Padding(14).BorderBackgroundColor(FLinearColor(.025f,.018f,.04f,.95f))
          [ SNew(SVerticalBox)
            +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0,0,0,8)
            [ SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Bold",20)).ColorAndOpacity(FLinearColor(1.f,.75f,.25f)).Text_Lambda([this](){return GetProgressText();}) ]
            +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)
            [ SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",16)).ColorAndOpacity(FLinearColor::White).Text_Lambda([this](){return GetStatusText();}) ] ] ];
        GEngine->GameViewport->AddViewportWidgetContent(Overlay.ToSharedRef(),50);
    }
}
void ABloomSignPuzzle::CloseConsole()
{
    if (!bConsoleOpen) return;
    if (APlayerController* PC=UGameplayStatics::GetPlayerController(this,0)) PC->SetIgnoreMoveInput(false);
    if (Overlay.IsValid() && GEngine && GEngine->GameViewport) GEngine->GameViewport->RemoveViewportWidgetContent(Overlay.ToSharedRef());
    Overlay.Reset();bConsoleOpen=false;
}
void ABloomSignPuzzle::EnterSymbol(int32 Index)
{
    if (!bConsoleOpen || bSolved || Index < 1 || Index > 3) return;
    if (Index == SequenceProgress + 1) { ++SequenceProgress; bWrong=false; }
    else { SequenceProgress=0; bWrong=true; MessageTime=1.5f; }
    if (SequenceProgress==3) { bSolved=true; bFinishing=true; FinishTime=1.3f; }
}
void ABloomSignPuzzle::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (MessageTime>0) MessageTime=FMath::Max(0.f,MessageTime-DeltaSeconds);
    if (bFinishing)
    {
        FinishTime-=DeltaSeconds;
        if (FinishTime<=0) { bFinishing=false; if (IsValid(ExitDoor)) ExitDoor->OpenDoor(); OnPuzzleSolved(); CloseConsole(); }
        return;
    }
    APlayerController* PC=UGameplayStatics::GetPlayerController(this,0); if (!PC) return;
    if (PC->WasInputKeyJustPressed(EKeys::B)) SetBloomEnabled(!bBloomOn);
    if (PC->WasInputKeyJustPressed(EKeys::E)) { if (bConsoleOpen) CloseConsole(); else OpenConsole(); return; }
    if (!bConsoleOpen) return;
    if (PC->WasInputKeyJustPressed(EKeys::One)) EnterSymbol(1);
    if (PC->WasInputKeyJustPressed(EKeys::Two)) EnterSymbol(2);
    if (PC->WasInputKeyJustPressed(EKeys::Three)) EnterSymbol(3);
}
