#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DirectorCutHeroLegs.generated.h"

class ADirectorCutDragon;
class USkeletalMeshComponent;

UCLASS()
class ADirectorCutHeroLegs : public AActor
{
    GENERATED_BODY()

public:
    ADirectorCutHeroLegs();
    virtual void Tick(float DeltaSeconds) override;

    bool CanEquip(const ADirectorCutDragon& Dragon) const;
    FVector GetPromptAnchor() const;

private:
    UPROPERTY(VisibleAnywhere, Category="Hero Legs")
    TObjectPtr<USkeletalMeshComponent> Legs;

    UPROPERTY(EditInstanceOnly, Category="Hero Legs", meta=(ClampMin="30", Units="cm"))
    float InteractionDistance = 130.f;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Hero Legs", meta=(AllowPrivateAccess="true"))
    bool bEquipped = false;
};
