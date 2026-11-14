#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DirectorCutWheelchair.generated.h"

class ADirectorCutDragon;

namespace DirectorCutCart
{
    constexpr float WheelRadius = 17.5f;
    inline const FVector WheelCenters[] = {
        FVector(-37.62f, -35.64f, WheelRadius),
        FVector(-37.62f, 35.64f, WheelRadius),
        FVector(36.63f, -34.32f, WheelRadius),
        FVector(36.63f, 34.32f, WheelRadius),
    };
}

UCLASS()
class ADirectorCutWheelchair : public AActor
{
    GENERATED_BODY()

public:
    ADirectorCutWheelchair();
    virtual void Tick(float DeltaSeconds) override;

    bool CanEquip(const ADirectorCutDragon& Dragon) const;
    FVector GetPromptAnchor() const;

private:
    UPROPERTY(EditInstanceOnly, Category="Wheelchair", meta=(ClampMin="30", Units="cm"))
    float InteractionDistance = 145.f;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Wheelchair", meta=(AllowPrivateAccess="true"))
    bool bEquipped = false;
};
