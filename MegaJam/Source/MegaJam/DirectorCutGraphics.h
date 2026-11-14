#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "Subsystems/WorldSubsystem.h"
#include "Styling/SlateBrush.h"
#include "DirectorCutGraphics.generated.h"

class SWidget;
class UTexture2D;

UENUM(BlueprintType)
enum class EDirectorCutGraphicsOption : uint8
{
    ModelDetail,
    Resolution,
    Shadows
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FDirectorCutGraphicsChanged,
    EDirectorCutGraphicsOption, Option, bool, bHigh);

UCLASS()
class UDirectorCutGraphicsSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()

public:


    UFUNCTION(BlueprintPure, Category="Director Cut|Graphics")
    bool IsHigh(EDirectorCutGraphicsOption Option) const;

    UFUNCTION(BlueprintCallable, Category="Director Cut|Graphics")
    void SetHigh(EDirectorCutGraphicsOption Option, bool bHigh);

    bool CanSet(EDirectorCutGraphicsOption Option) const;

    UPROPERTY(BlueprintAssignable, Category="Director Cut|Graphics")
    FDirectorCutGraphicsChanged OnGraphicsChanged;

private:
    void Apply(EDirectorCutGraphicsOption Option) const;
    virtual void OnWorldBeginPlay(UWorld& InWorld) override;
    virtual void Deinitialize() override;

    bool bModelHigh = false;
    bool bResolutionHigh = true;
    bool bShadowsHigh = true;
};

UCLASS()
class ADirectorCutPlayerController : public APlayerController
{
    GENERATED_BODY()

public:
    ADirectorCutPlayerController();
    bool IsGraphicsMenuOpen() const { return bMenuOpen; }

protected:
    virtual void SetupInputComponent() override;
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    void SetMenuOpen(bool bOpen);
    void ToggleMenu();
    void SelectLowModelDetail();
    void SelectHighModelDetail();
    void ToggleShadows();

    bool bMenuOpen = false;
    bool bWorkshop = false;
    TSharedPtr<SWidget> SettingsOverlay;
    FSlateBrush StoneBrush;

    UPROPERTY(EditDefaultsOnly, Category="Director Cut|Settings")
    TObjectPtr<UTexture2D> SettingsPanelTexture;
};



