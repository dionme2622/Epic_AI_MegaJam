#include "DirectorCutHeroLegs.h"

#include "Components/SceneComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "DirectorCutTest.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

ADirectorCutHeroLegs::ADirectorCutHeroLegs()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickGroup = TG_PostPhysics;

    auto* DisplayRoot = CreateDefaultSubobject<USceneComponent>(TEXT("DisplayRoot"));
    SetRootComponent(DisplayRoot);

    static ConstructorHelpers::FObjectFinder<UStaticMesh> DisplayCube(
        TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> StoneMaterial(
        TEXT("/Game/Stage4Integrated/Theatre/M03_Slate.M03_Slate"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> BrassMaterial(
        TEXT("/Game/Stage4Integrated/Theatre/M06_Gold.M06_Gold"));
    auto* Stand = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Stand"));
    Stand->SetupAttachment(DisplayRoot);
    Stand->SetCollisionProfileName(TEXT("NoCollision"));
    Stand->SetStaticMesh(DisplayCube.Object);
    Stand->SetMaterial(0, StoneMaterial.Object);
    Stand->SetRelativeLocation(FVector(0.f, 0.f, 9.f));
    Stand->SetRelativeScale3D(FVector(.89f, .68f, .18f));

    auto* Trim = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("StandTrim"));
    Trim->SetupAttachment(DisplayRoot);
    Trim->SetCollisionProfileName(TEXT("NoCollision"));
    Trim->SetStaticMesh(DisplayCube.Object);
    Trim->SetMaterial(0, BrassMaterial.Object);
    Trim->SetRelativeLocation(FVector(0.f, 0.f, 19.f));
    Trim->SetRelativeScale3D(FVector(.93f, .72f, .04f));

    Legs = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("HeroLegs"));
    Legs->SetupAttachment(DisplayRoot);
    Legs->SetCollisionProfileName(TEXT("NoCollision"));
    static ConstructorHelpers::FObjectFinder<USkeletalMesh> HeroLegsMesh(
        TEXT("/Game/DirectorCut/Dragon/KnightLegs/SK_Knight_LowerBody.SK_Knight_LowerBody"));
    if (USkeletalMesh* Mesh = HeroLegsMesh.Object)
    {
        Legs->SetSkeletalMesh(Mesh);
        Legs->SetForceRefPose(true);
        const FBoxSphereBounds Bounds = Mesh->GetBounds();
        const double Scale = 88. / FMath::Max(1., Bounds.BoxExtent.Z * 2.);
        const FRotator Rotation(0.f, 65.f, 0.f);
        Legs->SetRelativeScale3D(FVector(Scale));
        Legs->SetRelativeRotation(Rotation);
        Legs->SetRelativeLocation(FVector(0.f, 0.f, 21.f + Bounds.BoxExtent.Z * Scale)
            - Rotation.RotateVector(Bounds.Origin * Scale));
    }
}

bool ADirectorCutHeroLegs::CanEquip(const ADirectorCutDragon& Dragon) const
{
    const auto* Controller = Cast<APlayerController>(Dragon.GetController());
    const FVector Offset = Dragon.GetActorLocation() - GetActorLocation();
    return !bEquipped && !Dragon.HasHeroLegs() && Controller && !Controller->IsMoveInputIgnored()
        && Dragon.GetCharacterMovement()->IsMovingOnGround()
        && Offset.SizeSquared2D() <= FMath::Square(InteractionDistance) && FMath::Abs(Offset.Z) <= 150.f;
}

FVector ADirectorCutHeroLegs::GetPromptAnchor() const
{
    return GetActorLocation() + FVector(0.f, 0.f, 132.f);
}

void ADirectorCutHeroLegs::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    auto* Controller = UGameplayStatics::GetPlayerController(this, 0);
    auto* Dragon = Controller ? Cast<ADirectorCutDragon>(Controller->GetPawn()) : nullptr;
    if (Dragon && Controller->WasInputKeyJustPressed(EKeys::E) && CanEquip(*Dragon) && Dragon->EquipHeroLegs())
    {
        bEquipped = true;
        Legs->SetVisibility(false);
        SetActorTickEnabled(false);
    }
}
