#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/PlayerController.h"
#include "Styling/SlateBrush.h"
#include "DirectorCutLobby.generated.h"

class SWidget;
class UTexture2D;

UCLASS()
class ADirectorCutLobbyController : public APlayerController
{
    GENERATED_BODY()

public:
    ADirectorCutLobbyController();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    TObjectPtr<UTexture2D> LobbyKeyArt;

    FSlateBrush LobbyArtBrush;
    TSharedPtr<SWidget> Lobby;
    bool bStarting = false;
};

UCLASS()
class ADirectorCutLobbyMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    ADirectorCutLobbyMode();
};

