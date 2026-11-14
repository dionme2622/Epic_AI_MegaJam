#include "DirectorCutGraphics.h"
#include "DirectorCutInteractionData.h"
#include "DirectorCutTest.h"
#include "Components/InputComponent.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/Texture2D.h"
#include "Widgets/Images/SImage.h"
#include "Widgets/Layout/SScaleBox.h"

#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "UObject/ConstructorHelpers.h"
#include "Widgets/SViewport.h"
#include "HAL/IConsoleManager.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"

#define LOCTEXT_NAMESPACE "DirectorCutGraphics"

namespace
{
    using EOption = EDirectorCutGraphicsOption;
    const FName GraphicsTag("DirectorCutGraphics");
    const FLinearColor PanelColor(.023f, .033f, .048f, .96f);
    const FLinearColor TextColor(.91f, .91f, .85f);
    const FLinearColor AccentColor(.94f, .71f, .34f);

    void SetRenderingValue(const TCHAR* Name, float Value)
    {
        if (IConsoleVariable* Variable = IConsoleManager::Get().FindConsoleVariable(Name))
        {
            Variable->Set(Value, ECVF_SetByGameOverride, GraphicsTag);
        }
    }

    TSharedRef<STextBlock> Label(FText Text, int32 Size, FLinearColor Color = TextColor)
    {
        return SNew(STextBlock).Text(Text)
            .Font(FCoreStyle::GetDefaultFontStyle("Regular", Size)).ColorAndOpacity(Color);
    }
}

bool UDirectorCutGraphicsSubsystem::IsHigh(EOption Option) const
{
    switch (Option)
    {
        case EOption::ModelDetail: return bModelHigh;
        case EOption::Resolution: return bResolutionHigh;
        case EOption::Shadows: return bShadowsHigh;
    }
    return true;
}

void UDirectorCutGraphicsSubsystem::SetHigh(EOption Option, bool bHigh)
{
    if (!CanSet(Option) || IsHigh(Option) == bHigh)
    {
        return;
    }
    switch (Option)
    {
        case EOption::ModelDetail:
            bModelHigh = bHigh;
            break;
        case EOption::Resolution:
            bResolutionHigh = bHigh;
            break;
        case EOption::Shadows:
            bShadowsHigh = bHigh;
            break;
        default:
            return;
    }
    Apply(Option);
    OnGraphicsChanged.Broadcast(Option, bHigh);
}

bool UDirectorCutGraphicsSubsystem::CanSet(EOption Option) const
{
    return Option != EOption::ModelDetail || CanChangeDirectorCutWorkshopDetail(*GetWorld());
}

void UDirectorCutGraphicsSubsystem::OnWorldBeginPlay(UWorld& InWorld)
{
    Super::OnWorldBeginPlay(InWorld);
    if (InWorld.IsGameWorld() && InWorld.GetNetMode() != NM_DedicatedServer)
    {
        Apply(EOption::ModelDetail);
        Apply(EOption::Resolution);
        Apply(EOption::Shadows);
    }
}

void UDirectorCutGraphicsSubsystem::Deinitialize()
{
    if (GetWorld() && GetWorld()->IsGameWorld() && GetWorld()->GetNetMode() != NM_DedicatedServer)
    {
        IConsoleManager::Get().UnsetAllConsoleVariablesWithTag(GraphicsTag, ECVF_SetByGameOverride);
    }
    Super::Deinitialize();
}

void UDirectorCutGraphicsSubsystem::Apply(EOption Option) const
{
    const bool bHigh = IsHigh(Option);
    switch (Option)
    {
        case EOption::ModelDetail:
        {
            ApplyDirectorCutWorkshopDetail(*GetWorld(), bHigh);
            if (const auto* Mode = GetWorld()->GetAuthGameMode<ADirectorCutTestMode>())
            {
                Mode->ApplyModelDetail(bHigh);
            }
            break;
        }
        case EOption::Resolution:
            SetRenderingValue(TEXT("r.Editor.Viewport.OverridePIEScreenPercentage"), 0.f);
            SetRenderingValue(TEXT("r.ScreenPercentage"), bHigh ? 100.f : 40.f);
            break;
        case EOption::Shadows:
            SetRenderingValue(TEXT("r.ShadowQuality"), bHigh ? 5.f : 0.f);
            break;
    }
}

ADirectorCutPlayerController::ADirectorCutPlayerController()
{
    static ConstructorHelpers::FObjectFinder<UTexture2D> Stone(
        TEXT("/Game/DirectorCut/Environment/T_Castle_Wall_BaseColor.T_Castle_Wall_BaseColor"));
    SettingsPanelTexture = Stone.Object;
}

void ADirectorCutPlayerController::SetupInputComponent()
{
    Super::SetupInputComponent();
    bWorkshop = UGameplayStatics::GetCurrentLevelName(this, true) == TEXT("Stage2")
        && GetWorld()->GetOutermost()->GetName().Contains(TEXT("/DirectorCut/Stage/"));
    if (bWorkshop && InputComponent)
    {
        InputComponent->BindKey(EKeys::Escape, IE_Pressed, this, &ADirectorCutPlayerController::ToggleMenu);
        InputComponent->BindKey(EKeys::M, IE_Pressed, this, &ADirectorCutPlayerController::ToggleMenu);
        InputComponent->BindKey(EKeys::One, IE_Pressed, this, &ADirectorCutPlayerController::SelectLowModelDetail);
        InputComponent->BindKey(EKeys::Two, IE_Pressed, this, &ADirectorCutPlayerController::SelectHighModelDetail);
        InputComponent->BindKey(EKeys::Three, IE_Pressed, this, &ADirectorCutPlayerController::ToggleShadows);
    }
}

void ADirectorCutPlayerController::BeginPlay()
{
    Super::BeginPlay();
    if (!IsLocalController())
    {
        return;
    }
    UGameViewportClient* Viewport = GetWorld()->GetGameViewport();
    if (!Viewport)
    {
        return;
    }

    StoneBrush.SetResourceObject(SettingsPanelTexture);
    StoneBrush.DrawAs = ESlateBrushDrawType::Image;
    StoneBrush.ImageSize = FVector2f(760.f, 510.f);

    auto MakeChoice = [this](EOption Option, bool bHigh)
    {
        const FText Text = bHigh ? LOCTEXT("High", "높음") : LOCTEXT("Low", "낮음");
        return SNew(SButton)
            .HAlign(HAlign_Center)
            .IsEnabled_Lambda([this, Option] { return GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>()->CanSet(Option); })
            .ContentPadding(FMargin(25.f, 14.f))
            .ButtonColorAndOpacity_Lambda([this, Option, bHigh]
            {
                const bool bSelected = GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>()->IsHigh(Option) == bHigh;
                return bSelected ? FLinearColor(.57f,.36f,.12f) : FLinearColor(.16f,.21f,.27f);
            })
            .OnClicked_Lambda([this, Option, bHigh]
            {
                GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>()->SetHigh(Option, bHigh);
                return FReply::Handled();
            })
            [Label(Text, 23)];
    };
    auto MakeRow = [&MakeChoice](EOption Option, FText Text)
    {
        return SNew(SHorizontalBox)
            + SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)[Label(Text, 27)]
            + SHorizontalBox::Slot().AutoWidth().Padding(10,0)[MakeChoice(Option, false)]
            + SHorizontalBox::Slot().AutoWidth()[MakeChoice(Option, true)];
    };

    SettingsOverlay = SNew(SOverlay).Visibility(EVisibility::SelfHitTestInvisible)
        + SOverlay::Slot().HAlign(HAlign_Fill).VAlign(VAlign_Fill)
        [
            SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
            .BorderBackgroundColor(FLinearColor(.006f, .012f, .022f, .53f))
            .Visibility_Lambda([this] { return bMenuOpen ? EVisibility::Visible : EVisibility::Collapsed; })
            .Padding(FMargin(22, 56, 22, 22))
            [
                SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::Both)
                [
                    SNew(SBox).WidthOverride(760).HeightOverride(490)
                    [
                        SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                        .BorderBackgroundColor(FLinearColor(.39f,.29f,.15f)).Padding(3)
                        [
                            SNew(SOverlay)
                            + SOverlay::Slot()
                            [
                                SNew(SImage).Image(&StoneBrush).ColorAndOpacity(FLinearColor(.68f,.77f,.92f))
                                .Visibility(EVisibility::HitTestInvisible)
                            ]
                            + SOverlay::Slot()
                            [
                                SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                                .BorderBackgroundColor(FLinearColor(.025f,.039f,.059f,.82f)).Padding(FMargin(37, 27))
                                [
                                    SNew(SVerticalBox)
                                    + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,bWorkshop ? 5 : 25)
                                        [Label(LOCTEXT("Title", "그래픽 설정"), 38, AccentColor)]
                                    + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,bWorkshop ? 14 : 0)
                                    [
                                        SNew(SBox).Visibility(bWorkshop ? EVisibility::HitTestInvisible : EVisibility::Collapsed)
                                        [Label(LOCTEXT("WorkshopKeys", "1 낮음   2 높음   3 그림자 전환   Esc / M 닫기"), 17)]
                                    ]
                                    + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,15)
                                        [MakeRow(EOption::ModelDetail, LOCTEXT("Model", "모델 디테일"))]
                                    + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,15)
                                        [MakeRow(EOption::Resolution, LOCTEXT("Resolution", "해상도"))]
                                    + SVerticalBox::Slot().AutoHeight()
                                        [MakeRow(EOption::Shadows, LOCTEXT("Shadows", "그림자"))]
                                    + SVerticalBox::Slot().FillHeight(1).HAlign(HAlign_Right).VAlign(VAlign_Bottom)
                                    [
                                        SNew(SButton).ContentPadding(FMargin(26,12))
                                        .ButtonColorAndOpacity(FLinearColor(.39f,.27f,.12f))
                                        .OnClicked_Lambda([this] { SetMenuOpen(false); return FReply::Handled(); })
                                        [Label(LOCTEXT("Close", "닫기"), 22)]
                                    ]
                                ]
                            ]
                        ]
                    ]
                ]
            ]
        ]
        + SOverlay::Slot().HAlign(HAlign_Right).VAlign(VAlign_Top).Padding(0, 18, 18, 0)
        [
            SNew(SButton).HAlign(HAlign_Center).ContentPadding(FMargin(15, 8))
            .ToolTipText(LOCTEXT("SettingsTooltip", "그래픽 설정"))
            .ButtonColorAndOpacity(PanelColor)
            .OnClicked_Lambda([this] { ToggleMenu(); return FReply::Handled(); })
            [Label(FText::FromString(TEXT("\u2699")), 27, AccentColor)]
        ];
    Viewport->AddViewportWidgetContent(SettingsOverlay.ToSharedRef(), 10);
    SetMenuOpen(false);
}

void ADirectorCutPlayerController::SetMenuOpen(bool bOpen)
{
    if (bMenuOpen != bOpen)
    {
        SetIgnoreMoveInput(bOpen);
    }
    bMenuOpen = bOpen;
    if (bWorkshop)
    {
        SetDirectorCutWorkshopMenuOpen(*GetWorld(), bOpen);
    }
    bShowMouseCursor = true;
    FInputModeGameAndUI Mode;
    Mode.SetHideCursorDuringCapture(false);
    Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
    if (!bOpen)
    {
        Mode.SetWidgetToFocus(GetWorld()->GetGameViewport()->GetGameViewportWidget());
    }
    SetInputMode(Mode);
}

void ADirectorCutPlayerController::ToggleMenu()
{
    SetMenuOpen(!bMenuOpen);
}

void ADirectorCutPlayerController::SelectLowModelDetail()
{
    if (bMenuOpen) GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>()->SetHigh(EOption::ModelDetail, false);
}

void ADirectorCutPlayerController::SelectHighModelDetail()
{
    if (bMenuOpen) GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>()->SetHigh(EOption::ModelDetail, true);
}

void ADirectorCutPlayerController::ToggleShadows()
{
    if (bMenuOpen)
    {
        auto* Graphics = GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>();
        Graphics->SetHigh(EOption::Shadows, !Graphics->IsHigh(EOption::Shadows));
    }
}

void ADirectorCutPlayerController::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (SettingsOverlay.IsValid())
    {
        if (UGameViewportClient* Viewport = GetWorld()->GetGameViewport())
        {
            Viewport->RemoveViewportWidgetContent(SettingsOverlay.ToSharedRef());
        }
        SettingsOverlay.Reset();
    }
    Super::EndPlay(EndPlayReason);
}

#undef LOCTEXT_NAMESPACE





