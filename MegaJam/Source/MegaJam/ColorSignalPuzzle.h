#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ColorSignalPuzzle.generated.h"

class UCameraComponent;
class UStaticMeshComponent;
class UTextRenderComponent;
class AStage2ShadowDoor;
class SWidget;

UCLASS(Blueprintable)
class MEGAJAM_API AColorSignalPuzzle : public AActor
{
    GENERATED_BODY()
public:
    AColorSignalPuzzle();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void Tick(float DeltaSeconds) override;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Color Signal") TObjectPtr<USceneComponent> Root;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Color Signal") TObjectPtr<UStaticMeshComponent> Frame;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Color Signal") TObjectPtr<UStaticMeshComponent> SignalPanel;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Color Signal") TObjectPtr<UStaticMeshComponent> RecordBackground;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Color Signal") TObjectPtr<UStaticMeshComponent> Dial1;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Color Signal") TObjectPtr<UStaticMeshComponent> Dial2;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Color Signal") TObjectPtr<UStaticMeshComponent> Dial3;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Color Signal") TObjectPtr<UStaticMeshComponent> Dial4;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Color Signal") TObjectPtr<UTextRenderComponent> RestoredRecord;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Color Signal") TObjectPtr<UCameraComponent> PuzzleCamera;
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Color Signal") TObjectPtr<AStage2ShadowDoor> ExitDoor;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Color Signal") float InteractDistance = 250.f;
    UPROPERTY(BlueprintReadOnly, Category="Color Signal") bool bActive = false;
    UPROPERTY(BlueprintReadOnly, Category="Color Signal") bool bSolved = false;
    UPROPERTY(BlueprintReadOnly, Category="Color Signal") int32 FilterMode = 0;
    UPROPERTY(BlueprintReadOnly, Category="Color Signal") TArray<int32> DialValues;
    UFUNCTION(BlueprintCallable, Category="Color Signal") void EnterPuzzle();
    UFUNCTION(BlueprintCallable, Category="Color Signal") void LeavePuzzle();
    UFUNCTION(BlueprintCallable, Category="Color Signal") void SetFilter(int32 Mode);
    UFUNCTION(BlueprintCallable, Category="Color Signal") void RotateDial(int32 Index);
    UFUNCTION(BlueprintCallable, Category="Color Signal") void ResetDials();
    UFUNCTION(BlueprintPure, Category="Color Signal") bool AreDialsAligned() const;
    UFUNCTION(BlueprintCallable, Category="Color Signal") void Submit();
    UFUNCTION(BlueprintImplementableEvent, Category="Color Signal") void OnSolved();
private:
    TWeakObjectPtr<AActor> PreviousView;
    TSharedPtr<SWidget> Overlay;
    bool bCompleting = false;
    bool bWrong = false;
    float FinishTime = 0.f;
    float MessageTime = 0.f;
    void UpdateDialVisuals();
    FText GetHeaderText() const;
    FText GetMessageText() const;
};
