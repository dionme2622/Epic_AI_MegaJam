#pragma once
#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "DirectorCutPrologueSubtitles.generated.h"
class SWidget;
UCLASS()
class UDirectorCutPrologueSubtitles : public UTickableWorldSubsystem
{
    GENERATED_BODY()
public:
    virtual void OnWorldBeginPlay(UWorld& World) override;
    virtual void Tick(float DeltaTime) override;
    virtual void Deinitialize() override;
    virtual TStatId GetStatId() const override;
private:
    TArray<TWeakObjectPtr<AActor>> Captions;
    TSharedPtr<SWidget> Overlay;
    int32 ActiveCaption = INDEX_NONE;
};
