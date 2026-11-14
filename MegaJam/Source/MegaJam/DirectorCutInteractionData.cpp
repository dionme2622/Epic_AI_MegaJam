#include "DirectorCutInteractionData.h"

#include "ColorSignalPuzzle.h"
#include "Components/StaticMeshComponent.h"
#include "DirectorCutGraphics.h"
#include "DirectorCutTest.h"
#include "DirectorCutWheelchair.h"
#include "EngineUtils.h"
#include "FocusPropPuzzle.h"
#include "GameFramework/Character.h"
#include "GameFramework/PlayerController.h"
#include "ResolutionCorridor.h"
#include "Stage3StorageCrate.h"
#include "Stage3TakePuzzle.h"
#include "Stage4ShadowStandIn.h"
#include "Stage4ShadowTheatre.h"
#include "UObject/UnrealType.h"

#define LOCTEXT_NAMESPACE "DirectorCutInteractionData"

namespace
{
    // These bounds match the workshop Blueprints' gate and lift triggers.
    constexpr double WheelBayMinX = 1110.;
    constexpr double WheelBayMaxX = 1320.;
    constexpr double LiftFullHeight = 230.;

    template <typename ActorType>
    const ActorType* FindFirst(UWorld& World)
    {
        for (TActorIterator<ActorType> Actor(&World); Actor; ++Actor)
        {
            if (!Actor->IsActorBeingDestroyed()) return *Actor;
        }
        return nullptr;
    }

    bool IsNear(const FVector& Player, const FVector& Target, double Distance, double Height = 175.)
    {
        return FVector::DistSquared2D(Player, Target) <= FMath::Square(Distance)
            && FMath::Abs(Player.Z - Target.Z) < Height;
    }

    FDirectorCutInteractionPrompt MakePrompt(const TCHAR* Key, const FText& Korean, const FText& English, const FVector& Anchor)
    {
        return {FText::FromString(Key), Korean, English, Anchor};
    }

    bool ReadBlueprintFlag(const AActor& Actor, FName Name)
    {
        const FBoolProperty* Property = FindFProperty<FBoolProperty>(Actor.GetClass(), Name);
        return Property && Property->GetPropertyValue_InContainer(&Actor);
    }

    void WriteBlueprintFlag(AActor& Actor, FName Name, bool bValue)
    {
        if (const auto* Property = FindFProperty<FBoolProperty>(Actor.GetClass(), Name))
        {
            Property->SetPropertyValue_InContainer(&Actor, bValue);
        }
    }

    double ReadBlueprintNumber(const AActor& Actor, FName Name)
    {
        const FNumericProperty* Property = FindFProperty<FNumericProperty>(Actor.GetClass(), Name);
        return Property && Property->IsFloatingPoint()
            ? Property->GetFloatingPointPropertyValue(Property->ContainerPtrToValuePtr<void>(&Actor)) : 0.;
    }

    AActor* FindWorkshopDirector(FName MapName, UWorld& World)
    {
        if (MapName != TEXT("Stage1") && MapName != TEXT("Stage2")) return nullptr;

        const TCHAR* DirectorClassPath = MapName == TEXT("Stage2")
            ? TEXT("/Game/Stage2Workshop/BP_Stage2WorkshopDirector.BP_Stage2WorkshopDirector_C")
            : TEXT("/Game/Stage1Generated/BP_Stage1Director.BP_Stage1Director_C");
        UClass* DirectorClass = FindObject<UClass>(nullptr, DirectorClassPath);
        if (!DirectorClass) return nullptr;

        TActorIterator<AActor> It(&World, DirectorClass);
        return It ? *It : nullptr;
    }

    bool GetWorkshopPrompt(FName MapName, UWorld& World, const FVector& Player, FDirectorCutInteractionPrompt& Out)
    {
        const AActor* WorkshopDirector = FindWorkshopDirector(MapName, World);
        if (!WorkshopDirector) return false;

        const AActor& Director = *WorkshopDirector;
        const bool bStage2 = MapName == TEXT("Stage2");
        if (ReadBlueprintFlag(Director, TEXT("MenuOpen")) || ReadBlueprintFlag(Director, TEXT("LiftActive"))) return false;

        const double WheelX = ReadBlueprintNumber(Director, TEXT("WheelX"));
        if (bStage2 && !ReadBlueprintFlag(Director, TEXT("WheelSolved")) && Player.Z > 0. && Player.Z < 310.
            && FMath::Abs(Player.X - WheelX) < 220.)
        {
            const FVector Anchor(WheelX, -30., 312.);
            if (ReadBlueprintFlag(Director, TEXT("IsLow")))
            {
                if (WheelX > WheelBayMinX && WheelX < WheelBayMaxX) return false;
                Out = MakePrompt(TEXT("Esc"), LOCTEXT("UnlockWheelKo", "설정에서 2로 모델 품질 높음 선택"),
                    LOCTEXT("UnlockWheelEn", "Choose 2 for High model quality in Settings"), Anchor);
                return true;
            }

            const double PushTarget = ReadBlueprintNumber(Director, TEXT("WheelPushTarget"));
            if (FMath::Abs(PushTarget - WheelX) >= 4.) return false;

            if (WheelX > WheelBayMinX && WheelX < WheelBayMaxX)
            {
                Out = MakePrompt(TEXT("Esc"), LOCTEXT("ParkWheelKo", "설정에서 1로 모델 품질 낮음 선택"),
                    LOCTEXT("ParkWheelEn", "Choose 1 for Low model quality in Settings"), Anchor);
                return true;
            }

            const bool bPushRight = Player.X <= WheelX;
            if (bPushRight ? WheelX >= 1420. : WheelX <= 440.) return false;

            Out = MakePrompt(TEXT("E"),
                bPushRight ? LOCTEXT("PushWheelRightKo", "바퀴를 오른쪽으로 밀기") : LOCTEXT("PushWheelLeftKo", "바퀴를 왼쪽으로 밀기"),
                bPushRight ? LOCTEXT("PushWheelRightEn", "Push the wheel right") : LOCTEXT("PushWheelLeftEn", "Push the wheel left"), Anchor);
            return true;
        }
        if (!bStage2 && Player.X >= 180. && Player.X <= 1600. && !ReadBlueprintFlag(Director, TEXT("WheelSolved")))
        {
            const bool bLow = ReadBlueprintFlag(Director, TEXT("IsLow"));
            Out = MakePrompt(TEXT("Q"),
                bLow ? LOCTEXT("RollWheelKo", "높음으로 바꿔 바퀴 굴리기") : LOCTEXT("StopWheelKo", "낮음으로 바꿔 바퀴 멈추기"),
                bLow ? LOCTEXT("RollWheelEn", "Set High to roll the wheel") : LOCTEXT("StopWheelEn", "Set Low to stop the wheel"),
                FVector(FMath::Clamp(WheelX, 440., 1420.), -30., 312.));
            return true;
        }

        const double LiftHeight = ReadBlueprintNumber(Director, TEXT("LiftAlpha"));
        const bool bOnLift = Player.X > 8585. && Player.X < 8800.
            && Player.Z > LiftHeight + 90. && Player.Z < LiftHeight + 150.;
        if (!bOnLift) return false;

        const bool bLow = ReadBlueprintFlag(Director, TEXT("IsLow"));
        const FVector Anchor(8700., -30., LiftHeight + 210.);
        if (bLow && bStage2)
        {
            Out = MakePrompt(TEXT("Esc"), LOCTEXT("WorkshopLiftHighKo", "설정에서 2로 모델 품질 높음 선택"),
                LOCTEXT("WorkshopLiftHighEn", "Choose 2 for High model quality in Settings"), Anchor);
        }
        else if (bLow)
        {
            Out = MakePrompt(TEXT("Q"), LOCTEXT("LiftHighKo", "모델 디테일을 높음으로"),
                LOCTEXT("LiftHighEn", "Set model detail to High"), Anchor);
        }
        else if (bStage2 && LiftHeight > 115.)
        {
            Out = MakePrompt(TEXT("E"), LOCTEXT("LowerLiftKo", "승강기 내리기"),
                LOCTEXT("LowerLiftEn", "Lower the lift"), Anchor);
        }
        else
        {
            Out = MakePrompt(TEXT("E"), LOCTEXT("UseLiftKo", "승강기 작동"),
                LOCTEXT("UseLiftEn", "Operate the lift"), Anchor);
        }
        return true;
    }

    bool GetArchivePrompt(UWorld& World, const APawn& Pawn, FDirectorCutInteractionPrompt& Out)
    {
        const FVector Player = Pawn.GetActorLocation();
        const auto* Focus = FindFirst<AFocusPropPuzzle>(World);
        const auto* Bridge = FindFirst<AResolutionCorridor>(World);
        if ((Focus && Focus->bActive) || (Bridge && Bridge->bBridgeConsoleOpen)) return false;

        if (Focus && !Focus->bSolved && IsNear(Player, Focus->GetActorLocation(), Focus->InteractDistance))
        {
            Out = MakePrompt(TEXT("E"), LOCTEXT("FocusKo", "초점 조절"), LOCTEXT("FocusEn", "Adjust focus"),
                Focus->GetActorLocation() + FVector(0., -20., 192.));
            return true;
        }

        if (const auto* Take = FindFirst<AStage3TakePuzzle>(World))
        {
            if (const auto* Character = Cast<ACharacter>(&Pawn))
            {
                if (Take->CanUseCamera(*Character))
                {
                    const bool bReplay = Take->Phase == EStage3TakePhase::ReplayReady;
                    Out = MakePrompt(TEXT("E"), bReplay ? LOCTEXT("ReplayKo", "첫 촬영 다시 재생") : LOCTEXT("RecordKo", "첫 촬영 시작"),
                        bReplay ? LOCTEXT("ReplayEn", "Replay the first take") : LOCTEXT("RecordEn", "Record the first take"),
                        Take->GetActorTransform().TransformPosition(Take->CameraMark + FVector(0., -110., 275.)));
                    return true;
                }
                if (Take->CanFinishRecording(*Character))
                {
                    Out = MakePrompt(TEXT("E"), LOCTEXT("FinishTakeKo", "촬영 마치기"), LOCTEXT("FinishTakeEn", "Finish the take"),
                        Take->GetActorTransform().TransformPosition(Take->LeftMark + FVector(0., -25., 185.)));
                    return true;
                }
            }
        }

        if (Bridge && Bridge->CanOpenBridgeConsole())
        {
            const FVector Desk = IsValid(Bridge->BridgeConsole) ? Bridge->BridgeConsole->GetActorLocation()
                : Bridge->GetActorLocation() + FVector(210., 0., 0.);
            Out = MakePrompt(TEXT("E"), LOCTEXT("BridgeKo", "필름 검수대 조작"), LOCTEXT("BridgeEn", "Operate the film desk"),
                Desk + FVector(0., 35., 228.));
            return true;
        }

        if (const auto* Crate = FindFirst<AStage3StorageCrate>(World);
            Crate && !Crate->bOpened && (!IsValid(Crate->Corridor) || Crate->Corridor->bCompleted)
            && IsNear(Player, Crate->GetActorLocation(), Crate->InteractionDistance))
        {
            Out = MakePrompt(TEXT("E"), LOCTEXT("CrateKo", "보관 상자 열기"), LOCTEXT("CrateEn", "Open the storage crate"),
                Crate->GetActorLocation() + FVector(0., 0., 188.));
            return true;
        }
        return false;
    }

    bool GetVaultPrompt(UWorld& World, const APawn& Pawn, FDirectorCutInteractionPrompt& Out)
    {
        if (const auto* Color = FindFirst<AColorSignalPuzzle>(World))
        {
            if (Color->bActive) return false;
            if (!Color->bSolved && IsNear(Pawn.GetActorLocation(), Color->GetActorLocation(), Color->InteractDistance))
            {
                Out = MakePrompt(TEXT("E"), LOCTEXT("LightPanelKo", "색 조명 조절"), LOCTEXT("LightPanelEn", "Calibrate the lights"),
                    Color->GetActorLocation() + FVector(0., -90., 248.));
                return true;
            }
        }

        const auto* Dragon = Cast<ADirectorCutDragon>(&Pawn);
        const auto* Theatre = FindFirst<AStage4ShadowTheatre>(World);
        if (Dragon && Theatre && Theatre->GetInteractionPrompt(*Dragon, Out)) return true;

        const auto* StandIn = FindFirst<AStage4ShadowStandIn>(World);
        if (!StandIn || StandIn->bReachedExhibit || !Dragon) return false;

        const FVector Player = Pawn.GetActorLocation();
        const FVector Local = StandIn->GetActorTransform().InverseTransformPosition(Player);
        const auto* Graphics = World.GetSubsystem<UDirectorCutGraphicsSubsystem>();
        const bool bShadows = !Graphics || Graphics->IsHigh(EDirectorCutGraphicsOption::Shadows);
        const bool bOnFerry = StandIn->Ferry && Dragon->GetMovementBaseObject() == StandIn->Ferry;
        if ((bOnFerry && Local.X < 740. && bShadows)
            || (StandIn->Checkpoint >= 1 && Local.X >= 1210. && Local.X <= 1380. && !StandIn->bRaisedBridge))
        {
            Out = MakePrompt(TEXT("\u2699"), LOCTEXT("AdjustShadowsKo", "설정에서 그림자 바꾸기"),
                LOCTEXT("AdjustShadowsEn", "Change shadows in Settings"), Player + FVector(0., -35., 110.));
            return true;
        }
        return false;
    }
}

EDirectorCutWorkshopPhase GetDirectorCutWorkshopPhase(FName MapName, UWorld& World, const FVector& Player)
{
    using EPhase = EDirectorCutWorkshopPhase;
    const AActor* Director = FindWorkshopDirector(MapName, World);
    if (!Director) return EPhase::Unavailable;

    const bool bLow = ReadBlueprintFlag(*Director, TEXT("IsLow"));
    if (Player.X >= 8260.)
    {
        if (ReadBlueprintFlag(*Director, TEXT("LiftActive"))) return EPhase::LiftMoving;

        const double LiftHeight = ReadBlueprintNumber(*Director, TEXT("LiftAlpha"));
        if ((Player.X >= 8800. && Player.Z >= 300.) || LiftHeight >= LiftFullHeight) return EPhase::Exit;

        return bLow ? EPhase::LiftNeedsHigh : EPhase::LiftReady;
    }
    if (Player.X < 2100. && !ReadBlueprintFlag(*Director, TEXT("WheelSolved")))
    {
        if (MapName != TEXT("Stage2")) return EPhase::Wheel;
        if (bLow) return EPhase::WheelNeedsHigh;

        const double WheelX = ReadBlueprintNumber(*Director, TEXT("WheelX"));
        const double PushTarget = ReadBlueprintNumber(*Director, TEXT("WheelPushTarget"));
        const bool bParked = WheelX > WheelBayMinX && WheelX < WheelBayMaxX && FMath::Abs(WheelX - PushTarget) < 4.;
        return bParked ? EPhase::WheelNeedsLow : EPhase::Wheel;
    }
    return EPhase::Hall;
}

bool IsDirectorCutWorkshopMenuOpen(FName MapName, UWorld& World)
{
    const AActor* Director = FindWorkshopDirector(MapName, World);
    return Director && ReadBlueprintFlag(*Director, TEXT("MenuOpen"));
}

void SetDirectorCutWorkshopMenuOpen(UWorld& World, bool bOpen)
{
    if (AActor* Director = FindWorkshopDirector(TEXT("Stage2"), World))
    {
        WriteBlueprintFlag(*Director, TEXT("MenuOpen"), bOpen);
    }
}

bool CanChangeDirectorCutWorkshopDetail(UWorld& World)
{
    const AActor* Director = FindWorkshopDirector(TEXT("Stage2"), World);
    return !Director || !ReadBlueprintFlag(*Director, TEXT("LiftActive"));
}

void ApplyDirectorCutWorkshopDetail(UWorld& World, bool bHigh)
{
    AActor* Director = FindWorkshopDirector(TEXT("Stage2"), World);
    if (!Director) return;

    WriteBlueprintFlag(*Director, TEXT("IsLow"), !bHigh);
    for (TActorIterator<AActor> It(&World); It; ++It)
    {
        if (It->ActorHasTag(TEXT("StageHigh")))
        {
            It->SetActorHiddenInGame(!bHigh);
        }
        else if (It->ActorHasTag(TEXT("StageLow")))
        {
            It->SetActorHiddenInGame(bHigh);
        }
    }
}

bool GetDirectorCutInteractionPrompt(FName MapName, APlayerController& Controller, FDirectorCutInteractionPrompt& Out)
{
    Out = {};
    const APawn* Pawn = Controller.GetPawn();
    UWorld* World = Controller.GetWorld();
    const auto* Director = Cast<ADirectorCutPlayerController>(&Controller);
    if (!Pawn || !World || (Director && Director->IsGraphicsMenuOpen())) return false;

    if (MapName == TEXT("L_Stage1"))
    {
        const auto* Dragon = Cast<ADirectorCutDragon>(Pawn);
        const auto* Chair = FindFirst<ADirectorCutWheelchair>(*World);
        if (!Dragon || !Chair || !Chair->CanEquip(*Dragon)) return false;

        Out = MakePrompt(TEXT("E"), LOCTEXT("EquipChairKo", "휠체어 장착"),
            LOCTEXT("EquipChairEn", "Equip wheelchair"), Chair->GetPromptAnchor());
        return true;
    }
    if (MapName == TEXT("Stage1") || MapName == TEXT("Stage2"))
    {
        return GetWorkshopPrompt(MapName, *World, Pawn->GetActorLocation(), Out);
    }
    if (MapName == TEXT("Stage3_"))
    {
        if (Controller.GetViewTarget() != Pawn) return false;
        return GetArchivePrompt(*World, *Pawn, Out);
    }
    if (MapName == TEXT("Stage4"))
    {
        return GetVaultPrompt(*World, *Pawn, Out);
    }
    return false;
}

#undef LOCTEXT_NAMESPACE
