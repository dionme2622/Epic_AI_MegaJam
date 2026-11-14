#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DirectorCutWallNote.generated.h"

UENUM(BlueprintType)
enum class EDirectorCutWallNote : uint8
{
    Wheel,
    Lens,
    TwoTakes,
    Projection,
    VaultLighting,
    ShadowRetake,
    ShadowFerry,
    UpperSwitch
};

UCLASS()
class ADirectorCutWallNote : public AActor
{
    GENERATED_BODY()

public:
    ADirectorCutWallNote();

    bool IsInReach(const FVector& PlayerPosition) const;
    FVector GetPromptAnchor() const;
    void GetText(FText& Korean, FText& English) const;

private:
    UPROPERTY(EditInstanceOnly, Category="Wall Note")
    EDirectorCutWallNote Note = EDirectorCutWallNote::Wheel;

    UPROPERTY(EditInstanceOnly, Category="Wall Note", meta=(ClampMin="30", Units="cm"))
    float InteractionDistance = 105.f;
};
