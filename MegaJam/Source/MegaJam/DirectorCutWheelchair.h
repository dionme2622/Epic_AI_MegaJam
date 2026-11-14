#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "DirectorCutWheelchair.generated.h"

class ADirectorCutDragon;

UCLASS()
class UDirectorCutWheelchairTravel : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    void BeginCastle() { CastleMounted = false; }
    void RecordMount() { CastleMounted = true; }
    bool EnterWorkshop(bool bStartMounted)
    {
        const bool bMounted = CastleMounted.Get(bStartMounted);
        CastleMounted.Reset();
        return bMounted;
    }
    void StartWorkshop() { bHeroLegsAcquired = false; }
    void RecordHeroLegs() { bHeroLegsAcquired = true; }
    bool HasHeroLegs(bool bDefault) const { return bHeroLegsAcquired.Get(bDefault); }

private:
    TOptional<bool> CastleMounted;
    TOptional<bool> bHeroLegsAcquired;
};

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
