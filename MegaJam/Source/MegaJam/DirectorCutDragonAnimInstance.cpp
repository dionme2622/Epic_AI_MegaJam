#include "DirectorCutDragonAnimInstance.h"

#include "Animation/AnimationPoseData.h"
#include "Animation/AnimInstanceProxy.h"
#include "Animation/AnimNodeBase.h"
#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"

namespace
{
    struct FDragonAnimProxy final : FAnimInstanceProxy
    {
        explicit FDragonAnimProxy(UAnimInstance* Instance)
            : FAnimInstanceProxy(Instance)
        {
        }

        UAnimSequence* Sequence = nullptr;
        float Time = 0.f;
        float BlendWeight = 1.f;
        float RootHeightOffset = 0.f;
        TArray<FTransform> PreviousPose;

        bool Evaluate(FPoseContext& Output) override
        {
            if (!Sequence)
            {
                return false;
            }

            FAnimationPoseData Data(Output);
            Sequence->GetAnimationPose(Data, FAnimExtractContext(static_cast<double>(Time), false));

            Output.Pose[FCompactPoseBoneIndex(0)].AddToTranslation(FVector(0, 0, RootHeightOffset));
            if (BlendWeight < 1.f)
            {
                for (const FCompactPoseBoneIndex Bone : Output.Pose.ForEachBoneIndex())
                {
                    const int32 MeshBone = Output.Pose.GetBoneContainer().MakeMeshPoseIndex(Bone).GetInt();
                    if (PreviousPose.IsValidIndex(MeshBone))
                    {
                        FTransform Blended;
                        Blended.Blend(PreviousPose[MeshBone], Output.Pose[Bone], BlendWeight);
                        Output.Pose[Bone] = Blended;
                    }
                }
            }
            return true;
        }
    };
}

FAnimInstanceProxy* UDirectorCutDragonAnimInstance::CreateAnimInstanceProxy()
{
    return new FDragonAnimProxy(this);
}

void UDirectorCutDragonAnimInstance::DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy)
{
    delete Proxy;
}

void UDirectorCutDragonAnimInstance::SetMotion(UAnimSequence* Sequence, float Time, float BlendDuration, float RootHeightOffset)
{
    auto& Proxy = GetProxyOnGameThread<FDragonAnimProxy>();
    if (Sequence != Proxy.Sequence)
    {
        Proxy.PreviousPose = Proxy.Sequence && BlendDuration > 0.f
            ? GetSkelMeshComponent()->GetBoneSpaceTransforms()
            : TArray<FTransform>();
        Proxy.BlendWeight = Proxy.PreviousPose.IsEmpty() ? 1.f : 0.f;
        Proxy.Sequence = Sequence;
    }
    else if (BlendDuration > 0.f)
    {
        Proxy.BlendWeight = FMath::Min(1.f, Proxy.BlendWeight + GetWorld()->GetDeltaSeconds() / BlendDuration);
    }
    Proxy.Time = Time;
    Proxy.RootHeightOffset = RootHeightOffset;
}


