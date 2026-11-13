#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "GameFramework/GameModeBase.h"
#include "DirectorCutTest.generated.h"

class UAnimSequence;
class UCameraComponent;

UCLASS()
class ADirectorCutDragon : public ACharacter
{
    GENERATED_BODY()

public:
    ADirectorCutDragon();
    virtual void Tick(float DeltaSeconds) override;
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual void Landed(const FHitResult& Hit) override;

protected:
    virtual void BeginPlay() override;

private:
    void Move(float Amount);
    void StartJump();
    void PlayMotion(UAnimSequence* Motion, bool bLoop);
    void UpdateAirPose(float DeltaSeconds);

    UPROPERTY()
    TObjectPtr<UCameraComponent> SideCamera;
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
    float LandUntil = 0.f;
    float AirPhase = 0.f;
};

UCLASS()
class ADirectorCutTestMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    ADirectorCutTestMode();
};

