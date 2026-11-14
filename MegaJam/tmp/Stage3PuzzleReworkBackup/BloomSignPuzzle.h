#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BloomSignPuzzle.generated.h"

class UStaticMeshComponent;
class APostProcessVolume;
class AStage2ShadowDoor;
class SWidget;

UCLASS(Blueprintable)
class MEGAJAM_API ABloomPuzzleSign : public AActor
{
    GENERATED_BODY()
public:
    ABloomPuzzleSign();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Bloom Puzzle") TObjectPtr<USceneComponent> Root;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Bloom Puzzle") TObjectPtr<UStaticMeshComponent> Frame;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Bloom Puzzle") TObjectPtr<UStaticMeshComponent> Face;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Bloom Puzzle") TObjectPtr<UStaticMeshComponent> Symbol;
};

UCLASS(Blueprintable)
class MEGAJAM_API ABloomSignPuzzle : public AActor
{
    GENERATED_BODY()
public:
    ABloomSignPuzzle();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void Tick(float DeltaSeconds) override;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Bloom Puzzle") TObjectPtr<USceneComponent> Root;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Bloom Puzzle") TObjectPtr<UStaticMeshComponent> ConsoleMesh;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Bloom Puzzle") TObjectPtr<APostProcessVolume> PostProcessVolume;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Bloom Puzzle") TObjectPtr<AStage2ShadowDoor> ExitDoor;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Bloom Puzzle", meta=(ClampMin="0")) float BloomIntensity = 7.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Bloom Puzzle", meta=(ClampMin="0")) float InteractDistance = 220.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Bloom Puzzle|Integration") bool bRestrictToArea = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Bloom Puzzle|Integration") float AreaMinOffsetX = -2500.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Bloom Puzzle|Integration") float AreaMaxOffsetX = 500.f;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Bloom Puzzle|Film Editing") bool bUseFilmEditing = false;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Bloom Puzzle|Film Editing", meta=(EditCondition="bUseFilmEditing"))
    TArray<TObjectPtr<AActor>> FilmSources;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Bloom Puzzle|Film Editing", meta=(EditCondition="bUseFilmEditing"))
    TArray<TObjectPtr<AActor>> FilmScenes;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Bloom Puzzle|Film Editing", meta=(ClampMin="0"))
    float FilmPickupDistance = 180.f;
    UPROPERTY(BlueprintReadOnly, Category="Bloom Puzzle|Film Editing") TArray<int32> CollectedFilms;
    UPROPERTY(BlueprintReadOnly, Category="Bloom Puzzle|Film Editing") TArray<int32> FilmSequence;
    UPROPERTY(BlueprintReadOnly, Category="Bloom Puzzle") bool bBloomOn = true;
    UPROPERTY(BlueprintReadOnly, Category="Bloom Puzzle") bool bConsoleOpen = false;
    UPROPERTY(BlueprintReadOnly, Category="Bloom Puzzle") bool bSolved = false;
    UPROPERTY(BlueprintReadOnly, Category="Bloom Puzzle") int32 SequenceProgress = 0;
    UFUNCTION(BlueprintCallable, Category="Bloom Puzzle") void SetBloomEnabled(bool bEnabled);
    UFUNCTION(BlueprintCallable, Category="Bloom Puzzle") void EnterSymbol(int32 Index);
    UFUNCTION(BlueprintCallable, Category="Bloom Puzzle") void OpenConsole();
    UFUNCTION(BlueprintCallable, Category="Bloom Puzzle") void CloseConsole();
    UFUNCTION(BlueprintImplementableEvent, Category="Bloom Puzzle") void OnPuzzleSolved();
private:
    TSharedPtr<SWidget> Overlay;
    float MessageTime = 0.f;
    bool bWrong = false;
    bool bFinishing = false;
    int32 WrongFilmSlot = INDEX_NONE;
    float FinishTime = 0.f;
    TSharedPtr<SWidget> FilmHintOverlay;
    int32 FindNearbyFilm() const;
    FText GetFilmHint() const;
    void TryFilmPlayback();
    FText GetStatusText() const;
    FText GetProgressText() const;
};
