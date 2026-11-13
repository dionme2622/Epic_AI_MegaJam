#include "Stage2PuzzleController.h"
#include "Components/LightComponent.h"
#include "Engine/Light.h"
#include "Engine/PostProcessVolume.h"
#include "Engine/Scene.h"

AStage2PuzzleController::AStage2PuzzleController()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AStage2PuzzleController::BeginPlay()
{
    Super::BeginPlay();
    SetShadowsEnabled(bShadowsOn);
    SetBloomEnabled(bBloomOn);
    SetDarkExposure(bExposureDark);
}

void AStage2PuzzleController::SetShadowsEnabled(bool bEnabled)
{
    bShadowsOn = bEnabled;
    for (ALight* Light : PuzzleLights)
    {
        if (IsValid(Light) && Light->GetLightComponent())
            Light->GetLightComponent()->SetCastShadows(bEnabled);
    }
    OnSettingsChanged.Broadcast();
    CheckShadowPuzzle();
}

void AStage2PuzzleController::SetBloomEnabled(bool bEnabled)
{
    bBloomOn = bEnabled;
    if (IsValid(PostProcessVolume))
    {
        FPostProcessSettings& Settings = PostProcessVolume->Settings;
        Settings.bOverride_BloomIntensity = true;
        Settings.BloomIntensity = bEnabled ? BloomOnIntensity : 0.f;
    }
    OnSettingsChanged.Broadcast();
}

void AStage2PuzzleController::SetDarkExposure(bool bDark)
{
    bExposureDark = bDark;
    if (IsValid(PostProcessVolume))
    {
        FPostProcessSettings& Settings = PostProcessVolume->Settings;
        Settings.bOverride_AutoExposureMethod = true;
        Settings.AutoExposureMethod = AEM_Manual;
        Settings.bOverride_AutoExposureBias = true;
        Settings.AutoExposureBias = bDark ? DarkExposureCompensation : BrightExposureCompensation;
    }
    OnSettingsChanged.Broadcast();
}

bool AStage2PuzzleController::IsShadowPieceAtTarget(AActor* Piece, FVector Target) const
{
    return IsValid(Piece) && FVector::DistSquared(Piece->GetActorLocation(), Target) <= FMath::Square(FMath::Max(ShadowTolerance, 0.f));
}

bool AStage2PuzzleController::CheckShadowPuzzle()
{
    if (!bShadowSolved && bShadowsOn && IsValid(ShadowPieceA) && IsValid(ShadowPieceB)
        && ShadowPieceA != ShadowPieceB && IsShadowPieceAtTarget(ShadowPieceA, ShadowTargetA)
        && IsShadowPieceAtTarget(ShadowPieceB, ShadowTargetB))
    {
        bShadowSolved = true;
        OnPuzzleCompleted.Broadcast(1);
    }
    return bShadowSolved;
}

bool AStage2PuzzleController::MoveShadowPiece(AActor* Piece, float DeltaX, float RailMinX, float RailMaxX)
{
    if (bShadowSolved || !IsValid(Piece) || (Piece != ShadowPieceA && Piece != ShadowPieceB) || RailMinX > RailMaxX)
        return false;
    FVector Location = Piece->GetActorLocation();
    Location.X = FMath::Clamp(Location.X + DeltaX, RailMinX, RailMaxX);
    Piece->SetActorLocation(Location, true);
    CheckShadowPuzzle();
    return true;
}

bool AStage2PuzzleController::EnterSymbol(EStage2Symbol Symbol)
{
    if (bSequenceSolved) return true;
    static constexpr EStage2Symbol Answer[] = { EStage2Symbol::Star, EStage2Symbol::Moon, EStage2Symbol::Sun };
    if (Symbol == Answer[SequenceProgress]) ++SequenceProgress;
    else SequenceProgress = 0;
    OnSequenceUpdated.Broadcast(SequenceProgress);
    if (SequenceProgress == UE_ARRAY_COUNT(Answer))
    {
        bSequenceSolved = true;
        OnPuzzleCompleted.Broadcast(2);
    }
    return bSequenceSolved;
}

void AStage2PuzzleController::ResetSequence()
{
    if (!bSequenceSolved) { SequenceProgress = 0; OnSequenceUpdated.Broadcast(0); }
}

void AStage2PuzzleController::SelectFilm(EStage2Film Film)
{
    CurrentFilm = Film;
    OnFilmChanged.Broadcast(Film);
}

bool AStage2PuzzleController::IsCurrentFilmClueVisible() const
{
    switch (CurrentFilm)
    {
    case EStage2Film::A: return !bBloomOn;
    case EStage2Film::B: return !bShadowsOn;
    case EStage2Film::C: return bExposureDark;
    default: return false;
    }
}

bool AStage2PuzzleController::SubmitFilmSolution(int32 SceneNumber, EStage2Direction Direction, EStage2Mark Mark)
{
    if (!bFilmSolved && SceneNumber == 3 && Direction == EStage2Direction::Right && Mark == EStage2Mark::Gear)
    {
        bFilmSolved = true;
        OnPuzzleCompleted.Broadcast(3);
    }
    return bFilmSolved;
}
