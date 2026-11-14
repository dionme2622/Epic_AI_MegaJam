#include "DirectorCutWheelchair.h"

#include "Components/StaticMeshComponent.h"
#include "DirectorCutTest.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"

ADirectorCutWheelchair::ADirectorCutWheelchair()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickGroup = TG_PostPhysics;

    auto* Body = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Body"));
    SetRootComponent(Body);
    Body->SetCollisionProfileName(TEXT("NoCollision"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> BodyMesh(
        TEXT("/Game/DirectorCut/Stage1/RideCart/SM_Dragon_Ride_Cart.SM_Dragon_Ride_Cart"));
    Body->SetStaticMesh(BodyMesh.Object);

    static ConstructorHelpers::FObjectFinder<UStaticMesh> WheelMeshes[] = {
        {TEXT("/Game/DirectorCut/Stage1/RideCart/SM_Dragon_Cart_Wheel_1.SM_Dragon_Cart_Wheel_1")},
        {TEXT("/Game/DirectorCut/Stage1/RideCart/SM_Dragon_Cart_Wheel_2.SM_Dragon_Cart_Wheel_2")},
        {TEXT("/Game/DirectorCut/Stage1/RideCart/SM_Dragon_Cart_Wheel_3.SM_Dragon_Cart_Wheel_3")},
        {TEXT("/Game/DirectorCut/Stage1/RideCart/SM_Dragon_Cart_Wheel_4.SM_Dragon_Cart_Wheel_4")},
    };
    static_assert(UE_ARRAY_COUNT(WheelMeshes) == UE_ARRAY_COUNT(DirectorCutCart::WheelCenters));

    for (int32 Index = 0; Index < UE_ARRAY_COUNT(WheelMeshes); ++Index)
    {
        auto* Wheel = CreateDefaultSubobject<UStaticMeshComponent>(*FString::Printf(TEXT("Wheel%d"), Index + 1));
        Wheel->SetupAttachment(Body);
        Wheel->SetRelativeLocation(DirectorCutCart::WheelCenters[Index]);
        Wheel->SetCollisionProfileName(TEXT("NoCollision"));
        Wheel->SetStaticMesh(WheelMeshes[Index].Object);
    }
}

bool ADirectorCutWheelchair::CanEquip(const ADirectorCutDragon& Dragon) const
{
    const auto* Controller = Cast<APlayerController>(Dragon.GetController());
    const FVector Offset = Dragon.GetActorLocation() - GetActorLocation();
    return !bEquipped && Dragon.CanMountCart() && Controller && !Controller->IsMoveInputIgnored()
        && Offset.SizeSquared2D() <= FMath::Square(InteractionDistance) && FMath::Abs(Offset.Z) <= 120.f;
}

FVector ADirectorCutWheelchair::GetPromptAnchor() const
{
    return GetActorLocation() + FVector(0.f, 0.f, 100.f);
}

void ADirectorCutWheelchair::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    auto* Controller = UGameplayStatics::GetPlayerController(this, 0);
    auto* Dragon = Controller ? Cast<ADirectorCutDragon>(Controller->GetPawn()) : nullptr;
    if (Dragon && Controller->WasInputKeyJustPressed(EKeys::E) && CanEquip(*Dragon) && Dragon->MountCart())
    {
        bEquipped = true;
        SetActorHiddenInGame(true);
        SetActorTickEnabled(false);
    }
}
