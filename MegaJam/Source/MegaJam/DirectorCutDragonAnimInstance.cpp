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
        TOptional<FVector> EquippedWaist;
        int32 WaistBoneIndex = INDEX_NONE;
        TArray<FTransform> PreviousPose;

        bool Evaluate(FPoseContext& Output) override
        {
            if (!Sequence)
            {
                return false;
            }

            FAnimationPoseData Data(Output);
            Sequence->GetAnimationPose(Data, FAnimExtractContext(static_cast<double>(Time), false));

            const FCompactPoseBoneIndex RootIndex(0);
            FTransform& Root = Output.Pose[RootIndex];
            Root.AddToTranslation(FVector(0, 0, RootHeightOffset));
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
            if (EquippedWaist.IsSet())
            {
                // The capsule drives the jump arc. Use the upright bind root for every
                // costume clip and keep the cut edge on the armour, including during blends.
                Root = Output.Pose.GetRefPose(RootIndex);
                const auto WaistBone = Output.Pose.GetBoneContainer().MakeCompactPoseIndex(FMeshPoseBoneIndex(WaistBoneIndex));
                if (WaistBone.GetInt() != INDEX_NONE)
                {
                    FTransform Reference = Output.Pose.GetRefPose(WaistBone);
                    FTransform Animated = Output.Pose[WaistBone];
                    for (auto Parent = Output.Pose.GetParentBoneIndex(WaistBone);
                        Parent.GetInt() != INDEX_NONE && Parent != RootIndex;
                        Parent = Output.Pose.GetParentBoneIndex(Parent))
                    {
                        Reference *= Output.Pose.GetRefPose(Parent);
                        Animated *= Output.Pose[Parent];
                    }
                    Reference *= Root;
                    Animated *= Root;
                    const FVector WaistInBone = Reference.InverseTransformPosition(EquippedWaist.GetValue());
                    Root.AddToTranslation(EquippedWaist.GetValue() - Animated.TransformPosition(WaistInBone));
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

void UDirectorCutDragonAnimInstance::SetMotion(UAnimSequence* Sequence, float Time, float BlendDuration, float RootHeightOffset,
    const TOptional<FVector>& EquippedWaist)
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
    Proxy.EquippedWaist = EquippedWaist;
    Proxy.WaistBoneIndex = EquippedWaist.IsSet() ? GetSkelMeshComponent()->GetBoneIndex(TEXT("spine")) : INDEX_NONE;
}


