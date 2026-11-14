// Fill out your copyright notice in the Description page of Project Settings.


#include "Dragon.h"
#include "Components/InputComponent.h"
#include "Components/SkeletalMeshComponent.h"

// Sets default values
ADragon::ADragon()
{
 	// Set this character to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;


}

// Called when the game starts or when spawned
void ADragon::BeginPlay()
{
	Super::BeginPlay();
	
}

// Called every frame
void ADragon::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

}

// Called to bind functionality to input
void ADragon::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);
	PlayerInputComponent->BindAxis(TEXT("DragonMove"), this, &ADragon::MoveRight);

}

void ADragon::MoveRight(float Value)
{
	if (!FMath::IsNearlyZero(Value))
	{
		// The side-view camera looks along -Y, so X is horizontal on screen.
		AddMovementInput(FVector::XAxisVector, FMath::Clamp(Value, -1.0f, 1.0f));
		GetMesh()->SetRelativeRotation(FRotator(0.0f, Value < 0.0f ? 180.0f : 0.0f, 0.0f));
	}

}

