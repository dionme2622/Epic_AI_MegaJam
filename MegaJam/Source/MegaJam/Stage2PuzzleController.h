#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Stage2PuzzleController.generated.h"

class APostProcessVolume;
class ALight;

UENUM(BlueprintType)
enum class EStage2Symbol : uint8 { Star, Moon, Sun };

UENUM(BlueprintType)
enum class EStage2Film : uint8 { None, A, B, C };

UENUM(BlueprintType)
enum class EStage2Direction : uint8 { Left, Right };

UENUM(BlueprintType)
enum class EStage2Mark : uint8 { Gear, Star, Moon };

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FStage2PuzzleCompleted, int32, PuzzleNumber);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FStage2SequenceUpdated, int32, CorrectCount);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FStage2FilmChanged, EStage2Film, Film);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FStage2SettingsChanged);

/** Stage 2 logic only. Assign level actors and bind events in Blueprint; no level geometry is created. */
UCLASS(Blueprintable)
class MEGAJAM_API AStage2PuzzleController : public AActor
{
    GENERATED_BODY()
public:
    AStage2PuzzleController();
    virtual void BeginPlay() override;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Stage 2|Rendering")
    TObjectPtr<APostProcessVolume> PostProcessVolume;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Stage 2|Rendering")
    TArray<TObjectPtr<ALight>> PuzzleLights;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Stage 2|Rendering", meta=(ClampMin="0"))
    float BloomOnIntensity = 1.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Stage 2|Rendering")
    float BrightExposureCompensation = 1.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Stage 2|Rendering")
    float DarkExposureCompensation = -1.0f;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Stage 2|Shadow")
    TObjectPtr<AActor> ShadowPieceA;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Stage 2|Shadow")
    TObjectPtr<AActor> ShadowPieceB;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Stage 2|Shadow", meta=(MakeEditWidget=true))
    FVector ShadowTargetA = FVector::ZeroVector;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Stage 2|Shadow", meta=(MakeEditWidget=true))
    FVector ShadowTargetB = FVector::ZeroVector;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Stage 2|Shadow", meta=(ClampMin="0"))
    float ShadowTolerance = 25.f;

    UPROPERTY(BlueprintReadOnly, Category="Stage 2|State") bool bShadowsOn = true;
    UPROPERTY(BlueprintReadOnly, Category="Stage 2|State") bool bBloomOn = true;
    UPROPERTY(BlueprintReadOnly, Category="Stage 2|State") bool bExposureDark = false;
    UPROPERTY(BlueprintReadOnly, Category="Stage 2|State") bool bShadowSolved = false;
    UPROPERTY(BlueprintReadOnly, Category="Stage 2|State") bool bSequenceSolved = false;
    UPROPERTY(BlueprintReadOnly, Category="Stage 2|State") bool bFilmSolved = false;
    UPROPERTY(BlueprintReadOnly, Category="Stage 2|State") int32 SequenceProgress = 0;
    UPROPERTY(BlueprintReadOnly, Category="Stage 2|State") EStage2Film CurrentFilm = EStage2Film::None;

    UPROPERTY(BlueprintAssignable, Category="Stage 2|Events") FStage2PuzzleCompleted OnPuzzleCompleted;
    UPROPERTY(BlueprintAssignable, Category="Stage 2|Events") FStage2SequenceUpdated OnSequenceUpdated;
    UPROPERTY(BlueprintAssignable, Category="Stage 2|Events") FStage2FilmChanged OnFilmChanged;
    UPROPERTY(BlueprintAssignable, Category="Stage 2|Events") FStage2SettingsChanged OnSettingsChanged;

    UFUNCTION(BlueprintCallable, Category="Stage 2|Rendering") void SetShadowsEnabled(bool bEnabled);
    UFUNCTION(BlueprintCallable, Category="Stage 2|Rendering") void SetBloomEnabled(bool bEnabled);
    UFUNCTION(BlueprintCallable, Category="Stage 2|Rendering") void SetDarkExposure(bool bDark);
    UFUNCTION(BlueprintCallable, Category="Stage 2|Shadow") bool CheckShadowPuzzle();
    UFUNCTION(BlueprintPure, Category="Stage 2|Shadow") bool IsShadowPieceAtTarget(AActor* Piece, FVector Target) const;
    /** Moves an assigned piece along world X, clamped to a rail, then checks the puzzle. */
    UFUNCTION(BlueprintCallable, Category="Stage 2|Shadow") bool MoveShadowPiece(AActor* Piece, float DeltaX, float RailMinX, float RailMaxX);
    UFUNCTION(BlueprintCallable, Category="Stage 2|Sequence") bool EnterSymbol(EStage2Symbol Symbol);
    UFUNCTION(BlueprintCallable, Category="Stage 2|Sequence") void ResetSequence();
    UFUNCTION(BlueprintCallable, Category="Stage 2|Film") void SelectFilm(EStage2Film Film);
    UFUNCTION(BlueprintPure, Category="Stage 2|Film") bool IsCurrentFilmClueVisible() const;
    UFUNCTION(BlueprintCallable, Category="Stage 2|Film") bool SubmitFilmSolution(int32 SceneNumber, EStage2Direction Direction, EStage2Mark Mark);
};
