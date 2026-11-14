#include "DirectorCutStoryData.h"

#include "ColorSignalPuzzle.h"
#include "DirectorCutGraphics.h"
#include "DirectorCutInteractionData.h"
#include "EngineUtils.h"
#include "FocusPropPuzzle.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "ResolutionCorridor.h"
#include "Stage3StorageCrate.h"
#include "Stage3TakePuzzle.h"
#include "Stage4ShadowStandIn.h"
#include "Stage4ShadowTheatre.h"

#define LOCTEXT_NAMESPACE "DirectorCutPuzzleGuide"

namespace
{
    const FDirectorCutGuideControl MoveControl = {TEXT("A / D"), LOCTEXT("MoveKo", "이동"), LOCTEXT("Move", "Move")};
    const FDirectorCutGuideControl Jump = {TEXT("Space"), LOCTEXT("JumpKo", "점프"), LOCTEXT("Jump", "Jump")};
    const FDirectorCutGuideControl OpenSettings = {TEXT("⚙"), LOCTEXT("SettingsKo", "그래픽 설정"), LOCTEXT("Settings", "Graphics settings")};
    const FDirectorCutGuideControl Exit = {TEXT("E"), LOCTEXT("ExitKo", "나가기"), LOCTEXT("Exit", "Exit")};

    template<typename ActorType>
    const ActorType* FindPuzzle(UWorld& World)
    {
        for (TActorIterator<ActorType> It(&World); It; ++It)
        {
            if (!It->IsActorBeingDestroyed()) return *It;
        }
        return nullptr;
    }

    FDirectorCutPuzzleGuide WorkshopGuide(EDirectorCutWorkshopPhase Phase, bool bManualWheel)
    {
        const FText WheelKo = LOCTEXT("WheelTitleKo", "바퀴와 황동 표식");
        const FText WheelEn = LOCTEXT("WheelTitle", "Wheel and brass marks");
        const FText LiftKo = LOCTEXT("LiftTitleKo", "톱니 승강기");
        const FText LiftEn = LOCTEXT("LiftTitle", "Gear lift");
        switch (Phase)
        {
        case EDirectorCutWorkshopPhase::Wheel:
            if (bManualWheel)
            {
                return {WheelKo, WheelEn,
                    LOCTEXT("WheelPushKo", "바퀴 왼쪽에서 E로 밀어 황동 표식 사이에 놓으세요. 그다음 모델 품질을 낮춰 통로를 여세요."),
                    LOCTEXT("WheelPush", "Press E from the left to push the wheel between the brass marks. Then set model quality to Low to open the gate."),
                    {{TEXT("E"), LOCTEXT("PushKo", "바퀴 밀기"), LOCTEXT("Push", "Push wheel")},
                     {TEXT("Esc → 1"), LOCTEXT("ModelLowKo", "모델 품질 낮음"), LOCTEXT("ModelLow", "Model quality: Low")}}};
            }
            return {WheelKo, WheelEn,
                LOCTEXT("LegacyPushKo", "모델 품질을 높여 바퀴를 굴리고 황동 표식 사이에서 낮춰 멈추세요."),
                LOCTEXT("LegacyPush", "Set model quality to High to roll the wheel, then switch to Low at the brass marks."),
                {{TEXT("Q"), LOCTEXT("QualityKo", "모델 품질 전환"), LOCTEXT("Quality", "Toggle model quality")}}};
        case EDirectorCutWorkshopPhase::WheelNeedsHigh:
            return {WheelKo, WheelEn,
                LOCTEXT("WheelUnlockKo", "낮음에서는 바퀴가 고정됩니다. 모델 품질을 높인 뒤 바퀴 앞에서 E를 누르세요."),
                LOCTEXT("WheelUnlock", "The wheel is locked on Low. Set model quality to High, then press E near the wheel."),
                {{TEXT("Esc → 2"), LOCTEXT("WheelHighKo", "모델 품질 높음"), LOCTEXT("WheelHigh", "Model quality: High")}}};
        case EDirectorCutWorkshopPhase::WheelNeedsLow:
            return {WheelKo, WheelEn,
                LOCTEXT("WheelParkedKo", "바퀴가 표식 사이에 들어왔습니다. 모델 품질을 낮춰 통로를 여세요."),
                LOCTEXT("WheelParked", "The wheel is in place. Set model quality to Low to open the gate."),
                {{TEXT("Esc → 1"), LOCTEXT("ParkLowKo", "모델 품질 낮음"), LOCTEXT("ParkLow", "Model quality: Low")}}};
        case EDirectorCutWorkshopPhase::Hall:
            return {LiftKo, LiftEn, LOCTEXT("FindLiftKo", "오른쪽 통로를 따라 톱니 승강기로 가세요."),
                LOCTEXT("FindLift", "Follow the passage to the gear lift on the right."), {MoveControl}};
        case EDirectorCutWorkshopPhase::LiftNeedsHigh:
            return {LiftKo, LiftEn,
                bManualWheel ? LOCTEXT("LiftSetupKo", "승강기 중앙에 올라 모델 품질을 높인 뒤, 메뉴를 닫고 E를 누르세요.")
                             : LOCTEXT("LegacyLiftSetupKo", "승강기 중앙에 올라 모델 품질을 높이고 E를 누르세요."),
                bManualWheel ? LOCTEXT("LiftSetup", "Board the center of the lift, set model quality to High, then press E after closing Settings.")
                             : LOCTEXT("LegacyLiftSetup", "Stand at the center of the lift, set model quality to High, then press E."),
                {{bManualWheel ? TEXT("Esc → 2") : TEXT("Q"), LOCTEXT("ModelHighKo", "모델 품질 높음"), LOCTEXT("ModelHigh", "Model quality: High")},
                 {TEXT("E"), LOCTEXT("LiftUseKo", "승강기 작동"), LOCTEXT("LiftUse", "Start lift")}}};
        case EDirectorCutWorkshopPhase::LiftReady:
            return {LiftKo, LiftEn, LOCTEXT("BoardLiftKo", "승강기 중앙에 서서 E를 누르세요."),
                LOCTEXT("BoardLift", "Stand at the center of the lift and press E."),
                {{TEXT("E"), LOCTEXT("StartLiftKo", "승강기 작동"), LOCTEXT("StartLift", "Start lift")}}};
        case EDirectorCutWorkshopPhase::LiftMoving:
            return {LiftKo, LiftEn, LOCTEXT("RideLiftKo", "승강기가 위층에 도착할 때까지 기다리세요."),
                LOCTEXT("RideLift", "Wait for the lift to reach the upper floor.")};
        case EDirectorCutWorkshopPhase::Exit:
            return {LiftKo, LiftEn, LOCTEXT("UpperExitKo", "위층 오른쪽 문으로 나가세요."),
                LOCTEXT("UpperExit", "Take the door on the right upstairs."), {MoveControl}};
        default:
            return {};
        }
    }

    FDirectorCutPuzzleGuide FocusGuide(const AFocusPropPuzzle& Focus)
    {
        const FText TitleKo = LOCTEXT("FocusTitleKo", "초점 밖 열쇠");
        const FText TitleEn = LOCTEXT("FocusTitle", "The key out of focus");
        if (Focus.bSolved)
        {
            if (Focus.bActive)
            {
                return {TitleKo, TitleEn, LOCTEXT("FocusOpeningKo", "열쇠가 맞춰졌습니다. 출구가 열리고 있습니다."),
                    LOCTEXT("FocusOpening", "The key is aligned. The exit is opening.")};
            }
            return {TitleKo, TitleEn, LOCTEXT("FocusSolvedKo", "열쇠가 맞춰졌습니다. 열린 통로로 나가세요."),
                LOCTEXT("FocusSolved", "The key is aligned. Continue through the open passage."), {MoveControl}};
        }
        if (!Focus.bActive)
        {
            return {TitleKo, TitleEn, LOCTEXT("FocusStartKo", "카메라에서 두 열쇠 조각을 한 모양으로 겹치세요."),
                LOCTEXT("FocusStart", "Use the camera to line up the two pieces of the key."),
                {{TEXT("E"), LOCTEXT("FocusOpenKo", "카메라 조작"), LOCTEXT("FocusOpen", "Use camera")}}};
        }
        const bool bAligned = Focus.IsAligned();
        return {TitleKo, TitleEn,
            bAligned ? LOCTEXT("FocusConfirmKo", "조각이 겹쳤습니다. Enter로 확정하세요.")
                     : LOCTEXT("FocusAlignKo", "앞뒤 조각을 번갈아 선택하고 좌우로 움직여 화면에서 겹치세요."),
            bAligned ? LOCTEXT("FocusConfirm", "The pieces overlap. Press Enter to confirm.")
                     : LOCTEXT("FocusAlign", "Select each piece in turn and slide it until the two overlap on screen."),
            {{TEXT("1 / 2"), LOCTEXT("PiecesKo", "앞 / 뒤 조각"), LOCTEXT("Pieces", "Near / far piece")},
             {TEXT("A / D"), LOCTEXT("SlideKo", "좌우 이동"), LOCTEXT("Slide", "Slide left / right")},
             {TEXT("Shift"), LOCTEXT("FineKo", "미세 조절"), LOCTEXT("Fine", "Fine adjustment")},
             {TEXT("Enter"), LOCTEXT("ConfirmKo", "확정"), LOCTEXT("Confirm", "Confirm")},
             {TEXT("R"), LOCTEXT("ResetKo", "초기화"), LOCTEXT("Reset", "Reset")}, Exit}};
    }

    FDirectorCutPuzzleGuide TakeGuide(const AStage3TakePuzzle& Take, const APawn& Pawn)
    {
        const FText TitleKo = LOCTEXT("TakeTitleKo", "두 테이크의 용");
        const FText TitleEn = LOCTEXT("TakeTitle", "Two takes");
        const FDirectorCutGuideControl Retry = {TEXT("R"), LOCTEXT("RecordAgainKo", "다시 녹화"), LOCTEXT("RecordAgain", "Record again")};
        const auto* Character = Cast<ACharacter>(&Pawn);
        switch (Take.Phase)
        {
        case EStage3TakePhase::Recording:
            if (Character && Take.CanFinishRecording(*Character))
            {
                return {TitleKo, TitleEn,
                    LOCTEXT("TakeHoldKo", "왼쪽 발판에서 조금 더 기다렸다가 E를 누르세요. 머무른 시간이 길수록 재생 때 여유가 생깁니다."),
                    LOCTEXT("TakeHold", "Hold the left plate a little longer, then press E. A longer hold gives you more time during playback."),
                    {{TEXT("E"), LOCTEXT("FinishRecordingKo", "촬영 마치기"), LOCTEXT("FinishRecording", "Finish recording")}, Retry}};
            }
            return {TitleKo, TitleEn, LOCTEXT("TakeLeftKo", "왼쪽 발판으로 가서 녹화가 준비될 때까지 그 위에 서 있으세요."),
                LOCTEXT("TakeLeft", "Go to the left plate and hold it until the take is ready."), {MoveControl, Retry}};
        case EStage3TakePhase::Playing:
            return {TitleKo, TitleEn, LOCTEXT("TakeRightKo", "녹화 속 드래곤이 왼쪽 발판을 밟는 동안 오른쪽 발판을 밟으세요."),
                LOCTEXT("TakeRight", "Stand on the right plate while your recording holds the left plate."), {MoveControl, Retry}};
        case EStage3TakePhase::ReplayReady:
            return {TitleKo, TitleEn, LOCTEXT("TakeRetryKo", "카메라로 돌아가 녹화한 장면을 재생하거나 다시 촬영하세요."),
                LOCTEXT("TakeRetry", "Return to the camera to replay the take, or record it again."),
                {{TEXT("E"), LOCTEXT("ReplayKo", "첫 촬영 재생"), LOCTEXT("Replay", "Replay first take")}, Retry}};
        case EStage3TakePhase::Solved:
            return {TitleKo, TitleEn, LOCTEXT("TakeDoneKo", "두 발판이 고정됐습니다. 오른쪽 영사 구역으로 가세요."),
                LOCTEXT("TakeDone", "Both plates are locked. Continue right to the projection room."), {MoveControl}};
        default:
            return {TitleKo, TitleEn, LOCTEXT("TakeStartKo", "카메라에서 녹화를 시작하고 왼쪽 발판으로 가세요."),
                LOCTEXT("TakeStart", "Start recording at the camera, then head to the left plate."),
                {{TEXT("E"), LOCTEXT("RecordKo", "첫 촬영 시작"), LOCTEXT("Record", "Record first take")}}};
        }
    }

    FDirectorCutPuzzleGuide BridgeGuide(const AResolutionCorridor& Bridge)
    {
        const FText TitleKo = LOCTEXT("BridgeTitleKo", "축소 영사로 잇는 다리");
        const FText TitleEn = LOCTEXT("BridgeTitle", "The projection bridge");
        if (Bridge.bCompleted)
        {
            return {TitleKo, TitleEn, LOCTEXT("BridgeDoneKo", "영사선이 이어져 다리가 고정됐습니다. 건너편 보관 구역으로 가세요."),
                LOCTEXT("BridgeDone", "The bridge is locked in place. Cross to the storage room."), {MoveControl}};
        }
        if (!Bridge.bProjectionReadable)
        {
            return {TitleKo, TitleEn, LOCTEXT("BridgeLowKo", "오른쪽 위 그래픽 설정에서 해상도를 낮음으로 바꾸면 영사막의 길이 드러납니다."),
                LOCTEXT("BridgeLow", "Set Resolution to Low in the graphics menu to reveal the path on the screen."), {OpenSettings}};
        }
        if (!Bridge.bBridgeConsoleOpen)
        {
            return {TitleKo, TitleEn, LOCTEXT("BridgeStartKo", "영사막에 길이 드러났습니다. 검수대에서 필름을 조작하세요."),
                LOCTEXT("BridgeStart", "The screen shows the path. Use the film desk to adjust the clips."),
                {{TEXT("E"), LOCTEXT("FilmDeskKo", "필름 검수대 조작"), LOCTEXT("FilmDesk", "Use film desk")}}};
        }
        return {TitleKo, TitleEn,
            LOCTEXT("BridgeAlignKo", "두 필름 조각을 움직여 영사막의 선이 끊김 없이 이어지게 하세요. 맞으면 다리가 자동으로 고정됩니다."),
            LOCTEXT("BridgeAlign", "Slide both clips until the lines join. The bridge locks automatically when they match."),
            {{TEXT("1 / 2"), LOCTEXT("ClipKo", "필름 선택"), LOCTEXT("Clip", "Select clip")},
             {TEXT("↑ / ↓"), LOCTEXT("ClipSlideKo", "필름 위아래 이동"), LOCTEXT("ClipSlide", "Slide clip up / down")}, Exit}};
    }

    FDirectorCutPuzzleGuide ArchiveGuide(UWorld& World, const APawn& Pawn)
    {
        const double X = Pawn.GetActorLocation().X;
        if (X < 1450.)
        {
            if (const auto* Focus = FindPuzzle<AFocusPropPuzzle>(World)) return FocusGuide(*Focus);
        }
        else if (X < 4800.)
        {
            if (const auto* Take = FindPuzzle<AStage3TakePuzzle>(World)) return TakeGuide(*Take, Pawn);
        }
        else if (const auto* Bridge = FindPuzzle<AResolutionCorridor>(World))
        {
            if (X < 6500. || !Bridge->bCompleted) return BridgeGuide(*Bridge);
            if (const auto* Crate = FindPuzzle<AStage3StorageCrate>(World); Crate && !Crate->bOpened)
            {
                return {LOCTEXT("CrateTitleKo", "운반 상자"), LOCTEXT("CrateTitle", "The transport crate"),
                    LOCTEXT("CrateGoalKo", "작업등 아래의 운반 상자를 열어 내용물을 확인하세요."),
                    LOCTEXT("CrateGoal", "Open the transport crate under the work light."),
                    {{TEXT("E"), LOCTEXT("OpenCrateKo", "상자 열기"), LOCTEXT("OpenCrate", "Open crate")}}};
            }
        }
        return {};
    }

    FDirectorCutPuzzleGuide RetakeGuide(const AStage4ShadowTheatre& Theatre, const FVector& Position, bool bShadows)
    {
        const FText TitleKo = LOCTEXT("RetakeTitleKo", "그림자 리테이크");
        const FText TitleEn = LOCTEXT("RetakeTitle", "Shadow retake");
        const double LocalX = Theatre.GetActorTransform().InverseTransformPosition(Position).X;
        if (LocalX >= 2570.)
        {
            return {TitleKo, TitleEn, LOCTEXT("RetakeDoneKo", "무대를 건넜습니다. 오른쪽의 그림자 대역 구역으로 가세요."),
                LOCTEXT("RetakeDone", "You crossed the stage. Continue right to Shadow Stand-In."), {MoveControl}};
        }
        if (!bShadows)
        {
            return {TitleKo, TitleEn, LOCTEXT("RetakeShadowKo", "그래픽 설정에서 그림자를 높음으로 바꿔 벽의 실루엣을 켜세요."),
                LOCTEXT("RetakeShadow", "Set Shadows to High in graphics settings to reveal the silhouette on the wall."), {OpenSettings}};
        }
        const int32 Cut = LocalX < 1190. ? Theatre.WestCut : Theatre.EastCut;
        return {TitleKo, TitleEn,
            Cut == INDEX_NONE ? LOCTEXT("RetakeAimKo", "황동 조작 표식에 서서 조명을 돌리세요. 그림자가 벽 표식과 맞으면 CUT으로 발판을 펼치세요.")
                              : LOCTEXT("RetakeCrossKo", "펼쳐진 발판을 점프해 건너세요. 다음 황동 표식에서 조명을 돌려 다시 CUT할 수 있습니다."),
            Cut == INDEX_NONE ? LOCTEXT("RetakeAim", "Stand on a brass mark and aim the lamp. When the shadow lines up, lock the shot to unfold the platforms.")
                              : LOCTEXT("RetakeCross", "Jump across the unfolded platforms. Aim and lock another shot at the next brass mark."),
            {{TEXT("Q / R"), LOCTEXT("AimKo", "조명 각도"), LOCTEXT("Aim", "Aim lamp")},
             {TEXT("E"), LOCTEXT("CutKo", "CUT 확정"), LOCTEXT("Cut", "Lock shot")}, Jump}};
    }

    FDirectorCutPuzzleGuide StandInGuide(const AStage4ShadowStandIn& Puzzle, const APawn& Pawn, bool bShadows)
    {
        const FText TitleKo = LOCTEXT("StandInTitleKo", "그림자 대역");
        const FText TitleEn = LOCTEXT("StandInTitle", "Shadow stand-in");
        const FVector Local = Puzzle.GetActorTransform().InverseTransformPosition(Pawn.GetActorLocation());
        const auto* Character = Cast<ACharacter>(&Pawn);
        if (Puzzle.bRaisedBridge)
        {
            return {TitleKo, TitleEn, LOCTEXT("StandInCrossKo", "다리가 고정됐습니다. 그림자를 켜둔 채 건너가세요."),
                LOCTEXT("StandInCross", "The bridge is latched. Keep Shadows on and cross."), {MoveControl, Jump}};
        }
        if (Character && Character->GetCharacterMovement()->IsMovingOnGround()
            && Local.X >= 1210. && Local.X <= 1380. && Local.Z > 121.)
        {
            return {TitleKo, TitleEn,
                bShadows ? LOCTEXT("HighSwitchKo", "높은 황동 표식 위에서 그림자를 낮음으로 바꾼 뒤 다시 높음으로 켜세요.")
                         : LOCTEXT("HighSwitchOnKo", "표식 위에서 그림자를 높음으로 켜 높은 스위치를 고정하세요."),
                bShadows ? LOCTEXT("HighSwitch", "On the raised brass mark, set Shadows to Low, then back to High.")
                         : LOCTEXT("HighSwitchOn", "On the mark, set Shadows to High to latch the upper switch."), {OpenSettings}};
        }
        if (Character && Puzzle.Ferry && Character->GetMovementBaseObject() == Puzzle.Ferry)
        {
            if (bShadows && Local.X < 740.)
            {
                return {TitleKo, TitleEn, LOCTEXT("FerryOffKo", "이동 발판에서 내리지 말고 그림자를 낮음으로 바꾸세요."),
                    LOCTEXT("FerryOff", "Stay on the ferry and set Shadows to Low to release it."), {OpenSettings}};
            }
            return {TitleKo, TitleEn, LOCTEXT("FerryRideKo", "발판이 반대편에 닿으면 내려서 오른쪽으로 가세요."),
                LOCTEXT("FerryRide", "Step off when the ferry reaches the far ledge."), {MoveControl}};
        }
        if (Puzzle.Checkpoint >= 1 || Local.X > 900.)
        {
            return {TitleKo, TitleEn,
                LOCTEXT("LowSwitchKo", "그림자를 높음으로 켜고 아래 벽 스위치에 그림자를 겹치세요. 발판이 올라오면 높은 황동 표식으로 점프하세요."),
                LOCTEXT("LowSwitch", "Set Shadows to High and let your shadow touch the lower wall switch. Jump onto the raised brass mark."),
                {OpenSettings, Jump}};
        }
        return {TitleKo, TitleEn,
            LOCTEXT("CallFerryKo", "그림자를 높음으로 켜고 황동 표식 위에 서세요. 그림자가 발판을 부르면 올라타세요."),
            LOCTEXT("CallFerry", "Set Shadows to High and stand on the brass mark. Board the ferry when your shadow calls it."),
            {OpenSettings, MoveControl}};
    }

    FDirectorCutPuzzleGuide VaultGuide(UWorld& World, const APawn& Pawn)
    {
        const double X = Pawn.GetActorLocation().X;
        if (X < 1320.)
        {
            const FText TitleKo = LOCTEXT("RgbTitleKo", "금고 조명 제어반");
            const FText TitleEn = LOCTEXT("RgbTitle", "Vault light console");
            if (const auto* Color = FindPuzzle<AColorSignalPuzzle>(World); Color && Color->bSolved)
            {
                return {TitleKo, TitleEn, LOCTEXT("RgbDoneKo", "금고 문이 열렸습니다. 오른쪽 무대로 가세요."),
                    LOCTEXT("RgbDone", "The vault door is open. Continue right to the stage."), {MoveControl}};
            }
            return {TitleKo, TitleEn,
                LOCTEXT("RgbGoalKo", "제어반에서 세 색의 밝기를 단서에 맞추세요. 값을 바꿀 때마다 자동으로 확인합니다."),
                LOCTEXT("RgbGoal", "Use the clue to set the three light levels. The console checks after each change."),
                {{TEXT("E"), LOCTEXT("RgbOpenKo", "제어반 열기"), LOCTEXT("RgbOpen", "Open console")}}};
        }
        const auto* Theatre = FindPuzzle<AStage4ShadowTheatre>(World);
        if (!Theatre || Theatre->bRecovered) return {};
        const auto* Graphics = World.GetSubsystem<UDirectorCutGraphicsSubsystem>();
        const bool bShadows = !Graphics || Graphics->IsHigh(EDirectorCutGraphicsOption::Shadows);
        const auto* StandIn = FindPuzzle<AStage4ShadowStandIn>(World);
        if (!StandIn || X < StandIn->GetActorLocation().X - 80.)
        {
            return RetakeGuide(*Theatre, Pawn.GetActorLocation(), bShadows);
        }
        if (!StandIn->bReachedExhibit)
        {
            return StandInGuide(*StandIn, Pawn, bShadows);
        }
        return {LOCTEXT("LegsTitleKo", "용의 하체"), LOCTEXT("LegsTitle", "The dragon's legs"),
            LOCTEXT("LegsGoalKo", "유리 보관함으로 다가가 용의 하체를 회수하세요."),
            LOCTEXT("LegsGoal", "Approach the glass case to recover your legs."),
            {{TEXT("E"), LOCTEXT("LegsRecoverKo", "하체 회수"), LOCTEXT("LegsRecover", "Recover legs")}}};
    }
}

bool HasDirectorCutPuzzleGuides(FName MapName)
{
    return MapName == TEXT("L_Stage1") || MapName == TEXT("Stage1") || MapName == TEXT("Stage2")
        || MapName == TEXT("Stage3_") || MapName == TEXT("Stage4");
}

FDirectorCutPuzzleGuide GetDirectorCutPuzzleGuide(FName MapName, APlayerController& Controller)
{
    UWorld* World = Controller.GetWorld();
    const APawn* Pawn = Controller.GetPawn();
    if (!World || !Pawn) return {};
    if (MapName == TEXT("L_Stage1"))
    {
        return {LOCTEXT("CastleTitleKo", "제작소로 가는 길"), LOCTEXT("CastleTitle", "To the workshop"),
            LOCTEXT("CastleGoalKo", "횃불을 따라 오른쪽 끝의 제작소 입구로 가세요."),
            LOCTEXT("CastleGoal", "Follow the torches to the workshop entrance on the right."),
            {MoveControl, {TEXT("← / →"), LOCTEXT("ArrowsKo", "이동"), LOCTEXT("Arrows", "Move")}}};
    }
    if (MapName == TEXT("Stage1") || MapName == TEXT("Stage2"))
    {
        return WorkshopGuide(GetDirectorCutWorkshopPhase(MapName, *World, Pawn->GetActorLocation()), MapName == TEXT("Stage2"));
    }
    if (MapName == TEXT("Stage3_")) return ArchiveGuide(*World, *Pawn);
    if (MapName == TEXT("Stage4")) return VaultGuide(*World, *Pawn);
    return {};
}

#undef LOCTEXT_NAMESPACE
