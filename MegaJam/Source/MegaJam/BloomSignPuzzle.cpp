#include "BloomSignPuzzle.h"
#include "DirectorCutGraphics.h"
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
void ABloomSignPuzzle::BeginPlay()
{
    Super::BeginPlay();
    SetBloomEnabled(bBloomOn);
    if (bRestrictToArea && IsValid(PostProcessVolume)) PostProcessVolume->BlendWeight = 0.f;
    if ((bUseFilmEditing || bUseShutterPuzzle) && GEngine && GEngine->GameViewport)
    {
        FilmHintOverlay = SNew(SOverlay).Visibility(EVisibility::HitTestInvisible)
            + SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Bottom).Padding(20.f, 20.f)
            [
                SNew(SBorder).Padding(FMargin(16.f, 8.f))
                .BorderBackgroundColor(FLinearColor(.025f, .018f, .04f, .95f))
                .Visibility_Lambda([this]
                {
                    return GetFilmHint().IsEmpty() ? EVisibility::Collapsed : EVisibility::HitTestInvisible;
                })
                [
                    SNew(STextBlock).Text_Lambda([this] { return GetFilmHint(); })
                    .Font(FCoreStyle::GetDefaultFontStyle("Regular", 16))
                    .ColorAndOpacity(FLinearColor(1.f, .87f, .65f))
                ]
            ];
        GEngine->GameViewport->AddViewportWidgetContent(FilmHintOverlay.ToSharedRef(), 45);
    }
}
void ABloomSignPuzzle::EndPlay(const EEndPlayReason::Type Reason)
{
    CloseConsole();
    if (FilmHintOverlay.IsValid() && GEngine && GEngine->GameViewport)
        GEngine->GameViewport->RemoveViewportWidgetContent(FilmHintOverlay.ToSharedRef());
    FilmHintOverlay.Reset();
    Super::EndPlay(Reason);
}
void ABloomSignPuzzle::SetBloomEnabled(bool bEnabled)
{
    bBloomOn = bEnabled;
    if (bUseFilmEditing)
    {
        for (AActor* Scene : FilmScenes)
        {
            if (IsValid(Scene)) Scene->SetActorHiddenInGame(bEnabled);
        }
    }
    if (bUseShutterPuzzle)
        for (AActor* Clue : ShutterClues)
            if (IsValid(Clue)) Clue->SetActorHiddenInGame(bEnabled);
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
    if (bUseShutterPuzzle)
    {
        if (bSolved) return FText::FromString(TEXT("LIGHT BOARD RESTORED - EXIT OPEN"));
        if (bWrong && MessageTime > 0.f) return FText::FromString(TEXT("SHUTTERS DO NOT MATCH - TRY AGAIN"));
        return FText::FromString(FString::Printf(TEXT("STAR  %s       MOON  %s       SUN  %s"),
            (ShutterMask & 1) ? TEXT("OPEN") : TEXT("CLOSED"),
            (ShutterMask & 2) ? TEXT("OPEN") : TEXT("CLOSED"),
            (ShutterMask & 4) ? TEXT("OPEN") : TEXT("CLOSED")));
    }
    if (bUseFilmEditing)
    {
        if (bSolved) return FText::FromString(TEXT("FILM RESTORED - THE STORE ROOM IS OPEN"));
        if (bWrong && WrongFilmSlot != INDEX_NONE)
            return FText::FromString(FString::Printf(TEXT("THE FILM BREAKS AT SLOT %d - PRESS R TO REVISE"), WrongFilmSlot + 1));
        const TCHAR* Names[] = {TEXT("STAR"), TEXT("MOON"), TEXT("SUN")};
        FString Text(TEXT("FILM SLOTS"));
        for (int32 Slot = 0; Slot < 3; ++Slot)
        {
            const FString Value = FilmSequence.IsValidIndex(Slot) ? Names[FilmSequence[Slot] - 1] : TEXT("--");
            Text += FString::Printf(TEXT("    %d: %s"), Slot + 1, *Value);
        }
        return FText::FromString(Text);
    }
    if (bSolved) return FText::FromString(TEXT("SEQUENCE COMPLETE"));
    if (bWrong && MessageTime > 0) return FText::FromString(TEXT("INCORRECT - TRY AGAIN"));
    return FText::FromString(FString::Printf(TEXT("INPUT: %d / 3"),SequenceProgress));
}
FText ABloomSignPuzzle::GetStatusText() const
{
    if (bUseShutterPuzzle) return FText::FromString(TEXT("1 / 2 / 3: SWITCH   |   ENTER: TEST   |   B: BLOOM   |   R: RESET   |   E: LEAVE"));
    if (bUseFilmEditing)
    {
        return FText::FromString(TEXT("1 / 2 / 3: PLACE FILM   |   R: UNDO   |   B: PROJECT   |   E: LEAVE"));
    }
    return FText::FromString(TEXT("1: STAR     2: MOON     3: SUN     |     E: LEAVE"));
}
void ABloomSignPuzzle::OpenConsole()
{
    APlayerController* PC=UGameplayStatics::GetPlayerController(this,0); APawn* Pawn=PC?PC->GetPawn():nullptr;
    if (!PC || !Pawn || bSolved || bConsoleOpen || FVector::Dist2D(Pawn->GetActorLocation(),GetActorLocation())>InteractDistance) return;
    if (bUseFilmEditing && CollectedFilms.Num() != 3)
    {
        MessageTime = 2.f;
        return;
    }
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
    if (bUseShutterPuzzle)
    {
        ShutterMask ^= (1 << (Index - 1));
        bWrong = false;
        return;
    }
    if (bUseFilmEditing)
    {
        if (FilmSequence.Num() == 3 || FilmSequence.Contains(Index) || !CollectedFilms.Contains(Index)) return;
        FilmSequence.Add(Index);
        SequenceProgress = FilmSequence.Num();
        bWrong = false;
        WrongFilmSlot = INDEX_NONE;
        return;
    }
    if (Index == SequenceProgress + 1) { ++SequenceProgress; bWrong=false; }
    else { SequenceProgress=0; bWrong=true; MessageTime=1.5f; }
    if (SequenceProgress==3) { bSolved=true; bFinishing=true; FinishTime=1.3f; }
}

int32 ABloomSignPuzzle::FindNearbyFilm() const
{
    const APawn* Pawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (!Pawn) return INDEX_NONE;
    int32 ClosestIndex = INDEX_NONE;
    double ClosestDistance = FilmPickupDistance;
    for (int32 Index = 0; Index < FilmSources.Num() && Index < 3; ++Index)
    {
        if (!IsValid(FilmSources[Index]) || CollectedFilms.Contains(Index + 1)) continue;
        const double Distance = FVector::Dist2D(Pawn->GetActorLocation(), FilmSources[Index]->GetActorLocation());
        if (Distance <= ClosestDistance)
        {
            ClosestDistance = Distance;
            ClosestIndex = Index;
        }
    }
    return ClosestIndex;
}

FText ABloomSignPuzzle::GetFilmHint() const
{
    const APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
    const APawn* Pawn = PC ? PC->GetPawn() : nullptr;
    const ADirectorCutPlayerController* Director = Cast<ADirectorCutPlayerController>(PC);
    if ((!bUseFilmEditing && !bUseShutterPuzzle) || bSolved || bConsoleOpen || !Pawn || (Director && Director->IsGraphicsMenuOpen()))
        return FText::GetEmpty();
    const double Offset = Pawn->GetActorLocation().X - GetActorLocation().X;
    if (bRestrictToArea && (Offset < AreaMinOffsetX || Offset > AreaMaxOffsetX)) return FText::GetEmpty();
    if (bUseShutterPuzzle)
    {
        if (FVector::Dist2D(Pawn->GetActorLocation(), GetActorLocation()) <= InteractDistance)
            return FText::FromString(TEXT("E: LIGHT BOARD   |   B: BLOOM ON / OFF"));
        return FText::FromString(bBloomOn
            ? TEXT("B: TURN BLOOM OFF TO READ THE SHUTTER CUES")
            : TEXT("MATCH THE THREE SHUTTER CUES AT THE LIGHT BOARD"));
    }
    if (MessageTime > 0 && CollectedFilms.Num() < 3 &&
        FVector::Dist2D(Pawn->GetActorLocation(), GetActorLocation()) <= InteractDistance)
        return FText::FromString(TEXT("FIND ALL THREE FILM REELS AT THE SIGNS"));
    const int32 Index = FindNearbyFilm();
    if (Index != INDEX_NONE)
    {
        const TCHAR* Names[] = {TEXT("STAR"), TEXT("MOON"), TEXT("SUN")};
        return bBloomOn
            ? FText::FromString(TEXT("B: TURN BLOOM OFF TO FIND THE FILM"))
            : FText::FromString(FString::Printf(TEXT("E: COLLECT %s FILM    (%d / 3)"), Names[Index], CollectedFilms.Num()));
    }
    if (FVector::Dist2D(Pawn->GetActorLocation(), GetActorLocation()) <= InteractDistance)
        return FText::FromString(CollectedFilms.Num() == 3 ? TEXT("E: EDIT THE THREE FILM REELS") : TEXT("B: BLOOM ON / OFF"));
    return FText::GetEmpty();
}

void ABloomSignPuzzle::TryFilmPlayback()
{
    if (!bUseFilmEditing || !bConsoleOpen || !bBloomOn || bSolved || FilmSequence.Num() != 3) return;
    for (int32 Slot = 0; Slot < 3; ++Slot)
    {
        if (FilmSequence[Slot] != Slot + 1)
        {
            bWrong = true;
            WrongFilmSlot = Slot;
            return;
        }
    }
    bWrong = false;
    bSolved = true;
    bFinishing = true;
    FinishTime = 2.5f;
}
void ABloomSignPuzzle::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (bRestrictToArea)
    {
        const APawn* Pawn=UGameplayStatics::GetPlayerPawn(this,0);
        const float Offset=Pawn ? Pawn->GetActorLocation().X-GetActorLocation().X : TNumericLimits<float>::Max();
        const bool bInArea=Pawn && Offset>=AreaMinOffsetX && Offset<=AreaMaxOffsetX;
        if (IsValid(PostProcessVolume)) PostProcessVolume->BlendWeight=bInArea ? 1.f : 0.f;
        if (!bInArea) { if (bConsoleOpen) CloseConsole(); return; }
    }
    if (MessageTime>0) MessageTime=FMath::Max(0.f,MessageTime-DeltaSeconds);
    if (bFinishing)
    {
        FinishTime-=DeltaSeconds;
        if (bUseFilmEditing)
        {
            const int32 ProjectedScene = FMath::Clamp(FMath::FloorToInt((2.5f - FinishTime) * 1.2f), 0, 2);
            for (int32 Index = 0; Index < FilmScenes.Num(); ++Index)
                if (IsValid(FilmScenes[Index])) FilmScenes[Index]->SetActorHiddenInGame(Index != ProjectedScene || FinishTime <= 0.f);
        }
        if (FinishTime<=0) { bFinishing=false; if (IsValid(ExitDoor)) ExitDoor->OpenDoor(); OnPuzzleSolved(); CloseConsole(); }
        return;
    }
    APlayerController* PC=UGameplayStatics::GetPlayerController(this,0); if (!PC) return;
    const auto* Director = Cast<ADirectorCutPlayerController>(PC);
    if (Director && Director->IsGraphicsMenuOpen()) return;
    if (PC->WasInputKeyJustPressed(EKeys::B))
    {
        SetBloomEnabled(!bBloomOn);
        TryFilmPlayback();
    }
    if (PC->WasInputKeyJustPressed(EKeys::E))
    {
        if (bConsoleOpen) CloseConsole();
        else if (bUseFilmEditing)
        {
            const int32 NearbyFilm = FindNearbyFilm();
            if (NearbyFilm != INDEX_NONE && !bBloomOn)
            {
                CollectedFilms.AddUnique(NearbyFilm + 1);
                MessageTime = 0.f;
            }
            else OpenConsole();
        }
        else OpenConsole();
        return;
    }
    if (!bConsoleOpen) return;
    if (bUseShutterPuzzle)
    {
        if (PC->WasInputKeyJustPressed(EKeys::R)) { ShutterMask = 0; bWrong = false; }
        if (PC->WasInputKeyJustPressed(EKeys::Enter))
        {
            if (ShutterMask == TargetShutterMask)
            {
                bSolved = true; bFinishing = true; FinishTime = 1.3f; bWrong = false;
            }
            else { bWrong = true; MessageTime = 2.f; }
        }
    }
    if (bUseFilmEditing && PC->WasInputKeyJustPressed(EKeys::R) && !FilmSequence.IsEmpty())
    {
        FilmSequence.Pop();
        SequenceProgress = FilmSequence.Num();
        bWrong = false;
        WrongFilmSlot = INDEX_NONE;
    }
    if (PC->WasInputKeyJustPressed(EKeys::One)) EnterSymbol(1);
    if (PC->WasInputKeyJustPressed(EKeys::Two)) EnterSymbol(2);
    if (PC->WasInputKeyJustPressed(EKeys::Three)) EnterSymbol(3);
}
