#include "DirectorCutLobby.h"

#include "Camera/CameraActor.h"
#include "Engine/GameViewportClient.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Styling/CoreStyle.h"
#include "Styling/SlateTypes.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SScaleBox.h"
#include "Widgets/Images/SImage.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/Texture2D.h"
#include "Sound/SoundBase.h"
#include "Components/AudioComponent.h"
#include "TimerManager.h"
#include "Widgets/Layout/SSpacer.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"

#define LOCTEXT_NAMESPACE "DirectorCutLobby"

namespace
{
const FLinearColor Gold(0.82f, 0.55f, 0.25f);
const FLinearColor Ivory(0.97f, 0.87f, 0.71f);
const FLinearColor Muted(0.75f, 0.68f, 0.71f);

FSlateRoundedBoxBrush NormalButton(FLinearColor(0.105f, 0.025f, 0.055f, 0.95f), 5.f, FLinearColor(0.44f, 0.26f, 0.12f), 1.f);
FSlateRoundedBoxBrush HoverButton(FLinearColor(0.21f, 0.058f, 0.10f), 5.f, Gold, 1.f);
FSlateRoundedBoxBrush PressButton(FLinearColor(0.31f, 0.12f, 0.105f), 5.f, Ivory, 2.f);
FSlateRoundedBoxBrush SecondaryButton(FLinearColor(0.03f, 0.014f, 0.032f, 0.86f), 5.f, FLinearColor(0.27f, 0.17f, 0.15f), 1.f);
FSlateColorBrush RuleBrush(FLinearColor(0.56f, 0.34f, 0.16f, 0.94f));

const FButtonStyle& GetLobbyButtonStyle(bool bPrimary)
{
    static const FButtonStyle Primary = FButtonStyle()
        .SetNormal(NormalButton).SetHovered(HoverButton).SetPressed(PressButton);
    static const FButtonStyle Secondary = FButtonStyle()
        .SetNormal(SecondaryButton).SetHovered(HoverButton).SetPressed(PressButton);
    return bPrimary ? Primary : Secondary;
}

FSlateFontInfo Font(int32 Size, const TCHAR* Typeface)
{
    return FCoreStyle::GetDefaultFontStyle(Typeface, Size);
}

TSharedRef<SWidget> Rule(float Width)
{
    return SNew(SBox).WidthOverride(Width).HeightOverride(2.f)
    [
        SNew(SBorder).BorderImage(&RuleBrush).Padding(0.f).Visibility(EVisibility::HitTestInvisible)
    ];
}

TSharedRef<SButton> Button(const FText& Label, const FText& Marker, bool bPrimary, FOnClicked Click)
{
    return SNew(SButton)
        .ButtonStyle(&GetLobbyButtonStyle(bPrimary))
        .OnClicked(Click)
        .ContentPadding(FMargin(17.f, 9.f))
        .HAlign(HAlign_Fill)
        .VAlign(VAlign_Center)
        [
            SNew(SHorizontalBox)
            + SHorizontalBox::Slot().FillWidth(1.f).VAlign(VAlign_Center)
            [
                SNew(STextBlock).Text(Label).Font(Font(19, TEXT("Bold"))).ColorAndOpacity(Ivory)
            ]
            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)
            [
                SNew(STextBlock).Text(Marker).Font(Font(15, TEXT("Bold"))).ColorAndOpacity(Gold)
            ]
        ];
}
}

ADirectorCutLobbyMode::ADirectorCutLobbyMode()
{
    DefaultPawnClass = nullptr;
    PlayerControllerClass = ADirectorCutLobbyController::StaticClass();
}

ADirectorCutLobbyController::ADirectorCutLobbyController()
{
    static ConstructorHelpers::FObjectFinder<UTexture2D> KeyArt(
        TEXT("/Game/DirectorCut/Lobby/T_Lobby_KeyArt.T_Lobby_KeyArt"));
    LobbyKeyArt = KeyArt.Object;
    static ConstructorHelpers::FObjectFinder<USoundBase> Music(
        TEXT("/Game/DirectorCut/Audio/S_Gameplay_ProcessingPower.S_Gameplay_ProcessingPower"));
    static ConstructorHelpers::FObjectFinder<USoundBase> Click(
        TEXT("/Game/DirectorCut/Ending/SFX/S_UI_Select.S_UI_Select"));
    LobbyMusic = Music.Object;
    ButtonClickSound = Click.Object;
}

void ADirectorCutLobbyController::BeginPlay()
{
    Super::BeginPlay();
    UGameViewportClient* Viewport = GetWorld()->GetGameViewport();
    if (!IsLocalController() || !Viewport)
    {
        return;
    }

    for (TActorIterator<ACameraActor> Camera(GetWorld()); Camera; ++Camera)
    {
        if (Camera->ActorHasTag(TEXT("LobbyCamera")))
        {
            SetViewTarget(*Camera);
            break;
        }
    }

    if (LobbyMusic) LobbyMusicComponent = UGameplayStatics::SpawnSound2D(this, LobbyMusic, .40f);

    const TSharedRef<SButton> Start = Button(LOCTEXT("Start", "Start Game"), FText::FromString(TEXT(">")), true,
        FOnClicked::CreateWeakLambda(this, [this]
        {
            StartLobbyAction(false);
            return FReply::Handled();
        }));
    const TSharedRef<SButton> Quit = Button(LOCTEXT("Quit", "Quit"), FText::GetEmpty(), false,
        FOnClicked::CreateWeakLambda(this, [this]
        {
            StartLobbyAction(true);
            return FReply::Handled();
        }));

    LobbyArtBrush.SetResourceObject(LobbyKeyArt);
    LobbyArtBrush.ImageSize = FVector2D(1280.f, 720.f);
    LobbyArtBrush.DrawAs = ESlateBrushDrawType::Image;

    Lobby = SNew(SScaleBox)
        .Stretch(EStretch::ScaleToFit)
        [
            SNew(SBox).WidthOverride(1280.f).HeightOverride(720.f)
            [
                SNew(SOverlay)
                + SOverlay::Slot()
                [
                    SNew(SImage).Image(&LobbyArtBrush).Visibility(EVisibility::HitTestInvisible)
                ]
                + SOverlay::Slot().HAlign(HAlign_Left).VAlign(VAlign_Center).Padding(FMargin(82.f, 0.f, 0.f, 0.f))
                [
                    SNew(SBox).WidthOverride(377.f)
                    [
                        SNew(SVerticalBox)
                        + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Left).Padding(0.f, 0.f, 0.f, 18.f)
                        [
                            Rule(88.f)
                        ]
                        + SVerticalBox::Slot().AutoHeight()
                        [
                            SNew(STextBlock).Text(LOCTEXT("TitleDirector", "DIRECTOR’S"))
                            .Font(Font(45, TEXT("Bold"))).ColorAndOpacity(Ivory)
                        ]
                        + SVerticalBox::Slot().AutoHeight()
                        [
                            SNew(STextBlock).Text(LOCTEXT("TitleCut", "CUT"))
                            .Font(Font(86, TEXT("Bold"))).ColorAndOpacity(Gold)
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0.f, 10.f, 0.f, 28.f)
                        [
                            SNew(STextBlock).Text(LOCTEXT("Tagline", "Beyond the frame lay an unfinished world."))
                            .Font(Font(15, TEXT("Regular"))).ColorAndOpacity(Muted).AutoWrapText(true)
                        ]
                        + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Left).Padding(0.f, 0.f, 0.f, 9.f)
                        [
                            SNew(SBox).WidthOverride(290.f).HeightOverride(58.f)[Start]
                        ]
                        + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Left)
                        [
                            SNew(SBox).WidthOverride(290.f).HeightOverride(47.f)[Quit]
                        ]
                    ]
                ]
            ]
        ];
    Viewport->AddViewportWidgetContent(Lobby.ToSharedRef(), 20);
    bShowMouseCursor = true;
    FInputModeUIOnly Mode;
    Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
    Mode.SetWidgetToFocus(Start);
    SetInputMode(Mode);
}

void ADirectorCutLobbyController::StartLobbyAction(bool bQuit)
{
    if (bStarting) return;
    bStarting = true;
    if (ButtonClickSound) UGameplayStatics::PlaySound2D(this, ButtonClickSound, .45f);
    // Let the same short selection sound finish before travel or application exit.
    const float Delay = ButtonClickSound ? FMath::Max(.05f, ButtonClickSound->GetDuration() + .02f) : .05f;
    GetWorldTimerManager().SetTimer(LobbyActionTimer, FTimerDelegate::CreateWeakLambda(this, [this, bQuit]
    {
        if (bQuit) UKismetSystemLibrary::QuitGame(this, this, EQuitPreference::Quit, false);
        else UGameplayStatics::OpenLevel(this, FName(TEXT("/Game/DirectorCut/Prologue/L_BossPrologue")));
    }), Delay, false);
}

void ADirectorCutLobbyController::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    GetWorldTimerManager().ClearTimer(LobbyActionTimer);
    if (IsValid(LobbyMusicComponent)) LobbyMusicComponent->Stop();
    LobbyMusicComponent = nullptr;
    if (Lobby.IsValid())
    {
        if (UGameViewportClient* Viewport = GetWorld()->GetGameViewport())
        {
            Viewport->RemoveViewportWidgetContent(Lobby.ToSharedRef());
        }
        Lobby.Reset();
    }
    Super::EndPlay(EndPlayReason);
}

#undef LOCTEXT_NAMESPACE

