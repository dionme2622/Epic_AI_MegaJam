#include "DirectorCutPlayHUD.h"

#include "ColorSignalPuzzle.h"
#include "Camera/PlayerCameraManager.h"
#include "DirectorCutGraphics.h"
#include "DirectorCutInteractionData.h"
#include "DirectorCutStoryData.h"
#include "DirectorCutWallNote.h"
#include "DirectorCutVoiceLookup.h"
#include "Components/AudioComponent.h"
#include "Sound/SoundBase.h"
#include "Engine/GameViewportClient.h"
#include "Engine/UserInterfaceSettings.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "FocusPropPuzzle.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "InputCoreTypes.h"
#include "Stage4ShadowTheatre.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SConstraintCanvas.h"
#include "Widgets/Layout/SDPIScaler.h"
#include "Widgets/Layout/SScaleBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"

#define LOCTEXT_NAMESPACE "DirectorCutPlayHUD"

namespace
{
    const FLinearColor HudPanelColor(.019f, .012f, .022f, .97f);
    const FLinearColor HudGold(.97f, .75f, .40f);
    const FLinearColor HudIvory(.96f, .94f, .89f);
    const FLinearColor SoftIvory(.81f, .76f, .72f);
    const FLinearColor HudBrass(.31f, .19f, .075f);
    const FLinearColor Ink(.065f, .036f, .019f);
    const FLinearColor Parchment(.76f, .60f, .37f);
    constexpr int32 MaxGuideControls = 6;

    float ReadableScale(const UGameViewportClient& Viewport, float Minimum)
    {
        FVector2D Size;
        Viewport.GetViewportSize(Size);
        if (Size.X <= 0 || Size.Y <= 0) return 1.f;
        const float ViewportScale = GetDefault<UUserInterfaceSettings>()->GetDPIScaleBasedOnSize(
            FIntPoint(FMath::RoundToInt(Size.X), FMath::RoundToInt(Size.Y)));
        return FMath::Clamp(Minimum / FMath::Max(ViewportScale, .1f), 1.f, 2.25f);
    }

    TSharedRef<STextBlock> Line(TAttribute<FText> Text, int32 Size, const FLinearColor& Color,
        bool bBold = false, ETextJustify::Type Justify = ETextJustify::Left, float WrapAt = 0.f)
    {
        return SNew(STextBlock)
            .Text(MoveTemp(Text))
            .Font(FCoreStyle::GetDefaultFontStyle(bBold ? "Bold" : "Regular", Size))
            .ColorAndOpacity(Color)
            .WrapTextAt(WrapAt)
            .Justification(Justify);
    }

    TSharedRef<STextBlock> Line(const FText& Text, int32 Size, const FLinearColor& Color,
        bool bBold = false, ETextJustify::Type Justify = ETextJustify::Left, float WrapAt = 0.f)
    {
        return Line(TAttribute<FText>::CreateLambda([TextSource = &Text] { return *TextSource; }),
            Size, Color, bBold, Justify, WrapAt);
    }

    TSharedRef<STextBlock> SubtitleLine(const FText& Text, int32 Size, bool bBold)
    {
        FSlateFontInfo Font = FCoreStyle::GetDefaultFontStyle(bBold ? "Bold" : "Regular", Size);
        Font.OutlineSettings = FFontOutlineSettings(1, FLinearColor::Black);
        return SNew(STextBlock)
            .Text_Lambda([TextSource = &Text] { return *TextSource; })
            .Font(Font)
            .ColorAndOpacity(bBold ? FLinearColor::White : HudIvory)
            .ShadowOffset(FVector2D(1.f, 2.f))
            .ShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, .72f))
            .WrapTextAt(700.f)
            .Justification(ETextJustify::Center);
    }
}

void UDirectorCutPlayHUD::OnWorldBeginPlay(UWorld& World)
{
    Super::OnWorldBeginPlay(World);
    if (!World.IsGameWorld() || World.GetNetMode() == NM_DedicatedServer) return;

    MapName = FName(*UGameplayStatics::GetCurrentLevelName(&World, true));
    if (MapName == TEXT("Stage1") && World.GetOutermost()->GetName().Contains(TEXT("/DirectorCut/Stage/")))
    {
        MapName = TEXT("L_Stage1");
    }
    if (HasDirectorCutPlayHUD(MapName))
    {
        for (TActorIterator<ADirectorCutWallNote> It(&World); It; ++It)
        {
            WallNotes.Add(*It);
        }
        BuildOverlay();
    }
    if (MapName == TEXT("Stage4"))
    {
        for (TActorIterator<AStage4ShadowTheatre> It(&World); It; ++It)
        {
            FinalTheatre = *It;
            break;
        }
        for (TActorIterator<AColorSignalPuzzle> It(&World); It; ++It)
        {
            ColorConsole = *It;
            break;
        }
    }
    if (MapName == TEXT("Stage3_"))
    {
        for (TActorIterator<AFocusPropPuzzle> It(&World); It; ++It)
        {
            FocusPuzzle = *It;
            break;
        }
    }
}

TStatId UDirectorCutPlayHUD::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UDirectorCutPlayHUD, STATGROUP_Tickables);
}

void UDirectorCutPlayHUD::Deinitialize()
{
    if (IsValid(SubtitleVoice)) SubtitleVoice->Stop();
    if (UGameViewportClient* Viewport = GetWorld()->GetGameViewport(); Viewport && Overlay)
    {
        Viewport->RemoveViewportWidgetContent(Overlay.ToSharedRef());
    }
    Overlay.Reset();
    Super::Deinitialize();
}

float UDirectorCutPlayHUD::ShowSubtitle(const FText& Korean, const FText& English, float Duration)
{
    if (!Overlay) BuildOverlay();
    FString Ko = Korean.ToString(), En = English.ToString();
    FString KoSpeaker, EnSpeaker, KoLine, EnLine;
    const bool bKoSpeaker = Ko.Split(TEXT(":"), &KoSpeaker, &KoLine);
    const bool bEnSpeaker = En.Split(TEXT(":"), &EnSpeaker, &EnLine);
    SubtitleSpeaker = FText::FromString(bKoSpeaker
        ? (bEnSpeaker ? KoSpeaker.TrimStartAndEnd() + TEXT(" (") + EnSpeaker.TrimStartAndEnd() + TEXT(")") : KoSpeaker.TrimStartAndEnd())
        : TEXT("드래곤 (Dragon)"));
    SubtitleKorean = FText::FromString(bKoSpeaker ? KoLine.TrimStartAndEnd() : Ko);
    SubtitleEnglish = FText::FromString(bEnSpeaker ? EnLine.TrimStartAndEnd() : En);
    if (IsValid(SubtitleVoice)) SubtitleVoice->Stop();
    SubtitleVoice = nullptr;
    if (const TCHAR* VoicePath = FindDirectorCutVoice(En))
    {
        if (USoundBase* Sound = LoadObject<USoundBase>(nullptr, VoicePath))
        {
            Duration = FMath::Max(Duration, Sound->GetDuration() + .25f);
            SubtitleVoice = UGameplayStatics::SpawnSound2D(this, Sound);
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Missing subtitle voice: %s"), VoicePath);
        }
    }
    SubtitleRemaining = Duration;
    return Duration;
}

void UDirectorCutPlayHUD::ClearSubtitle()
{
    if (IsValid(SubtitleVoice)) SubtitleVoice->Stop();
    SubtitleVoice = nullptr;
    SubtitleRemaining = 0.f;
}

ADirectorCutWallNote* UDirectorCutPlayHUD::UpdateWallNote(const FVector& Position, bool bCanRead, bool bInteract)
{
    if (const ADirectorCutWallNote* Note = OpenWallNote.Get())
    {
        if (!bCanRead || !Note->IsInReach(Position) || bInteract) OpenWallNote.Reset();
        return nullptr;
    }
    if (!bCanRead) return nullptr;

    ADirectorCutWallNote* Nearest = nullptr;
    double NearestDistance = TNumericLimits<double>::Max();
    for (const auto& Entry : WallNotes)
    {
        ADirectorCutWallNote* Note = Entry.Get();
        if (Note && Note->IsInReach(Position))
        {
            const double Distance = FMath::Abs(Note->GetActorLocation().X - Position.X);
            if (Distance < NearestDistance)
            {
                Nearest = Note;
                NearestDistance = Distance;
            }
        }
    }
    if (Nearest && bInteract)
    {
        OpenWallNote = Nearest;
        Nearest->GetText(WallNoteKorean, WallNoteEnglish);
    }
    return Nearest;
}

void UDirectorCutPlayHUD::Tick(float DeltaTime)
{
    if (!Overlay) return;
    Super::Tick(DeltaTime);
    APlayerController* Controller = GetWorld()->GetFirstPlayerController();
    APawn* Pawn = Controller ? Controller->GetPawn() : nullptr;
    if (!Pawn || !Controller->IsLocalController())
    {
        bPromptVisible = false;
        bGuideVisible = false;
        OpenWallNote.Reset();
        return;
    }

    const auto* Director = Cast<ADirectorCutPlayerController>(Controller);
    bMenuOpen = Director ? Director->IsGraphicsMenuOpen() : IsDirectorCutWorkshopMenuOpen(MapName, *GetWorld());
    const bool bRgbActive = ColorConsole.IsValid() && ColorConsole->bUseRgbCalibration && ColorConsole->bActive;
    if (IsValid(SubtitleVoice))
    {
        SubtitleVoice->SetPaused(bMenuOpen || bRgbActive || OpenWallNote.IsValid());
    }
    if (!bMenuOpen && !bRgbActive && !OpenWallNote.IsValid())
    {
        SubtitleRemaining = FMath::Max(0.f, SubtitleRemaining - DeltaTime);
    }
    if (FinalTheatre.IsValid() && FinalTheatre->bRecovered)
    {
        RecoveryElapsed += DeltaTime;
        if (RecoveryElapsed >= 2.1f && !bEndingShown)
        {
            bEndingShown = true;
            ShowSubtitle(LOCTEXT("EndingKo", "드래곤: 이번 컷은 끝까지 찍어."),
                LOCTEXT("EndingEn", "Dragon: Keep the camera rolling to the end of this take."), 5.5f);
        }
        // Let the leg recovery and the final gameplay line finish before the cinematic.
        if (RecoveryElapsed >= 7.6f && !bEndingTravelStarted)
        {
            bEndingTravelStarted = true;
            Controller->SetIgnoreMoveInput(true);
            Controller->SetIgnoreLookInput(true);
            OpenWallNote.Reset();
            ClearSubtitle();
            if (Controller->PlayerCameraManager)
            {
                Controller->PlayerCameraManager->StartCameraFade(0.f, 1.f, .5f, FLinearColor::Black, false, true);
            }
        }
        if (RecoveryElapsed >= 8.1f)
        {
            // Clear the completion source immediately so travel can only be requested once.
            FinalTheatre.Reset();
            UGameplayStatics::OpenLevel(this, FName(TEXT("/Game/DirectorCut/Ending/L_BossEnding")));
            return;
        }
    }
    const double X = Pawn->GetActorLocation().X;
    const bool bFocusActive = FocusPuzzle.IsValid() && FocusPuzzle->bActive;
    const bool bInteract = !WallNotes.IsEmpty() && Controller->WasInputKeyJustPressed(EKeys::E);
    QueryRemaining -= DeltaTime;
    if (QueryRemaining <= 0.f || bInteract)
    {
        ActionPrompt = {};
        if (!bMenuOpen) GetDirectorCutInteractionPrompt(MapName, *Controller, ActionPrompt);
    }
    if (QueryRemaining <= 0.f)
    {
        QueryRemaining = .10f;
        if (!bMenuOpen)
        {
            Guide = GetDirectorCutPuzzleGuide(MapName, *Controller);
        }
        if (SubtitleRemaining <= 0.f && !bMenuOpen && !bRgbActive && !bFocusActive
            && !OpenWallNote.IsValid() && !bEndingShown && GetWorld()->GetTimeSeconds() >= 1.6f)
        {
            const auto Cues = GetDirectorCutStoryCues(MapName);
            for (int32 Index = 0; Index < Cues.Num(); ++Index)
            {
                const FDirectorCutStoryCue& Cue = Cues[Index];
                const bool bInCueArea = X >= Cue.MinX && X < Cue.MaxX;
                if ((bInCueArea || Index == 0) && !PlayedStoryCues.Contains(Index))
                {
                    PlayedStoryCues.Add(Index);
                    ShowSubtitle(Cue.Korean, Cue.English, Cue.Duration);
                    break;
                }
            }
        }
    }

    bGuideVisible = !bMenuOpen && !bEndingShown && !Guide.TitleKorean.IsEmpty() && !bRgbActive;
    const bool bCanRead = !bMenuOpen && !bRgbActive && !bFocusActive && !bGuideVisible && !bEndingShown
        && ActionPrompt.Key.IsEmpty() && !Controller->IsMoveInputIgnored() && Controller->GetViewTarget() == Pawn;
    const ADirectorCutWallNote* Note = UpdateWallNote(Pawn->GetActorLocation(), bCanRead, bInteract);
    bPromptVisible = false;
    if (bMenuOpen || OpenWallNote.IsValid()) return;

    if (Note)
    {
        PromptKey = LOCTEXT("ReadNoteKey", "E");
        PromptKorean = LOCTEXT("ReadNoteKo", "메모 읽기");
        PromptEnglish = LOCTEXT("ReadNoteEn", "Read note");
        PromptWorldPosition = Note->GetPromptAnchor();
    }
    else if (!ActionPrompt.Key.IsEmpty())
    {
        PromptKey = ActionPrompt.Key;
        PromptKorean = ActionPrompt.Korean;
        PromptEnglish = ActionPrompt.English;
        PromptWorldPosition = ActionPrompt.Anchor;
    }
    else
    {
        return;
    }

    UGameViewportClient* Viewport = GetWorld()->GetGameViewport();
    FVector2D Pixel;
    FVector2D ViewportPixels;
    if (Viewport && Controller->ProjectWorldLocationToScreen(PromptWorldPosition, Pixel))
    {
        Viewport->GetViewportSize(ViewportPixels);
        if (ViewportPixels.X <= 0. || ViewportPixels.Y <= 0.) return;
        const FVector2D Normalized = Pixel / ViewportPixels;
        PromptScreenPosition = FVector2D(FMath::Clamp(Normalized.X, .18, .82),
            FMath::Clamp(Normalized.Y, Note ? .20 : .46, .76));
        bPromptVisible = true;
    }
}

void UDirectorCutPlayHUD::BuildOverlay()
{
    UGameViewportClient* Viewport = GetWorld()->GetGameViewport();
    if (!Viewport) return;
    const FSlateBrush* Brush = FCoreStyle::Get().GetBrush("WhiteBrush");

    const auto MakeGuideControls = [this, Brush](int32 ColumnCount)
    {
        const TSharedRef<SVerticalBox> GuideControls = SNew(SVerticalBox);
        for (int32 Index = 0; Index < MaxGuideControls; Index += ColumnCount)
        {
            const TSharedRef<SHorizontalBox> Row = SNew(SHorizontalBox);
            for (int32 Item = Index; Item < Index + ColumnCount; ++Item)
            {
                const auto ControlText = [this, Item](auto Read)
                {
                    return TAttribute<FText>::CreateLambda([this, Item, Read]
                    {
                        return Guide.Controls.IsValidIndex(Item) ? Read(Guide.Controls[Item]) : FText::GetEmpty();
                    });
                };
                Row->AddSlot().FillWidth(1.f).Padding(Item == Index ? 0.f : 5.f, 0.f, 0.f, 0.f)
                [
                    SNew(SBox)
                    [
                        SNew(SBorder).BorderImage(Brush).BorderBackgroundColor(FLinearColor(.07f, .043f, .054f))
                        .Padding(FMargin(6.f, 4.f))
                        .Visibility_Lambda([this, Item]
                        {
                            return Guide.Controls.IsValidIndex(Item) ? EVisibility::HitTestInvisible : EVisibility::Hidden;
                        })
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0.f, 0.f, 6.f, 0.f)
                            [
                                SNew(SBorder).BorderImage(Brush).BorderBackgroundColor(HudGold).Padding(FMargin(5.f, 3.f))
                                [Line(ControlText([](const FDirectorCutGuideControl& Control) { return FText::FromString(Control.Key); }), 12, Ink, true)]
                            ]
                            + SHorizontalBox::Slot().FillWidth(1.f).VAlign(VAlign_Center)
                            [
                                SNew(SVerticalBox)
                                + SVerticalBox::Slot().AutoHeight()
                                [Line(ControlText([](const FDirectorCutGuideControl& Control) { return Control.Korean; }), 12, HudIvory, true)]
                                + SVerticalBox::Slot().AutoHeight()
                                [Line(ControlText([](const FDirectorCutGuideControl& Control) { return Control.English; }), 10, SoftIvory, false, ETextJustify::Left, 94.f)]
                            ]
                        ]
                    ]
                ];
            }
            GuideControls->AddSlot().AutoHeight().Padding(0.f, 6.f, 0.f, 0.f)
            [
                SNew(SBox)
                .Visibility_Lambda([this, Index]
                {
                    return Guide.Controls.IsValidIndex(Index) ? EVisibility::HitTestInvisible : EVisibility::Collapsed;
                })
                [Row]
            ];
        }
        return GuideControls;
    };
    const auto MakeGuideCard = [this, Viewport, Brush, &MakeGuideControls](bool bFocusLayout)
    {
        const float CardWidth = bFocusLayout ? 590.f : 360.f;
        return SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::DownOnly)
                .HAlign(HAlign_Left).VAlign(VAlign_Top)
                .Visibility_Lambda([this, bFocusLayout]
                {
                    const bool bAdjustingFocus = FocusPuzzle.IsValid() && FocusPuzzle->bActive;
                    return bGuideVisible && bAdjustingFocus == bFocusLayout ? EVisibility::HitTestInvisible : EVisibility::Collapsed;
                })
                [
                    SNew(SDPIScaler).DPIScale_Lambda([Viewport] { return ReadableScale(*Viewport, .84f); })
                    [
                        SNew(SBox).WidthOverride(CardWidth)
                        [
                            SNew(SBorder).BorderImage(Brush).BorderBackgroundColor(HudBrass).Padding(FMargin(3.f, 1.f, 1.f, 1.f))
                            [
                                SNew(SBorder).BorderImage(Brush).BorderBackgroundColor(HudPanelColor).Padding(FMargin(12.f, 9.f))
                                [
                                    SNew(SVerticalBox)
                                    + SVerticalBox::Slot().AutoHeight()[Line(Guide.TitleKorean, 20, HudGold, true)]
                                    + SVerticalBox::Slot().AutoHeight()[Line(Guide.TitleEnglish, 12, SoftIvory, true)]
                                    + SVerticalBox::Slot().AutoHeight()[MakeGuideControls(bFocusLayout ? 3 : 2)]
                                ]
                            ]
                        ]
                    ]
                ];
    };

    Overlay = SNew(SOverlay).Visibility(EVisibility::HitTestInvisible)
        + SOverlay::Slot()
        [
            SNew(SConstraintCanvas)
            + SConstraintCanvas::Slot()
            .Anchors(FAnchors(0.f, 0.f, .45f, .56f)).Offset(FMargin(18.f, 18.f, 0.f, 0.f))
            [MakeGuideCard(false)]
            + SConstraintCanvas::Slot()
            .Anchors(FAnchors(0.f, 0.f, .64f, .34f)).Offset(FMargin(18.f, 18.f, 0.f, 0.f))
            [MakeGuideCard(true)]
            + SConstraintCanvas::Slot().AutoSize(true).Alignment(FVector2D(.5, 1.))
            .Anchors_Lambda([this] { return FAnchors(PromptScreenPosition.X, PromptScreenPosition.Y); })
            .Offset(FMargin(0.f))
            [
                SNew(SDPIScaler).DPIScale_Lambda([Viewport] { return ReadableScale(*Viewport, .69f); })
                .Visibility_Lambda([this] { return bPromptVisible ? EVisibility::HitTestInvisible : EVisibility::Collapsed; })
                [
                    SNew(SBorder).BorderImage(Brush).BorderBackgroundColor(HudPanelColor).Padding(FMargin(8.f, 6.f, 12.f, 6.f))
                    [
                        SNew(SHorizontalBox)
                        + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0.f, 0.f, 9.f, 0.f)
                        [
                            SNew(SBorder).BorderImage(Brush).BorderBackgroundColor(HudGold).Padding(FMargin(9.f, 5.f))
                            [Line(PromptKey, 21, Ink, true)]
                        ]
                        + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)
                        [
                            SNew(SVerticalBox)
                            + SVerticalBox::Slot().AutoHeight()[Line(PromptKorean, 17, HudIvory, true)]
                            + SVerticalBox::Slot().AutoHeight()[Line(PromptEnglish, 13, SoftIvory)]
                        ]
                    ]
                ]
            ]
        ]
        + SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center).Padding(20.f, 10.f)
        [
            SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::DownOnly)
            .HAlign(HAlign_Center).VAlign(VAlign_Center)
            .Visibility_Lambda([this]
            {
                return OpenWallNote.IsValid() && !bMenuOpen ? EVisibility::HitTestInvisible : EVisibility::Collapsed;
            })
            [
                SNew(SDPIScaler).DPIScale_Lambda([Viewport] { return ReadableScale(*Viewport, .85f); })
                [
                    SNew(SBox).WidthOverride(565.f)
                    [
                        SNew(SBorder).BorderImage(Brush).BorderBackgroundColor(HudBrass).Padding(3.f)
                        [
                            SNew(SBorder).BorderImage(Brush).BorderBackgroundColor(Parchment).Padding(FMargin(27.f, 20.f))
                            [
                                SNew(SVerticalBox)
                                + SVerticalBox::Slot().AutoHeight()
                                [Line(TAttribute<FText>(LOCTEXT("WallNoteTitle", "작업 메모  /  PRODUCTION NOTE")), 16, Ink, true)]
                                + SVerticalBox::Slot().AutoHeight().Padding(0.f, 10.f, 0.f, 14.f)
                                [SNew(SBox).HeightOverride(1.f)[SNew(SBorder).BorderImage(Brush).BorderBackgroundColor(HudBrass)]]
                                + SVerticalBox::Slot().AutoHeight()
                                [Line(WallNoteKorean, 23, Ink, true, ETextJustify::Left, 500.f)]
                                + SVerticalBox::Slot().AutoHeight().Padding(0.f, 9.f, 0.f, 0.f)
                                [Line(WallNoteEnglish, 17, Ink, false, ETextJustify::Left, 500.f)]
                                + SVerticalBox::Slot().AutoHeight().Padding(0.f, 17.f, 0.f, 0.f)
                                [Line(TAttribute<FText>(LOCTEXT("CloseWallNote", "E   닫기 / Close")), 14, Ink, true)]
                            ]
                        ]
                    ]
                ]
            ]
        ];
    auto GameplaySubtitleLine = [](const FText& Text, int32 Size, FLinearColor Color)
    {
        return SNew(STextBlock).Text_Lambda([Source = &Text] { return *Source; })
            .Font(FCoreStyle::GetDefaultFontStyle("Regular", Size)).ColorAndOpacity(Color)
            .AutoWrapText(false).Justification(ETextJustify::Center);
    };
    Overlay->AddSlot().HAlign(HAlign_Fill).VAlign(VAlign_Top).Padding(70, 55, 70, 0)
    [
        SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::DownOnly)
        .Visibility_Lambda([this] { return !bMenuOpen && !OpenWallNote.IsValid() && SubtitleRemaining > 0.f ? EVisibility::HitTestInvisible : EVisibility::Collapsed; })
        [
            SNew(SBox).MinDesiredWidth(1350)
            [
                SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                .BorderBackgroundColor(FLinearColor(.005f,.01f,.018f,.85f)).Padding(FMargin(36,12))
                [
                    SNew(SVerticalBox)
                    + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,6)
                    [SNew(STextBlock).Text_Lambda([this] { return SubtitleSpeaker; })
                        .Font(FCoreStyle::GetDefaultFontStyle("Regular",20)).ColorAndOpacity(FLinearColor(.92f,.71f,.35f)).Justification(ETextJustify::Center)]
                    + SVerticalBox::Slot().AutoHeight()[GameplaySubtitleLine(SubtitleKorean,30,FLinearColor(.95f,.94f,.87f))]
                    + SVerticalBox::Slot().AutoHeight().Padding(0,5,0,0)[GameplaySubtitleLine(SubtitleEnglish,23,FLinearColor(.82f,.85f,.88f))]
                ]
            ]
        ]
    ];
    Viewport->AddViewportWidgetContent(Overlay.ToSharedRef(), 65);
}

#undef LOCTEXT_NAMESPACE
