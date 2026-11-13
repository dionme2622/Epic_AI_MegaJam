#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DirectorCutMeshVariants.generated.h"

class AStaticMeshActor;
class UStaticMesh;

USTRUCT(BlueprintType)
struct FDirectorCutMeshVariant
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Model Detail")
    TObjectPtr<AStaticMeshActor> Target;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Model Detail")
    TObjectPtr<UStaticMesh> LowMesh;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Model Detail")
    TObjectPtr<UStaticMesh> HighMesh;
};

UCLASS(Blueprintable, meta=(DisplayName="Director Cut Stage Mesh Variants"))
class ADirectorCutStageMeshVariants : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Model Detail")
    TArray<FDirectorCutMeshVariant> MeshVariants;

protected:
    virtual void BeginPlay() override;
};
