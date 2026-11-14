from pathlib import Path
p=Path("Source/MegaJam/Stage4ShadowTheatre.cpp")
s=p.read_text(encoding="utf-8-sig")
i=s.index("    const bool bPastGate =")
j=s.index("void AStage4ShadowTheatre::SetCheckpoint",i)
s=s[:i]+"""    const bool bPastGate = !IsValid(EntranceDoor) || EntranceDoor->bOpen;
    const bool bInside = bPastGate && P.X >= -315.f && P.X < SetEnd + 50.f;
    const float Framing = bInside ? FMath::SmoothStep(-315.f, 55.f, static_cast<float>(P.X)) : 0.f;
    Dragon->SetTheatreCameraFraming(Framing, GetActorLocation().X + FMath::Clamp(P.X, 485., 2370.));
    UpdateCostume(*Dragon, !bRecovered || (RecoveryTime >= 0.f && RecoveryTime < 2.04f));

    const auto* Graphics = GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>();
    const bool bShadows = !Graphics || Graphics->IsHigh(EDirectorCutGraphicsOption::Shadows);
    const auto* Controller = Cast<ADirectorCutPlayerController>(Dragon->GetController());
    const bool bSettingsOpen = Controller && Controller->IsGraphicsMenuOpen();
    const bool bGrounded = Dragon->GetCharacterMovement()->IsMovingOnGround();
    const int32 Station = bInside && bGrounded && !bSettingsOpen && !bRecovered ? StationAt(P.X) : None;

    ResetFlash = FMath::Max(ResetFlash - DeltaSeconds, 0.f);
    CutFlash = FMath::Max(CutFlash - DeltaSeconds, 0.f);
    InputHintTime = FMath::Max(InputHintTime - DeltaSeconds, 0.f);
    FinishMessage = FMath::Max(FinishMessage - DeltaSeconds, 0.f);
    UpdateLanes(DeltaSeconds, Station, bShadows);

    if (RecoveryTime >= 0.f)
    {
        UpdateRecovery(DeltaSeconds);
        return;
    }
    if (!bInside || bSettingsOpen || (bRecovered && FinishMessage <= 0.f))
    {
        Prompt = FText::GetEmpty();
        return;
    }
    if (bRecovered)
    {
        return;
    }
    if (P.Z < -165.f)
    {
        ReturnToMark(*Dragon);
        return;
    }
    if (bGrounded && P.X >= 1225.f && P.X <= 1525.f && Checkpoint < 1)
    {
        SetCheckpoint(*Dragon, 1);
    }
    else if (bGrounded && P.X >= 2570.f && Checkpoint < 2)
    {
        SetCheckpoint(*Dragon, 2);
    }
    else if (Station == Entrance && Checkpoint == 0)
    {
        SetCheckpoint(*Dragon, 0);
    }

    HandleControls(*Dragon, Station, bShadows);
    if (!bRecovered)
    {
        UpdatePrompt(P.X, Station, bShadows);
    }
}

void AStage4ShadowTheatre::HandleControls(ADirectorCutDragon& Dragon, int32 Station, bool bShadows)
{
    auto* Controller = Cast<ADirectorCutPlayerController>(Dragon.GetController());
    if (!Controller || !Dragon.GetCharacterMovement()->IsMovingOnGround())
    {
        return;
    }

    if (Station == None)
    {
        const double X = GetActorTransform().InverseTransformPosition(Dragon.GetActorLocation()).X;
        if (Checkpoint == 2 && FMath::Abs(X - ExhibitX) <= 125.f && Controller->WasInputKeyJustPressed(EKeys::E))
        {
            StartRecovery(Dragon);
        }
        return;
    }

    FRetake& Retake = Station == Entrance ? WestRetake : EastRetake;
    const bool bLeft = Controller->WasInputKeyJustPressed(EKeys::Q);
    const bool bRight = Controller->WasInputKeyJustPressed(EKeys::R);
    if (bLeft || bRight)
    {
        Retake.Angle = bRight ? 1 : 0;
        CutFlash = 0.f;
        InputHintTime = 0.f;
        return;
    }
    if (!Controller->WasInputKeyJustPressed(EKeys::E))
    {
        return;
    }
    if (!bShadows || Retake.Cue == INDEX_NONE || FMath::Abs(Retake.CurrentAngle - Retake.Angle) > .04f)
    {
        InputHintTime = 1.8f;
        InputHint = bShadows ? LOCTEXT("WaitForLamp", "Let the lamp reach its brass mark, then press E.")
            : LOCTEXT("NeedShadow", "Turn Shadows High in Settings to line up the shot.");
        return;
    }

    int32& Committed = Station == Entrance ? WestCut : EastCut;
    if (Committed == Retake.Cue)
    {
        return;
    }
    Committed = Retake.Cue;
    CutFlash = 1.1f;
    InputHintTime = 0.f;
    if (RailCue)
    {
        UGameplayStatics::PlaySoundAtLocation(this, RailCue, Dragon.GetActorLocation(), .8f, 1.05f);
    }
    if (Controller->PlayerCameraManager)
    {
        Controller->PlayerCameraManager->StartCameraFade(.14f, 0.f, .18f, FLinearColor::Black, false, false);
    }
}

"""+s[j:]
s=s.replace("void AStage4ShadowTheatre::ReturnToMark(ADirectorCutDragon& Dragon, bool bStruck)","void AStage4ShadowTheatre::ReturnToMark(ADirectorCutDragon& Dragon)")
s=s.replace('Heading = bStruck ? LOCTEXT("Struck", "FLY BAR CONTACT") : LOCTEXT("Miss", "MISSED MARK");','Heading = LOCTEXT("Miss", "MISSED MARK");')
i=s.index("void AStage4ShadowTheatre::UpdatePrompt(")
j=s.index("void AStage4ShadowTheatre::UpdateCostume",i)
s=s[:i]+"""void AStage4ShadowTheatre::UpdatePrompt(float X, int32 Station, bool bShadows)
{
    if (ResetFlash > 0.f)
    {
        return;
    }
    if (Checkpoint == 2 && FMath::Abs(X - ExhibitX) <= 125.f)
    {
        Heading = LOCTEXT("Exhibit", "ORIGINAL DRAGON LEGS");
        Prompt = LOCTEXT("Recover", "E  Recover");
        return;
    }
    if (Station == None)
    {
        Prompt = FText::GetEmpty();
        return;
    }
    if (CutFlash > 0.f)
    {
        Heading = LOCTEXT("Committed", "CUT LOCKED");
        Prompt = LOCTEXT("SetMoving", "Wait for the stones to slide into place.");
        return;
    }

    Heading = Station == Entrance ? LOCTEXT("Title", "SHADOW RETAKE")
        : Station == Center ? LOCTEXT("Checkpoint", "CENTER STAGE / CHECKPOINT")
        : LOCTEXT("Island", "LIGHTING ISLAND / RETAKE");
    if (InputHintTime > 0.f)
    {
        Prompt = InputHint;
    }
    else if (!bShadows)
    {
        Prompt = LOCTEXT("WorkLight", "Lit edges show the current cut.  Settings > Shadows: High to line up the next shot.");
    }
    else
    {
        const FRetake& Preview = Station == Entrance ? WestRetake : EastRetake;
        const int32 Committed = Station == Entrance ? WestCut : EastCut;
        const FText Set = Committed == INDEX_NONE ? LOCTEXT("Unset", "--") : FText::AsNumber(Committed + 1);
        Prompt = FText::Format(
            LOCTEXT("Controls", "Q / R  Aim lamp     E  Cut    |    Preview {0} / Cut {1}\\n{2}"),
            FText::AsNumber(Preview.Angle + 1), Set,
            Station == Island ? LOCTEXT("NextShot", "Line up a shot that reaches the display platform.")
                : LOCTEXT("ShotHint", "Use the castle's shadow to line up a brass mark. Compare the paths."));
    }
}

"""+s[j:]
p.write_text(s,encoding="utf-8")
