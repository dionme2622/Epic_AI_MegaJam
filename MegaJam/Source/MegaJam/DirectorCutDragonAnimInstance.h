#pragma once

#include "Animation/AnimInstance.h"
#include "DirectorCutDragonAnimInstance.generated.h"

class UAnimSequence;

UCLASS(Transient)
class UDirectorCutDragonAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    void SetMotion(UAnimSequence* Sequence, float Time, float BlendDuration, float RootHeightOffset,
        const TOptional<FVector>& EquippedWaist);

protected:
    virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override;
    virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy) override;
};

