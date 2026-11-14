#include "DirectorCutPlayHUD.h"

#include "ColorSignalPuzzle.h"
#include "DirectorCutGraphics.h"
#include "DirectorCutInteractionData.h"
#include "DirectorCutStoryData.h"
#include "Engine/GameViewportClient.h"
#include "Engine/UserInterfaceSettings.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "FocusPropPuzzle.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
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
    if (HasDirectorCutPuzzleGuides(MapName))
    {
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
    if (UGameViewportClient* Viewport = GetWorld()->GetGameViewport(); Viewport && Overlay)
    {
        Viewport->RemoveViewportWidgetContent(Overlay.ToSharedRef());
    }
    Overlay.Reset();
    Super::Deinitialize();
}

void UDirectorCutPlayHUD::ShowSubtitle(const FText& Korean, const FText& English, float Duration)
{
    if (!Overlay) BuildOverlay();
    SubtitleKorean = Korean;
    SubtitleEnglish = English;
    SubtitleRemaining = Duration;
}

void UDirectorCutPlayHUD::ClearSubtitle()
{
    SubtitleRemaining = 0.f;
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
        return;
    }

    const auto* Director = Cast<ADirectorCutPlayerController>(Controller);
    bMenuOpen = Director ? Director->IsGraphicsMenuOpen() : IsDirectorCutWorkshopMenuOpen(MapName, *GetWorld());
    const bool bRgbActive = ColorConsole.IsValid() && ColorConsole->bUseRgbCalibration && ColorConsole->bActive;
    if (!bMenuOpen && !bRgbActive)
    {
        SubtitleRemaining = FMath::Max(0.f, SubtitleRemaining - DeltaTime);
    }
    if (FinalTheatre.IsValid() && FinalTheatre->bRecovered && !bEndingShown)
    {
        RecoveryElapsed += DeltaTime;
        if (RecoveryElapsed >= 2.1f)
        {
            bEndingShown = true;
            ShowSubtitle(LOCTEXT("EndingKo", "용: 이번 컷은 끝까지 찍어."),
                LOCTEXT("EndingEn", "Dragon: Keep the camera rolling to the end of this take."), 5.5f);
        }
    }
    const double X = Pawn->GetActorLocation().X;
    QueryRemaining -= DeltaTime;
    if (QueryRemaining <= 0.f)
    {
        QueryRemaining = .10f;
        FDirectorCutInteractionPrompt Prompt;
        bHasPrompt = !bMenuOpen && GetDirectorCutInteractionPrompt(MapName, *Controller, Prompt);
        if (bHasPrompt)
        {
            PromptKey = Prompt.Key;
            PromptKorean = Prompt.Korean;
            PromptEnglish = Prompt.English;
            PromptWorldPosition = Prompt.Anchor;
        }
        if (!bMenuOpen)
        {
            Guide = GetDirectorCutPuzzleGuide(MapName, *Controller);
        }

        if (SubtitleRemaining <= 0.f && !bMenuOpen && !bRgbActive && !bEndingShown && GetWorld()->GetTimeSeconds() >= 1.6f)
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
    bPromptVisible = false;
    if (!bHasPrompt || bMenuOpen) return;

    UGameViewportClient* Viewport = GetWorld()->GetGameViewport();
    FVector2D Pixel;
    FVector2D ViewportPixels;
    if (Viewport && Controller->ProjectWorldLocationToScreen(PromptWorldPosition, Pixel))
    {
        Viewport->GetViewportSize(ViewportPixels);
        if (ViewportPixels.X <= 0. || ViewportPixels.Y <= 0.) return;
        const FVector2D Normalized = Pixel / ViewportPixels;
        PromptScreenPosition = FVector2D(FMath::Clamp(Normalized.X, .18, .82),
            FMath::Clamp(Normalized.Y, .46, .76));
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
                                    + SVerticalBox::Slot().AutoHeight().Padding(0.f, 7.f, 0.f, 7.f)
                                    [SNew(SBox).HeightOverride(1.f)[SNew(SBorder).BorderImage(Brush).BorderBackgroundColor(HudBrass)]]
                                    + SVerticalBox::Slot().AutoHeight()
                                    [Line(Guide.Korean, 16, HudIvory, true, ETextJustify::Left, CardWidth - 30.f)]
                                    + SVerticalBox::Slot().AutoHeight().Padding(0.f, 3.f, 0.f, 0.f)
                                    [Line(Guide.English, 13, SoftIvory, false, ETextJustify::Left, CardWidth - 30.f)]
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
        + SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Bottom).Padding(20.f, 0.f, 20.f, 84.f)
        [
            SNew(SBorder).BorderImage(Brush).BorderBackgroundColor(HudPanelColor).Padding(FMargin(24.f, 12.f))
            .Visibility_Lambda([this]
            {
                return !bMenuOpen && SubtitleRemaining > 0.f
                    && !(ColorConsole.IsValid() && ColorConsole->bUseRgbCalibration && ColorConsole->bActive)
                    ? EVisibility::HitTestInvisible : EVisibility::Collapsed;
            })
            [
                SNew(SVerticalBox)
                + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)[Line(SubtitleKorean, 24, FLinearColor::White, true, ETextJustify::Center, 650.f)]
                + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0.f, 4.f, 0.f, 0.f)[Line(SubtitleEnglish, 18, HudIvory, false, ETextJustify::Center, 650.f)]
            ]
        ];
    Viewport->AddViewportWidgetContent(Overlay.ToSharedRef(), 65);
}

#undef LOCTEXT_NAMESPACE
