#pragma once

#include "CoreMinimal.h"

namespace DirectorCutPuzzleAudio
{
    enum class ECue : uint8
    {
        ControlTick,
        ChairEquip,
        WheelLatch,
        LiftStart,
        LiftLock,
        HeroLegs,
        FocusMove,
        FocusLock,
        TakeRecord,
        TakeReplay,
        TakeLock,
        FilmNotch,
        FilmLock,
        ArchiveCrate,
        RgbDial,
        RgbLock,
        LampAim,
        RetakeLock,
        StandSwitch,
        FerryMotor,
        BridgeLock,
        Count
    };

    bool Play(const UObject* Context, ECue Cue, const FVector& Location);
}
