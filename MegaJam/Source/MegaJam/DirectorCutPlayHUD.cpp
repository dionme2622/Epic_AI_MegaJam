#include "DirectorCutPlayHUD.h"

#include "DirectorCutGraphics.h"
#include "DirectorCutInteractionData.h"
#include "DirectorCutStoryData.h"
#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Stage4ShadowTheatre.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SConstraintCanvas.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"

#define LOCTEXT_NAMESPACE "DirectorCutPlayHUD"

namespace
{
    const FLinearColor PanelColor(.015f, .012f, .02f, .88f);
    const FLinearColor Gold(.97f, .74f, .36f);
    const FLinearColor Ivory(.96f, .94f, .89f);

    TSharedRef<STextBlock> Line(const FText& Text, int32 Size, const FLinearColor& Color,
        bool bBold = false, ETextJustify::Type Justify = ETextJustify::Left, float WrapAt = 0.f)
    {
        return SNew(STextBlock)
            .Text_Lambda([TextSource = &Text] { return *TextSource; })
            .Font(FCoreStyle::GetDefaultFontStyle(bBold ? "Bold" : "Regular", Size))
            .ColorAndOpacity(Color)
            .WrapTextAt(WrapAt)
            .Justification(Justify);
    }
}

void UDirectorCutPlayHUD::OnWorldBeginPlay(UWorld& World)
{
    Super::OnWorldBeginPlay(World);
    if (!World.IsGameWorld() || World.GetNetMode() == NM_DedicatedServer) return;

    MapName = FName(*UGameplayStatics::GetCurrentLevelName(&World, true));
    if (!GetDirectorCutStoryCues(MapName).IsEmpty() || !GetDirectorCutAreaHints(MapName).IsEmpty())
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
        return;
    }

    const auto* Director = Cast<ADirectorCutPlayerController>(Controller);
    bMenuOpen = Director ? Director->IsGraphicsMenuOpen() : Controller->IsMoveInputIgnored();
    if (!bMenuOpen)
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
        HintKorean = FText::GetEmpty();
        HintEnglish = FText::GetEmpty();
        for (const FDirectorCutAreaHint& Hint : GetDirectorCutAreaHints(MapName))
        {
            if (X >= Hint.MinX && X < Hint.MaxX)
            {
                HintKorean = Hint.Korean;
                HintEnglish = Hint.English;
                break;
            }
        }

        if (SubtitleRemaining <= 0.f && !bMenuOpen && !bEndingShown && GetWorld()->GetTimeSeconds() >= 1.6f)
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
        PromptScreenPosition = FVector2D(FMath::Clamp(Normalized.X, .15, .85),
            FMath::Clamp(Normalized.Y, .18, .72));
        bPromptVisible = true;
    }
}

void UDirectorCutPlayHUD::BuildOverlay()
{
    UGameViewportClient* Viewport = GetWorld()->GetGameViewport();
    if (!Viewport) return;
    const FSlateBrush* Brush = FCoreStyle::Get().GetBrush("WhiteBrush");
    Overlay = SNew(SOverlay).Visibility(EVisibility::HitTestInvisible)
        + SOverlay::Slot()
        [
            SNew(SConstraintCanvas)
            + SConstraintCanvas::Slot().AutoSize(true).Alignment(FVector2D(.5, 1.))
            .Anchors_Lambda([this] { return FAnchors(PromptScreenPosition.X, PromptScreenPosition.Y); })
            .Offset(FMargin(0.f))
            [
                SNew(SBorder).BorderImage(Brush).BorderBackgroundColor(PanelColor).Padding(FMargin(8.f, 6.f, 12.f, 6.f))
                .Visibility_Lambda([this] { return bPromptVisible ? EVisibility::HitTestInvisible : EVisibility::Collapsed; })
                [
                    SNew(SHorizontalBox)
                    + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0.f, 0.f, 9.f, 0.f)
                    [
                        SNew(SBorder).BorderImage(Brush).BorderBackgroundColor(Gold).Padding(FMargin(9.f, 5.f))
                        [Line(PromptKey, 20, FLinearColor(.06f, .035f, .013f), true)]
                    ]
                    + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)
                    [
                        SNew(SVerticalBox)
                        + SVerticalBox::Slot().AutoHeight()[Line(PromptKorean, 16, Ivory, true)]
                        + SVerticalBox::Slot().AutoHeight()[Line(PromptEnglish, 12, Ivory)]
                    ]
                ]
            ]
        ]
        + SOverlay::Slot().HAlign(HAlign_Left).VAlign(VAlign_Bottom).Padding(24.f, 0.f, 24.f, 123.f)
        [
            SNew(SBorder).BorderImage(Brush).BorderBackgroundColor(PanelColor).Padding(FMargin(13.f, 8.f))
            .Visibility_Lambda([this]
            {
                return !bMenuOpen && !bEndingShown && !HintKorean.IsEmpty() && SubtitleRemaining <= 0.f
                    ? EVisibility::HitTestInvisible : EVisibility::Collapsed;
            })
            [
                SNew(SVerticalBox)
                + SVerticalBox::Slot().AutoHeight()[Line(HintKorean, 16, Gold, true, ETextJustify::Left, 550.f)]
                + SVerticalBox::Slot().AutoHeight().Padding(0.f, 3.f, 0.f, 0.f)[Line(HintEnglish, 13, Ivory, false, ETextJustify::Left, 550.f)]
            ]
        ]
        + SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Bottom).Padding(20.f, 0.f, 20.f, 54.f)
        [
            SNew(SBorder).BorderImage(Brush).BorderBackgroundColor(PanelColor).Padding(FMargin(24.f, 12.f))
            .Visibility_Lambda([this]
            {
                return !bMenuOpen && SubtitleRemaining > 0.f ? EVisibility::HitTestInvisible : EVisibility::Collapsed;
            })
            [
                SNew(SVerticalBox)
                + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)[Line(SubtitleKorean, 24, FLinearColor::White, true, ETextJustify::Center, 650.f)]
                + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0.f, 4.f, 0.f, 0.f)[Line(SubtitleEnglish, 18, Ivory, false, ETextJustify::Center, 650.f)]
            ]
        ];
    Viewport->AddViewportWidgetContent(Overlay.ToSharedRef(), 65);
}

#undef LOCTEXT_NAMESPACE
