#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Stage4ShadowStandIn.generated.h"

class ADirectorCutDragon;
class UMaterialInterface;
class UPoseableMeshComponent;
class UStaticMeshComponent;

UCLASS()
class MEGAJAM_API AStage4ShadowStandIn : public AActor
{
    GENERATED_BODY()

public:
    AStage4ShadowStandIn();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    bool OwnsRecovery(double WorldX) const;

    UPROPERTY(EditInstanceOnly, Category="Stand-In")
    TObjectPtr<UStaticMeshComponent> Ferry;
    UPROPERTY(EditInstanceOnly, Category="Stand-In")
    TObjectPtr<UStaticMeshComponent> FerryArt;
    UPROPERTY(EditInstanceOnly, Category="Stand-In")
    TObjectPtr<UStaticMeshComponent> Bridge;
    UPROPERTY(EditInstanceOnly, Category="Stand-In")
    TObjectPtr<UStaticMeshComponent> BridgeArt;
    UPROPERTY(EditInstanceOnly, Category="Stand-In")
    TArray<TObjectPtr<UStaticMeshComponent>> SwitchLamps;
    UPROPERTY(EditInstanceOnly, Category="Stand-In")
    TObjectPtr<UMaterialInterface> ShadowMaterial;
    UPROPERTY(EditInstanceOnly, Category="Stand-In")
    TObjectPtr<UMaterialInterface> LampOnMaterial;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Stand-In")
    bool bCallSwitch = false;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Stand-In")
    bool bLowSwitch = false;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Stand-In")
    bool bHighSwitch = false;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Stand-In")
    bool bRaisedBridge = false;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Stand-In")
    int32 Checkpoint = 0;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Stand-In")
    bool bReachedExhibit = false;

private:
    FVector Project(const FVector& Point, const FVector& Light) const;
    void UpdateShadow(ADirectorCutDragon& Dragon, const FVector& Light, bool bVisible);
    void SetCheckpoint(ADirectorCutDragon& Dragon, int32 Index);
    void Respawn(ADirectorCutDragon& Dragon);
    void MoveMechanism(UStaticMeshComponent* Collider, UStaticMeshComponent* Art, const FVector& Delta);

    UPROPERTY(Transient)
    TObjectPtr<UPoseableMeshComponent> Shadow;
    UPROPERTY(Transient)
    TArray<TObjectPtr<UMaterialInterface>> LampOffMaterials;

    float FerryX = 816.f;
    float BridgeZ = -176.f;
    float SwitchSoundCooldown = 0.f;
    bool bFerryReturning = false;
    bool bFerryCarrying = false;
    bool bLastShadows = true;
};
