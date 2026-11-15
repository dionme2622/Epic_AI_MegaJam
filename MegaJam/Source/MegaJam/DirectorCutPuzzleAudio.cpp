#include "DirectorCutPuzzleAudio.h"

#include "Components/AudioComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"

DEFINE_LOG_CATEGORY_STATIC(LogDirectorCutPuzzleAudio, Log, All);

namespace
{
    constexpr const TCHAR* PuzzleCueNames[] = {
        TEXT("ControlTick"), TEXT("ChairEquip"), TEXT("WheelLatch"), TEXT("LiftStart"), TEXT("LiftLock"), TEXT("HeroLegs"),
        TEXT("FocusMove"), TEXT("FocusLock"), TEXT("TakeRecord"), TEXT("TakeReplay"), TEXT("TakeLock"),
        TEXT("FilmNotch"), TEXT("FilmLock"), TEXT("ArchiveCrate"), TEXT("RgbDial"), TEXT("RgbLock"), TEXT("LampAim"),
        TEXT("RetakeLock"), TEXT("StandSwitch"), TEXT("FerryMotor"), TEXT("BridgeLock"),
        TEXT("CrawlStep"), TEXT("ChairRoll"), TEXT("HeroStep"), TEXT("DragonStep")
    };
    static_assert(UE_ARRAY_COUNT(PuzzleCueNames) == static_cast<uint8>(DirectorCutPuzzleAudio::ECue::Count));

    USoundBase* FindPuzzleSound(uint8 Index)
    {
        check(Index < UE_ARRAY_COUNT(PuzzleCueNames));

        static TWeakObjectPtr<USoundBase> CachedSounds[UE_ARRAY_COUNT(PuzzleCueNames)];
        USoundBase* Sound = CachedSounds[Index].Get();
        if (!Sound)
        {
            const FString Path = FString::Printf(TEXT("/Game/DirectorCut/Audio/Puzzles/SFX_Puzzle_%s.SFX_Puzzle_%s"),
                PuzzleCueNames[Index], PuzzleCueNames[Index]);
            Sound = LoadObject<USoundBase>(nullptr, *Path);
            CachedSounds[Index] = Sound;
        }
        return Sound;
    }
}

bool DirectorCutPuzzleAudio::Play(const UObject* Context, ECue Cue, const FVector& Location)
{
    const uint8 Index = static_cast<uint8>(Cue);
    if (auto* Sound = FindPuzzleSound(Index))
    {
        UGameplayStatics::PlaySoundAtLocation(Context, Sound, Location);
        UE_LOG(LogDirectorCutPuzzleAudio, Verbose, TEXT("Played %s"), PuzzleCueNames[Index]);
        return true;
    }
    return false;
}

void DirectorCutPuzzleAudio::PlayLoop(UAudioComponent& Component, ECue Cue)
{
    const uint8 Index = static_cast<uint8>(Cue);
    if (auto* Sound = FindPuzzleSound(Index))
    {
        Component.SetSound(Sound);
        Component.Play();
        UE_LOG(LogDirectorCutPuzzleAudio, Verbose, TEXT("Played %s"), PuzzleCueNames[Index]);
    }
}
