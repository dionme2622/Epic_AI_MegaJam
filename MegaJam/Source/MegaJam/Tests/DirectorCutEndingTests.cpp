#if WITH_DEV_AUTOMATION_TESTS
#include "HAL/IConsoleManager.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "../Stage4ShadowTheatre.h"

namespace
{
// PIE-only completion fixture for verify_campaign_ending.py. This does not open
// the ending itself: the observer verifies the real HUD transition and playback.
FAutoConsoleCommandWithWorld DirectorCutFinalClearFixtureCommand(
    TEXT("DirectorCut.Test.CompleteFinalStage"),
    TEXT("PIE test only: reproduce final Stage4 completion for ending travel verification."),
    FConsoleCommandWithWorldDelegate::CreateLambda([](UWorld* World)
    {
        if (!World || World->WorldType != EWorldType::PIE ||
            !World->GetOutermost()->GetName().Contains(TEXT("/DirectorCut/Stage/")) ||
            !World->GetOutermost()->GetName().EndsWith(TEXT("Stage4"))) return;
        for (TActorIterator<AStage4ShadowTheatre> It(World); It; ++It)
        {
            It->bRecovered = true;
            UE_LOG(LogTemp, Display, TEXT("CAMPAIGN_TEST_FINAL_CLEAR_APPLIED"));
            return;
        }
    }));
}
#endif
