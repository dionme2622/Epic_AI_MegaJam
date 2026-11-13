#include "DirectorCutMeshVariants.h"

#include "Components/StaticMeshComponent.h"
#include "DirectorCutGraphics.h"
#include "DirectorCutTest.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"

void ADirectorCutStageMeshVariants::BeginPlay()
{
    Super::BeginPlay();
    if (auto* Mode = GetWorld()->GetAuthGameMode<ADirectorCutTestMode>())
    {
        Mode->RegisterMeshVariants(MeshVariants);
    }
}

void ADirectorCutTestMode::RegisterMeshVariants(const TArray<FDirectorCutMeshVariant>& Entries)
{
    for (const FDirectorCutMeshVariant& Entry : Entries)
    {
        if (IsValid(Entry.Target) && Entry.Target->GetWorld() == GetWorld() && Entry.LowMesh && Entry.HighMesh)
        {
            MeshVariants.RemoveAll([&Entry](const FDirectorCutMeshVariant& Existing)
            {
                return Existing.Target == Entry.Target;
            });
            MeshVariants.Add(Entry);
        }
    }
    if (const auto* Graphics = GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>())
    {
        ApplyModelDetail(Graphics->IsHigh(EDirectorCutGraphicsOption::ModelDetail));
    }
}

void ADirectorCutTestMode::ApplyModelDetail(bool bHigh) const
{
    for (const FDirectorCutMeshVariant& Entry : MeshVariants)
    {
        if (!IsValid(Entry.Target) || Entry.Target->GetWorld() != GetWorld())
        {
            continue;
        }

        auto* Component = Entry.Target->GetStaticMeshComponent();
        UStaticMesh* Selected = bHigh ? Entry.HighMesh.Get() : Entry.LowMesh.Get();
        if (Selected && Component->GetStaticMesh() != Selected)
        {
            Component->SetMobility(EComponentMobility::Movable);
            Component->SetStaticMesh(Selected);
        }
    }
}
