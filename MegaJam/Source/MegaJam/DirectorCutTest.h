#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "GameFramework/GameModeBase.h"
#include "DirectorCutMeshVariants.h"
#include "DirectorCutTest.generated.h"

class UAnimSequence;
class UCameraComponent;
class UPoseableMeshComponent;
class UStaticMeshComponent;
class USkeletalMesh;

UCLASS()
class ADirectorCutDragon : public ACharacter
{
    GENERATED_BODY()

public:
    ADirectorCutDragon();
    virtual void Tick(float DeltaSeconds) override;
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual void Landed(const FHitResult& Hit) override;
    virtual void CheckJumpInput(float DeltaTime) override;

    bool IsRidingCart() const { return bRideCart; }
    bool CanMountCart() const;
    bool MountCart();
    bool HasHeroLegs() const { return bHeroLegsEquipped; }
    bool EquipHeroLegs();
    void RestoreOriginalLegs();

    void SetPuzzleRespawnPoint(const FVector& Location) { SpawnPoint = Location; }
    void SetTheatreCameraFraming(float Amount, float FocusX)
    {
        TheatreCameraTarget = Amount;
        TheatreCameraFocusX = FocusX;
    }

protected:
    virtual void BeginPlay() override;
    virtual bool CanJumpInternal_Implementation() const override;

private:
    void Move(float Amount);
    void StartJump();
    void PlayMotion(UAnimSequence* Motion, float Time, float BlendDuration, float RootHeightOffset = 0.f);
    void UpdateAirPose(float DeltaSeconds);
    void UpdateSideCamera(float FollowX);
    void UpdateCart(float DeltaSeconds);
    void UpdateHeroLegsPose();

    UPROPERTY(EditInstanceOnly, Category="Ride Cart")
    bool bRideCart = false;

    UPROPERTY(EditInstanceOnly, Category="Ride Cart")
    bool bAwaitWheelchair = false;

    UPROPERTY(EditInstanceOnly, Category="Ride Cart")
    bool bContinueCartFromCastle = false;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Hero Legs", meta=(AllowPrivateAccess="true"))
    bool bHeroLegsEquipped = false;

    UPROPERTY(VisibleAnywhere, Category="Hero Legs")
    TObjectPtr<UPoseableMeshComponent> HeroLegsMesh;

    UPROPERTY()
    TObjectPtr<USkeletalMesh> StandingDragonMesh;

    UPROPERTY()
    TObjectPtr<USkeletalMesh> HeroUpperMesh;

    UPROPERTY()
    TObjectPtr<UAnimSequence> HeroRunMotion;

    UPROPERTY()
    TObjectPtr<UAnimSequence> HeroLandMotion;

    UPROPERTY()
    TObjectPtr<UAnimSequence> StandingMotions[4];

    UPROPERTY(VisibleAnywhere, Category="Ride Cart")
    TObjectPtr<UStaticMeshComponent> CartBody;

    UPROPERTY()
    TArray<TObjectPtr<UStaticMeshComponent>> CartWheels;

    UPROPERTY(EditInstanceOnly, Category="Ride Cart")
    TObjectPtr<USkeletalMesh> CartRiderMesh;

    UPROPERTY(EditInstanceOnly, Category="Ride Cart")
    TObjectPtr<UAnimSequence> CartMotion;

    UPROPERTY(EditInstanceOnly, Category="Ride Cart")
    TObjectPtr<UAnimSequence> CartIdleMotion;

    UPROPERTY(EditInstanceOnly, Category="Ride Cart")
    TObjectPtr<UAnimSequence> CartDriveMotion;

    UPROPERTY()
    TObjectPtr<UAnimSequence> UnmountedCartIdleMotion;

    UPROPERTY()
    TObjectPtr<UAnimSequence> UnmountedCartJumpMotion;

    float CartMotionTime = 0.f;
    bool bCartDriving = false;
    float WheelAngle = 0.f;
    FVector LastCartLocation;
    bool bCartWasGrounded = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Side Camera", meta=(AllowPrivateAccess="true"))
    TObjectPtr<UCameraComponent> SideCamera;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Side Camera", meta=(AllowPrivateAccess="true", ClampMin="100", Units="cm"))
    float CameraDistance = 810.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Side Camera", meta=(AllowPrivateAccess="true", Units="cm"))
    float CameraElevation = 266.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Side Camera", meta=(AllowPrivateAccess="true", ClampMin="-80", ClampMax="0", Units="deg"))
    float CameraPitch = -17.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Side Camera", meta=(AllowPrivateAccess="true", ClampMin="10", ClampMax="120", Units="deg"))
    float CameraFieldOfView = 49.f;
    UPROPERTY()
    TObjectPtr<UAnimSequence> IdleMotion;
    UPROPERTY()
    TObjectPtr<UAnimSequence> RunMotion;
    UPROPERTY()
    TObjectPtr<UAnimSequence> JumpMotion;
    UPROPERTY()
    TObjectPtr<UAnimSequence> LandMotion;
    UPROPERTY()
    TObjectPtr<UAnimSequence> CurrentMotion;

    FVector SpawnPoint;
    float CameraZ = 0.f;
    double BufferedJumpUntil = -1.0;
    float LandingElapsed = 1.f;
    float GroundMotionTime = 0.f;
    float MoveInput = 0.f;
    float AirPhase = 0.f;
    float TheatreCameraTarget = 0.f;
    float TheatreCameraBlend = 0.f;
    float TheatreCameraFocusX = 0.f;
};

UCLASS()
class ADirectorCutTestMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    ADirectorCutTestMode();
    virtual APawn* SpawnDefaultPawnAtTransform_Implementation(AController* NewPlayer, const FTransform& SpawnTransform) override;

    UFUNCTION(BlueprintCallable, Category="Director Cut|Model Detail")
    void RegisterMeshVariants(const TArray<FDirectorCutMeshVariant>& Entries);

    void ApplyModelDetail(bool bHigh) const;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Director Cut|Model Detail")
    TArray<FDirectorCutMeshVariant> MeshVariants;
};










