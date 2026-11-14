#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FilmRestorePuzzle.generated.h"

class UCameraComponent;
class UStaticMeshComponent;
class UTextRenderComponent;
class APostProcessVolume;
class AStage2ShadowDoor;
class SWidget;

UCLASS(Blueprintable)
class MEGAJAM_API AFilmRestorePuzzle : public AActor
{
    GENERATED_BODY()
public:
    AFilmRestorePuzzle();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void Tick(float DeltaSeconds) override;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Film Puzzle") TObjectPtr<USceneComponent> Root;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Film Puzzle") TObjectPtr<UStaticMeshComponent> Frame;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Film Puzzle") TObjectPtr<UStaticMeshComponent> Screen;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Film Puzzle") TObjectPtr<UStaticMeshComponent> ClueA;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Film Puzzle") TObjectPtr<UStaticMeshComponent> ClueB;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Film Puzzle") TObjectPtr<UStaticMeshComponent> ClueC;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Film Puzzle") TObjectPtr<UStaticMeshComponent> ShadowMask;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Film Puzzle") TObjectPtr<UTextRenderComponent> RestoredRecord;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Film Puzzle") TObjectPtr<UCameraComponent> PuzzleCamera;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Film Puzzle") TObjectPtr<APostProcessVolume> PostProcessVolume;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Film Puzzle") TObjectPtr<AStage2ShadowDoor> ExitDoor;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Film Puzzle", meta=(ClampMin="0")) float InteractDistance = 250.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Film Puzzle", meta=(ClampMin="0")) float BloomIntensity = 70.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Film Puzzle") float BrightExposure = 1.5f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Film Puzzle") float DarkExposure = -3.f;
    UPROPERTY(BlueprintReadOnly, Category="Film Puzzle") bool bActive = false;
    UPROPERTY(BlueprintReadOnly, Category="Film Puzzle") bool bSolved = false;
    UPROPERTY(BlueprintReadOnly, Category="Film Puzzle") bool bBloomOn = true;
    UPROPERTY(BlueprintReadOnly, Category="Film Puzzle") bool bShadowOn = true;
    UPROPERTY(BlueprintReadOnly, Category="Film Puzzle") bool bDarkExposure = false;
    UPROPERTY(BlueprintReadOnly, Category="Film Puzzle") int32 CurrentFilm = 1;
    UPROPERTY(BlueprintReadOnly, Category="Film Puzzle") int32 SceneChoice = 1;
    UPROPERTY(BlueprintReadOnly, Category="Film Puzzle") int32 DirectionChoice = 0;
    UPROPERTY(BlueprintReadOnly, Category="Film Puzzle") int32 MarkChoice = 0;
    UFUNCTION(BlueprintCallable, Category="Film Puzzle") void EnterPuzzle();
    UFUNCTION(BlueprintCallable, Category="Film Puzzle") void LeavePuzzle();
    UFUNCTION(BlueprintCallable, Category="Film Puzzle") void SelectFilm(int32 Film);
    UFUNCTION(BlueprintCallable, Category="Film Puzzle") void ApplySettings();
    UFUNCTION(BlueprintCallable, Category="Film Puzzle") void Submit();
    UFUNCTION(BlueprintImplementableEvent, Category="Film Puzzle") void OnSolved();
private:
    TWeakObjectPtr<AActor> PreviousView;
    TSharedPtr<SWidget> Overlay;
    float MessageTime = 0.f;
    float FinishTime = 0.f;
    bool bWrong = false;
    bool bCompleting = false;
    FText GetSettingsText() const;
    FText GetChoicesText() const;
    FText GetMessageText() const;
};
