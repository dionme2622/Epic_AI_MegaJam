#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameFramework/GameModeBase.h"
#include "Styling/SlateBrush.h"
#include "DirectorCutEnding.generated.h"

class ALevelSequenceActor;
class APlayerController;
class SWidget;
class UTexture2D;
class UAnimSequence;

UCLASS()
class ADirectorCutEndingMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    ADirectorCutEndingMode();
};

UENUM(BlueprintType)
enum class EDirectorCutEndingState : uint8
{
    Dialogue,
    Choosing,
    Revealing,
    ReadyForContinuation,
    OriginalLegsScene,
    CartScene,
    HeroLegsScene
};

/** Runtime bridge between the editable ending sequences and the player's choice. */
UCLASS(Blueprintable)
class ADirectorCutEnding : public AActor
{
    GENERATED_BODY()

public:
    ADirectorCutEnding();

    /** Rebuild the deliberately unfinished, stiff-legged walk from the existing dragon rig. */
    UFUNCTION(BlueprintCallable, Category="Director Cut|Ending|Editor")
    static UAnimSequence* BuildAwkwardWalkAnimation();

    UFUNCTION(BlueprintCallable, Category="Director Cut|Ending|Editor")
    static UAnimSequence* BuildHeroLegsScurryAnimation();

    /** 0 = original dragon, 1 = cart, 2 = hero's legs. Only accepted at the choice. */
    UFUNCTION(BlueprintCallable, Category="Director Cut|Ending")
    void ChooseLowerBody(int32 OptionIndex);

    UFUNCTION(BlueprintPure, Category="Director Cut|Ending")
    EDirectorCutEndingState GetEndingState() const { return EndingState; }

    UFUNCTION(BlueprintPure, Category="Director Cut|Ending")
    int32 GetSelectedLowerBody() const { return SelectedLowerBody; }

    /** Hook for the next scene. The return shot and selected model remain on screen. */
    UFUNCTION(BlueprintImplementableEvent, Category="Director Cut|Ending")
    void OnReadyForContinuation(int32 OptionIndex);

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Sequences")
    TObjectPtr<ALevelSequenceActor> IntroSequenceActor;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Sequences")
    TObjectPtr<ALevelSequenceActor> RevealSequenceActor;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Sequences")
    TObjectPtr<ALevelSequenceActor> OriginalLegsSequenceActor;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Sequences")
    TObjectPtr<ALevelSequenceActor> CartSequenceActor;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Sequences")
    TObjectPtr<ALevelSequenceActor> HeroLegsSequenceActor;

    /** Ramp scenery is shown only for the runaway-cart branch. */
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Sequences")
    TArray<TObjectPtr<AActor>> CartSceneActors;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Sequences")
    TObjectPtr<AActor> EndingCamera;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Models")
    TObjectPtr<AActor> FullDragon;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Models")
    TObjectPtr<AActor> UpperDragon;

    /** Optional separate original lower mesh, used when FullDragon is not assigned. */
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Models")
    TObjectPtr<AActor> DragonLowerBody;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Models")
    TObjectPtr<AActor> CartBody;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Models")
    TArray<TObjectPtr<AActor>> CartAccessories;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Models")
    TObjectPtr<AActor> HeroLegs;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Models")
    bool bUseVariantUpperTransforms = false;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Models", meta=(EditCondition="bUseVariantUpperTransforms"))
    FTransform CartUpperTransform;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Models", meta=(EditCondition="bUseVariantUpperTransforms"))
    FTransform HeroUpperTransform;

    /** Rendered photographs of the existing models, ordered original / cart / hero. */
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Ending|Choice")
    TArray<TObjectPtr<UTexture2D>> OptionImages;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Ending|Subtitles")
    FText HeroSubtitle;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Ending|Subtitles")
    FText DragonSubtitle;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Ending|Subtitles", meta=(ClampMin="0"))
    float HeroSubtitleStart = .6f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Ending|Subtitles", meta=(ClampMin="0"))
    float HeroSubtitleEnd = 5.2f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Ending|Subtitles", meta=(ClampMin="0"))
    float DragonSubtitleStart = 5.4f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Ending|Subtitles", meta=(ClampMin="0"))
    float DragonSubtitleEnd = 9.7f;

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UFUNCTION()
    void ShowChoice();

    UFUNCTION()
    void FinishReveal();

    UFUNCTION()
    void FinishBranchScene();

    void CreateOverlay();
    void ApplyLowerBody(int32 OptionIndex);
    void SetChoiceInput(bool bChoosing);
    FText GetCurrentSubtitle() const;
    FText GetCurrentEnglishSubtitle() const;
    FText GetCurrentSpeaker() const;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Ending|State", meta=(AllowPrivateAccess="true"))
    EDirectorCutEndingState EndingState = EDirectorCutEndingState::Dialogue;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Ending|State", meta=(AllowPrivateAccess="true"))
    int32 SelectedLowerBody = INDEX_NONE;

    TWeakObjectPtr<APlayerController> LocalController;
    TWeakObjectPtr<AActor> PreviousViewTarget;
    bool bPreviousMouseCursor = false;
    bool bBlockedPlayerInput = false;
    int32 FocusedOption = 0;
    TSharedPtr<SWidget> Overlay;
    TSharedPtr<SWidget> ChoicePanel;
    TArray<FSlateBrush> ImageBrushes;
    FTransform InitialUpperTransform;
};
