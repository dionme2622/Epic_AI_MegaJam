#include "DirectorCutPuzzleAudio.h"

#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"

DEFINE_LOG_CATEGORY_STATIC(LogDirectorCutPuzzleAudio, Log, All);

bool DirectorCutPuzzleAudio::Play(const UObject* Context, ECue Cue, const FVector& Location)
{
    static constexpr const TCHAR* Names[] = {
        TEXT("ControlTick"), TEXT("ChairEquip"), TEXT("WheelLatch"), TEXT("LiftStart"), TEXT("LiftLock"), TEXT("HeroLegs"),
        TEXT("FocusMove"), TEXT("FocusLock"), TEXT("TakeRecord"), TEXT("TakeReplay"), TEXT("TakeLock"),
        TEXT("FilmNotch"), TEXT("FilmLock"), TEXT("ArchiveCrate"), TEXT("RgbDial"), TEXT("RgbLock"), TEXT("LampAim"),
        TEXT("RetakeLock"), TEXT("StandSwitch"), TEXT("FerryMotor"), TEXT("BridgeLock")
    };
    static_assert(UE_ARRAY_COUNT(Names) == static_cast<uint8>(ECue::Count));
    const uint8 Index = static_cast<uint8>(Cue);
    check(Index < UE_ARRAY_COUNT(Names));

    static TWeakObjectPtr<USoundBase> CachedSounds[UE_ARRAY_COUNT(Names)];
    USoundBase* Sound = CachedSounds[Index].Get();
    if (!Sound)
    {
        const FString Path = FString::Printf(TEXT("/Game/DirectorCut/Audio/Puzzles/SFX_Puzzle_%s.SFX_Puzzle_%s"),
            Names[Index], Names[Index]);
        Sound = LoadObject<USoundBase>(nullptr, *Path);
        CachedSounds[Index] = Sound;
    }
    if (Sound)
    {
        UGameplayStatics::PlaySoundAtLocation(Context, Sound, Location);
        UE_LOG(LogDirectorCutPuzzleAudio, Verbose, TEXT("Played %s"), Names[Index]);
        return true;
    }
    return false;
}
