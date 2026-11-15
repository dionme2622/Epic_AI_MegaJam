#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Sound/SoundBase.h"
#include "../DirectorCutStoryData.h"
#include "../DirectorCutVoiceLookup.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDirectorCutVoiceCoverageTest,
    "DirectorCut.Audio.GameplayVoiceCoverage",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FDirectorCutVoiceCoverageTest::RunTest(const FString& Parameters)
{
    int32 Count = 0;
    auto Check = [this, &Count](const FString& Text)
    {
        const TCHAR* Path = FindDirectorCutVoice(Text);
        if (!TestNotNull(*Text, Path)) return;
        USoundBase* Sound = LoadObject<USoundBase>(nullptr, Path);
        if (TestNotNull(Path, Sound))
        {
            TestTrue(TEXT("Imported dialogue has a finite positive duration"),
                FMath::IsFinite(Sound->GetDuration()) && Sound->GetDuration() > .1f && Sound->GetDuration() < 30.f);
            ++Count;
        }
    };
    for (const TCHAR* Map : {TEXT("L_Stage1"), TEXT("Stage2"), TEXT("Stage3_"), TEXT("Stage4")})
        for (const auto& Cue : GetDirectorCutStoryCues(FName(Map))) Check(Cue.English.ToString());
    TestNull(TEXT("Paper note must not resolve to the retired HUD voice"),
        FindDirectorCutVoice(TEXT("Storage log: The real legs were moved to the final vault.")));
    Check(TEXT("Dragon: Keep the camera rolling to the end of this take."));
    TestEqual(TEXT("Every gameplay subtitle resolves to a loaded voice asset"), Count, 11);
    return true;
}
#endif
