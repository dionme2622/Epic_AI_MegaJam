#include "DirectorCutEnding.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimData/IAnimationDataController.h"
#include "Animation/Skeleton.h"
#include "Engine/SkeletalMesh.h"
#include "UObject/Package.h"

#include "Engine/GameViewportClient.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "Framework/Application/SlateApplication.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "LevelSequenceActor.h"
#include "LevelSequencePlayer.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Images/SImage.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SScaleBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SCompoundWidget.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"

#define LOCTEXT_NAMESPACE "DirectorCutEnding"

ADirectorCutEndingMode::ADirectorCutEndingMode()
{
    DefaultPawnClass = nullptr;
    HUDClass = nullptr;
}

namespace
{
    const FLinearColor EndingGold(.92f, .71f, .35f);
    const FLinearColor EndingInk(.018f, .026f, .037f, .98f);
    const FLinearColor EndingIvory(.95f, .94f, .87f);

    TSharedRef<STextBlock> EndingText(FText Text, int32 Size, FLinearColor Color = EndingIvory)
    {
        return SNew(STextBlock).Text(Text)
            .Font(FCoreStyle::GetDefaultFontStyle("Regular", Size))
            .ColorAndOpacity(Color).Justification(ETextJustify::Center);
    }

    void SetModelVisible(AActor* Actor, bool bVisible)
    {
        if (IsValid(Actor))
        {
            Actor->SetActorHiddenInGame(!bVisible);
            Actor->SetActorEnableCollision(false);
        }
    }

    /** Keep keyboard navigation on the modal even when a child button has focus. */
    class SEndingChoice : public SCompoundWidget
    {
    public:
        SLATE_BEGIN_ARGS(SEndingChoice) {}
            SLATE_DEFAULT_SLOT(FArguments, Content)
            SLATE_EVENT(FOnKeyDown, HandleKey)
        SLATE_END_ARGS()

        void Construct(const FArguments& Args)
        {
            HandleKey = Args._HandleKey;
            ChildSlot[Args._Content.Widget];
        }

        virtual bool SupportsKeyboardFocus() const override { return true; }
        virtual FReply OnPreviewKeyDown(const FGeometry&, const FKeyEvent& Event) override
        {
            return HandleKey.IsBound() ? HandleKey.Execute(GetCachedGeometry(), Event) : FReply::Unhandled();
        }
        virtual FReply OnKeyDown(const FGeometry&, const FKeyEvent& Event) override
        {
            return HandleKey.IsBound() ? HandleKey.Execute(GetCachedGeometry(), Event) : FReply::Unhandled();
        }

    private:
        FOnKeyDown HandleKey;
    };
}

ADirectorCutEnding::ADirectorCutEnding()
{
    PrimaryActorTick.bCanEverTick = false;
    HeroSubtitle = LOCTEXT("HeroLine", "준비됐어? 이제 제대로 마지막 전투를 찍을 수 있겠네.");
    DragonSubtitle = LOCTEXT("DragonLine", "잠깐. 나는 어떤 모습으로 나갈지 아직 안 정했어.");
}

UAnimSequence* ADirectorCutEnding::BuildAwkwardWalkAnimation()
{
#if WITH_EDITOR
    USkeletalMesh* Mesh = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/DirectorCut/Dragon/Origin/SK_Dragon_Origin.SK_Dragon_Origin"));
    if (!Mesh) return nullptr;
    UPackage* Package = CreatePackage(TEXT("/Game/DirectorCut/Ending/Animation/A_Dragon_AwkwardWalk"));
    UAnimSequence* Animation = FindObject<UAnimSequence>(Package, TEXT("A_Dragon_AwkwardWalk"));
    if (!Animation) Animation = NewObject<UAnimSequence>(Package, TEXT("A_Dragon_AwkwardWalk"), RF_Public | RF_Standalone | RF_Transactional);
    Animation->SetSkeleton(Mesh->GetSkeleton());
    Animation->SetPreviewMesh(Mesh);
    IAnimationDataController& Controller = Animation->GetController();
    Controller.OpenBracket(LOCTEXT("BuildWalk", "Build unfinished dragon walk"), false);
    Controller.InitializeModel();
    Controller.SetFrameRate(FFrameRate(24, 1), false);
    Controller.SetNumberOfFrames(FFrameNumber(48), false);
    const FReferenceSkeleton& Ref = Mesh->GetRefSkeleton();
    const TArray<FTransform>& Pose = Ref.GetRefBonePose();
    // Long frozen poses and uneven leg phases intentionally mimic an unfinished blocking pass.
    const float Left[]  = {0, 0, -14, -14, 11, 11, 0, 0, 0};
    const float Right[] = {0, 12, 12, 12, 0, -10, -10, 0, 0};
    for (int32 Bone = 0; Bone < Ref.GetNum(); ++Bone)
    {
        const FName Name = Ref.GetBoneName(Bone);
        Controller.AddBoneCurve(Name, false);
        TArray<FVector> Positions, Scales;
        TArray<FQuat> Rotations;
        for (int32 Frame = 0; Frame <= 48; ++Frame)
        {
            FTransform Local = Pose[Bone];
            const int32 Step = FMath::Min(Frame / 6, 7);
            // A short linear snap between held key poses, rather than a polished gait.
            const float Blend = FMath::Clamp((Frame % 6 - 3.f) / 2.f, 0.f, 1.f);
            float Angle = 0.f;
            if (Name == TEXT("Thigh_L")) Angle = FMath::Lerp(Left[Step], Left[Step + 1], Blend);
            if (Name == TEXT("Thigh_R")) Angle = FMath::Lerp(Right[Step], Right[Step + 1], Blend);
            Local.SetRotation(Local.GetRotation() * FQuat(FVector::XAxisVector, FMath::DegreesToRadians(Angle)));
            Positions.Add(Local.GetTranslation()); Rotations.Add(Local.GetRotation()); Scales.Add(Local.GetScale3D());
        }
        Controller.SetBoneTrackKeys(Name, Positions, Rotations, Scales, false);
    }
    Controller.NotifyPopulated();
    Controller.CloseBracket(false);
    Animation->MarkPackageDirty();
    return Animation;
#else
    return nullptr;
#endif
}

UAnimSequence* ADirectorCutEnding::BuildHeroLegsScurryAnimation()
{
#if WITH_EDITOR
    USkeletalMesh* Mesh = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/DirectorCut/Dragon/KnightLegs/SK_Knight_LowerBody.SK_Knight_LowerBody"));
    if (!Mesh) return nullptr;
    UPackage* Package = CreatePackage(TEXT("/Game/DirectorCut/Ending/Animation/A_HeroLegs_Scurry"));
    UAnimSequence* Animation = FindObject<UAnimSequence>(Package, TEXT("A_HeroLegs_Scurry"));
    if (!Animation) Animation = NewObject<UAnimSequence>(Package, TEXT("A_HeroLegs_Scurry"), RF_Public | RF_Standalone | RF_Transactional);
    Animation->SetSkeleton(Mesh->GetSkeleton());
    Animation->SetPreviewMesh(Mesh);
    IAnimationDataController& Controller = Animation->GetController();
    Controller.OpenBracket(LOCTEXT("BuildScurry", "Build smooth little-leg walk"), false);
    Controller.InitializeModel();
    Controller.SetFrameRate(FFrameRate(24, 1), false);
    Controller.SetNumberOfFrames(FFrameNumber(24), false);
    const FReferenceSkeleton& Ref = Mesh->GetRefSkeleton();
    const TArray<FTransform>& Pose = Ref.GetRefBonePose();
    TArray<FTransform> ComponentPose;
    for (int32 Bone = 0; Bone < Ref.GetNum(); ++Bone)
    {
        const int32 Parent = Ref.GetParentIndex(Bone);
        ComponentPose.Add(Parent == INDEX_NONE ? Pose[Bone] : Pose[Bone] * ComponentPose[Parent]);
    }
    for (int32 Bone = 0; Bone < Ref.GetNum(); ++Bone)
    {
        const FName Name = Ref.GetBoneName(Bone);
        Controller.AddBoneCurve(Name, false);
        TArray<FVector> Positions, Scales;
        TArray<FQuat> Rotations;
        const FString BoneName = Name.ToString();
        const bool bLeft = BoneName.StartsWith(TEXT("Left"));
        for (int32 Frame = 0; Frame <= 24; ++Frame)
        {
            FTransform Local = Pose[Bone];
            const float Phase = 2.f * PI * Frame / 24.f + (bLeft ? 0.f : PI);
            float Angle = 0.f;
            if (Name == TEXT("LeftUpLeg") || Name == TEXT("RightUpLeg")) Angle = 22.f * FMath::Sin(Phase);
            if (Name == TEXT("LeftLeg") || Name == TEXT("RightLeg")) Angle = -28.f * FMath::Square(FMath::Max(0.f, FMath::Sin(Phase)));
            if (Name == TEXT("LeftFoot") || Name == TEXT("RightFoot")) Angle = 4.f * FMath::Sin(Phase);
            const FVector Axis = ComponentPose[Bone].GetRotation().UnrotateVector(FVector::ForwardVector);
            Local.SetRotation(Local.GetRotation() * FQuat(Axis, FMath::DegreesToRadians(Angle)));
            Positions.Add(Local.GetTranslation()); Rotations.Add(Local.GetRotation()); Scales.Add(Local.GetScale3D());
        }
        Controller.SetBoneTrackKeys(Name, Positions, Rotations, Scales, false);
    }
    Controller.NotifyPopulated();
    Controller.CloseBracket(false);
    Animation->MarkPackageDirty();
    return Animation;
#else
    return nullptr;
#endif
}

void ADirectorCutEnding::BeginPlay()
{
    Super::BeginPlay();
    LocalController = UGameplayStatics::GetPlayerController(this, 0);
    if (APlayerController* Controller = LocalController.Get())
    {
        PreviousViewTarget = Controller->GetViewTarget();
        bPreviousMouseCursor = Controller->bShowMouseCursor;
        Controller->SetIgnoreMoveInput(true);
        Controller->SetIgnoreLookInput(true);
        bBlockedPlayerInput = true;
        SetChoiceInput(false);
        if (EndingCamera)
        {
            Controller->SetViewTarget(EndingCamera);
        }
    }

    // The ending repeats the prologue's opening: the dragon has no lower body yet.
    if (UpperDragon) InitialUpperTransform = UpperDragon->GetActorTransform();
    SetModelVisible(FullDragon, false);
    SetModelVisible(UpperDragon, true);
    SetModelVisible(DragonLowerBody, false);
    SetModelVisible(CartBody, false);
    for (AActor* Accessory : CartAccessories) SetModelVisible(Accessory, false);
    SetModelVisible(HeroLegs, false);
    for (AActor* SceneActor : CartSceneActors) SetModelVisible(SceneActor, false);
    CreateOverlay();
    if (IntroSequenceActor && IntroSequenceActor->GetSequencePlayer())
    {
        ULevelSequencePlayer* Player = IntroSequenceActor->GetSequencePlayer();
        Player->OnFinished.AddUniqueDynamic(this, &ADirectorCutEnding::ShowChoice);
        Player->Play();
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Ending has no intro sequence; opening the lower-body choice."));
        ShowChoice();
    }
}

FText ADirectorCutEnding::GetCurrentSubtitle() const
{
    if (EndingState == EDirectorCutEndingState::HeroLegsScene && HeroLegsSequenceActor && HeroLegsSequenceActor->GetSequencePlayer())
    {
        const double Time = HeroLegsSequenceActor->GetSequencePlayer()->GetCurrentTime().AsSeconds();
        return Time >= 3.5 && Time < 6.5 ? LOCTEXT("HeroLegsQuestion", "왜 내 다리가 저기 있는거야?") : FText::GetEmpty();
    }
    if (EndingState == EDirectorCutEndingState::CartScene && CartSequenceActor && CartSequenceActor->GetSequencePlayer())
    {
        const double Time = CartSequenceActor->GetSequencePlayer()->GetCurrentTime().AsSeconds();
        if (Time >= .75 && Time < 3.3) return LOCTEXT("CartBrakes", "잠깐. 이거 브레이크는 어디—");
        if (Time >= 3.3 && Time < 5.75) return LOCTEXT("CartScream", "으아아!!!");
        return FText::GetEmpty();
    }
    if (EndingState == EDirectorCutEndingState::OriginalLegsScene && OriginalLegsSequenceActor && OriginalLegsSequenceActor->GetSequencePlayer())
    {
        const double Time = OriginalLegsSequenceActor->GetSequencePlayer()->GetCurrentTime().AsSeconds();
        if (Time >= 6.5 && Time < 9.7) return LOCTEXT("AwkwardHero", "…너 원래 그렇게 걸었어?");
        if (Time >= 10.1 && Time < 14.4) return LOCTEXT("AwkwardDragon", "하... 애니메이션은 또 왜 이래.");
        return FText::GetEmpty();
    }
    if (EndingState != EDirectorCutEndingState::Dialogue || !IntroSequenceActor || !IntroSequenceActor->GetSequencePlayer())
    {
        return FText::GetEmpty();
    }
    const double Time = IntroSequenceActor->GetSequencePlayer()->GetCurrentTime().AsSeconds();
    if (Time >= HeroSubtitleStart && Time < HeroSubtitleEnd) return HeroSubtitle;
    if (Time >= DragonSubtitleStart && Time < DragonSubtitleEnd) return DragonSubtitle;
    return FText::GetEmpty();
}

FText ADirectorCutEnding::GetCurrentEnglishSubtitle() const
{
    if (GetCurrentSubtitle().IsEmpty()) return FText::GetEmpty();
    if (EndingState == EDirectorCutEndingState::HeroLegsScene) return LOCTEXT("HeroLegsQuestionEnglish", "Why are my legs over there?");
    if (EndingState == EDirectorCutEndingState::CartScene)
    {
        const double Time = CartSequenceActor->GetSequencePlayer()->GetCurrentTime().AsSeconds();
        return Time < 3.3
            ? LOCTEXT("CartBrakesEnglish", "Wait. Where are the brakes on this—")
            : LOCTEXT("CartScreamEnglish", "Aaaah!!!");
    }
    if (EndingState == EDirectorCutEndingState::OriginalLegsScene)
    {
        const double Time = OriginalLegsSequenceActor->GetSequencePlayer()->GetCurrentTime().AsSeconds();
        return Time < 10.1
            ? LOCTEXT("AwkwardHeroEnglish", "...Have you always walked like that?")
            : LOCTEXT("AwkwardDragonEnglish", "Sigh... What's wrong with the animation now?");
    }
    const double Time = IntroSequenceActor->GetSequencePlayer()->GetCurrentTime().AsSeconds();
    return Time < DragonSubtitleStart
        ? LOCTEXT("HeroLineEnglish", "Ready? Now we can finally film the final battle properly.")
        : LOCTEXT("DragonLineEnglish", "Wait. I haven't decided what I want to look like yet.");
}

FText ADirectorCutEnding::GetCurrentSpeaker() const
{
    if (EndingState == EDirectorCutEndingState::HeroLegsScene) return LOCTEXT("Hero", "용사");
    if (EndingState == EDirectorCutEndingState::CartScene) return LOCTEXT("Dragon", "드래곤");
    if (EndingState == EDirectorCutEndingState::OriginalLegsScene && OriginalLegsSequenceActor && OriginalLegsSequenceActor->GetSequencePlayer())
    {
        const double Time = OriginalLegsSequenceActor->GetSequencePlayer()->GetCurrentTime().AsSeconds();
        return Time < 10.1 ? LOCTEXT("Hero", "용사") : LOCTEXT("Dragon", "드래곤");
    }
    if (!IntroSequenceActor || !IntroSequenceActor->GetSequencePlayer()) return FText::GetEmpty();
    const double Time = IntroSequenceActor->GetSequencePlayer()->GetCurrentTime().AsSeconds();
    return Time < DragonSubtitleStart ? LOCTEXT("Hero", "용사") : LOCTEXT("Dragon", "드래곤");
}

void ADirectorCutEnding::ShowChoice()
{
    if (EndingState != EDirectorCutEndingState::Dialogue) return;
    EndingState = EDirectorCutEndingState::Choosing;
    FocusedOption = 0;
    if (APlayerController* Controller = LocalController.Get(); Controller && EndingCamera)
    {
        Controller->SetViewTarget(EndingCamera);
    }
    SetChoiceInput(true);
}

void ADirectorCutEnding::ChooseLowerBody(int32 OptionIndex)
{
    if (EndingState != EDirectorCutEndingState::Choosing || OptionIndex < 0 || OptionIndex > 2) return;
    SelectedLowerBody = OptionIndex;
    EndingState = EDirectorCutEndingState::Revealing;
    ApplyLowerBody(OptionIndex);
    SetChoiceInput(false);
    if (RevealSequenceActor && RevealSequenceActor->GetSequencePlayer())
    {
        ULevelSequencePlayer* Player = RevealSequenceActor->GetSequencePlayer();
        Player->OnFinished.AddUniqueDynamic(this, &ADirectorCutEnding::FinishReveal);
        Player->Play();
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Ending has no reveal sequence; preserving the selected model."));
        FinishReveal();
    }
}

void ADirectorCutEnding::ApplyLowerBody(int32 OptionIndex)
{
    const bool bOriginal = OptionIndex == 0;
    if (UpperDragon)
    {
        AActor* Rig = OptionIndex == 1 && CartBody ? CartBody->GetAttachParentActor() :
            (OptionIndex == 2 && HeroLegs ? HeroLegs->GetAttachParentActor() : nullptr);
        UpperDragon->DetachFromActor(FDetachmentTransformRules::KeepWorldTransform);
        if (Rig) UpperDragon->AttachToActor(Rig, FAttachmentTransformRules::KeepWorldTransform);
    }
    SetModelVisible(FullDragon, bOriginal);
    SetModelVisible(UpperDragon, !bOriginal || !FullDragon);
    SetModelVisible(DragonLowerBody, bOriginal && !FullDragon);
    SetModelVisible(CartBody, OptionIndex == 1);
    for (AActor* Accessory : CartAccessories) SetModelVisible(Accessory, OptionIndex == 1);
    SetModelVisible(HeroLegs, OptionIndex == 2);
    if (UpperDragon && bUseVariantUpperTransforms && !bOriginal)
    {
        UpperDragon->SetActorTransform(OptionIndex == 1 ? CartUpperTransform : HeroUpperTransform);
    }
    else if (UpperDragon && bOriginal)
    {
        UpperDragon->SetActorTransform(InitialUpperTransform);
    }
}

void ADirectorCutEnding::FinishReveal()
{
    if (EndingState != EDirectorCutEndingState::Revealing) return;
    if (SelectedLowerBody == 0 && OriginalLegsSequenceActor && OriginalLegsSequenceActor->GetSequencePlayer())
    {
        EndingState = EDirectorCutEndingState::OriginalLegsScene;
        ULevelSequencePlayer* Player = OriginalLegsSequenceActor->GetSequencePlayer();
        Player->OnFinished.AddUniqueDynamic(this, &ADirectorCutEnding::FinishBranchScene);
        Player->Play();
        return;
    }
    if (SelectedLowerBody == 1 && CartSequenceActor && CartSequenceActor->GetSequencePlayer())
    {
        EndingState = EDirectorCutEndingState::CartScene;
        for (AActor* SceneActor : CartSceneActors) SetModelVisible(SceneActor, true);
        ULevelSequencePlayer* Player = CartSequenceActor->GetSequencePlayer();
        Player->OnFinished.AddUniqueDynamic(this, &ADirectorCutEnding::FinishBranchScene);
        Player->Play();
        return;
    }
    if (SelectedLowerBody == 2 && HeroLegsSequenceActor && HeroLegsSequenceActor->GetSequencePlayer())
    {
        EndingState = EDirectorCutEndingState::HeroLegsScene;
        ULevelSequencePlayer* Player = HeroLegsSequenceActor->GetSequencePlayer();
        Player->OnFinished.AddUniqueDynamic(this, &ADirectorCutEnding::FinishBranchScene);
        Player->Play();
        return;
    }
    FinishBranchScene();
}

void ADirectorCutEnding::FinishBranchScene()
{
    if (EndingState != EDirectorCutEndingState::Revealing && EndingState != EDirectorCutEndingState::OriginalLegsScene && EndingState != EDirectorCutEndingState::CartScene && EndingState != EDirectorCutEndingState::HeroLegsScene) return;
    EndingState = EDirectorCutEndingState::ReadyForContinuation;
    if (APlayerController* Controller = LocalController.Get(); Controller && EndingCamera)
    {
        Controller->SetViewTarget(EndingCamera);
    }
    OnReadyForContinuation(SelectedLowerBody);
}

void ADirectorCutEnding::SetChoiceInput(bool bChoosing)
{
    if (APlayerController* Controller = LocalController.Get())
    {
        Controller->bShowMouseCursor = bChoosing;
        if (bChoosing)
        {
            FInputModeUIOnly Mode;
            Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
            if (ChoicePanel.IsValid()) Mode.SetWidgetToFocus(ChoicePanel);
            Controller->SetInputMode(Mode);
            if (ChoicePanel.IsValid() && FSlateApplication::IsInitialized())
            {
                FSlateApplication::Get().SetKeyboardFocus(ChoicePanel, EFocusCause::SetDirectly);
            }
        }
        else
        {
            Controller->SetInputMode(FInputModeGameOnly());
        }
    }
}

void ADirectorCutEnding::CreateOverlay()
{
    UGameViewportClient* Viewport = GetWorld()->GetGameViewport();
    if (!Viewport) return;
    ImageBrushes.SetNum(3);
    for (int32 Index = 0; Index < 3; ++Index)
    {
        FSlateBrush& Brush = ImageBrushes[Index];
        Brush.DrawAs = ESlateBrushDrawType::Image;
        Brush.ImageSize = FVector2D(360.f, 290.f);
        if (OptionImages.IsValidIndex(Index) && OptionImages[Index]) Brush.SetResourceObject(OptionImages[Index]);
    }
    const TWeakObjectPtr<ADirectorCutEnding> WeakThis(this);
    auto MakeCard = [this, WeakThis](int32 Index, FText Title, FText Detail)
    {
        return SNew(SButton).ContentPadding(0).IsFocusable(false)
            .ButtonColorAndOpacity(FLinearColor::Transparent)
            .OnHovered_Lambda([WeakThis, Index] { if (WeakThis.IsValid()) WeakThis->FocusedOption = Index; })
            .OnClicked_Lambda([WeakThis, Index]
            {
                if (WeakThis.IsValid()) WeakThis->ChooseLowerBody(Index);
                return FReply::Handled();
            })
            [
                SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                .BorderBackgroundColor_Lambda([WeakThis, Index]
                {
                    return WeakThis.IsValid() && WeakThis->FocusedOption == Index ? EndingGold : FLinearColor(.19f, .23f, .27f);
                }).Padding(2)
                [
                    SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                    .BorderBackgroundColor(EndingInk).Padding(FMargin(14, 16))
                    [
                        SNew(SVerticalBox)
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 12)
                            [EndingText(FText::AsNumber(Index + 1), 19, EndingGold)]
                        + SVerticalBox::Slot().AutoHeight()
                        [
                            SNew(SBox).WidthOverride(360).HeightOverride(290)
                            [SNew(SImage).Image(&ImageBrushes[Index])]
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 20, 0, 9)
                            [EndingText(Title, 30)]
                        + SVerticalBox::Slot().AutoHeight()
                            [EndingText(Detail, 16, FLinearColor(.58f, .64f, .68f))]
                    ]
                ]
            ];
    };
    ChoicePanel = SNew(SEndingChoice)
        .HandleKey(FOnKeyDown::CreateLambda([WeakThis](const FGeometry&, const FKeyEvent& Event)
        {
            ADirectorCutEnding* Ending = WeakThis.Get();
            if (!Ending || Ending->EndingState != EDirectorCutEndingState::Choosing) return FReply::Unhandled();
            const FKey Key = Event.GetKey();
            if (Key == EKeys::One || Key == EKeys::NumPadOne) Ending->ChooseLowerBody(0);
            else if (Key == EKeys::Two || Key == EKeys::NumPadTwo) Ending->ChooseLowerBody(1);
            else if (Key == EKeys::Three || Key == EKeys::NumPadThree) Ending->ChooseLowerBody(2);
            else if (Key == EKeys::Right || Key == EKeys::D || Key == EKeys::Tab) Ending->FocusedOption = (Ending->FocusedOption + 1) % 3;
            else if (Key == EKeys::Left || Key == EKeys::A) Ending->FocusedOption = (Ending->FocusedOption + 2) % 3;
            else if (Key == EKeys::Enter || Key == EKeys::SpaceBar) Ending->ChooseLowerBody(Ending->FocusedOption);
            else return FReply::Handled();
            return FReply::Handled();
        }))
        [
            SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
            .BorderBackgroundColor(FLinearColor(.004f, .008f, .014f, .82f)).Padding(45)
            [
                SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::Both)
                [
                    SNew(SBox).WidthOverride(1280).HeightOverride(660)
                    [
                        SNew(SVerticalBox)
                        + SVerticalBox::Slot().AutoHeight()
                            [EndingText(LOCTEXT("ChoiceEyebrow", "THE FINAL TAKE"), 16, EndingGold)]
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 12, 0, 32)
                            [EndingText(LOCTEXT("ChoiceTitle", "Choose Your Lower Body"), 42)]
                        + SVerticalBox::Slot().AutoHeight()
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().FillWidth(1).Padding(0, 0, 12, 0)
                                [MakeCard(0, LOCTEXT("DragonLegs", "Dragon Legs"), LOCTEXT("DragonLegsDetail", "The original dragon"))]
                            + SHorizontalBox::Slot().FillWidth(1).Padding(6, 0, 6, 0)
                                [MakeCard(1, LOCTEXT("Cart", "Cart"), LOCTEXT("CartDetail", "A different kind of ride"))]
                            + SHorizontalBox::Slot().FillWidth(1).Padding(12, 0, 0, 0)
                                [MakeCard(2, LOCTEXT("HeroLegs", "Hero's Legs"), LOCTEXT("HeroLegsDetail", "Borrowed from the hero"))]
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 24, 0, 0)
                            [EndingText(LOCTEXT("ChoiceHelp", "Click a card  /  1, 2, 3 to choose  /  Arrow keys + Enter"), 17, FLinearColor(.65f, .69f, .72f))]
                    ]
                ]
            ]
        ];
    ChoicePanel->SetVisibility(TAttribute<EVisibility>::CreateLambda([WeakThis]
    {
        return WeakThis.IsValid() && WeakThis->EndingState == EDirectorCutEndingState::Choosing ? EVisibility::Visible : EVisibility::Collapsed;
    }));

    Overlay = SNew(SOverlay).Visibility(EVisibility::SelfHitTestInvisible)
        + SOverlay::Slot().HAlign(HAlign_Fill).VAlign(VAlign_Fill)[ChoicePanel.ToSharedRef()]
        + SOverlay::Slot().HAlign(HAlign_Fill).VAlign(VAlign_Bottom).Padding(70, 0, 70, 55)
        [
            SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::DownOnly)
            .Visibility_Lambda([WeakThis]
            {
                return WeakThis.IsValid() && !WeakThis->GetCurrentSubtitle().IsEmpty() ? EVisibility::HitTestInvisible : EVisibility::Collapsed;
            })
            [
                SNew(SBox).WidthOverride(1350)
                [
                    SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                    .BorderBackgroundColor(FLinearColor(.005f, .01f, .018f, .85f)).Padding(FMargin(36, 20))
                    [
                        SNew(SVerticalBox)
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 9)
                        [
                            SNew(STextBlock).Text_Lambda([WeakThis] { return WeakThis.IsValid() ? WeakThis->GetCurrentSpeaker() : FText::GetEmpty(); })
                            .Font(FCoreStyle::GetDefaultFontStyle("Bold", 20)).ColorAndOpacity(EndingGold).Justification(ETextJustify::Center)
                        ]
                        + SVerticalBox::Slot().AutoHeight()
                        [
                            SNew(STextBlock).Text_Lambda([WeakThis] { return WeakThis.IsValid() ? WeakThis->GetCurrentSubtitle() : FText::GetEmpty(); })
                            .Font(FCoreStyle::GetDefaultFontStyle("Regular", 30)).ColorAndOpacity(EndingIvory)
                            .Justification(ETextJustify::Center).WrapTextAt(1260)
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 8, 0, 0)
                        [
                            SNew(STextBlock).Text_Lambda([WeakThis] { return WeakThis.IsValid() ? WeakThis->GetCurrentEnglishSubtitle() : FText::GetEmpty(); })
                            .Font(FCoreStyle::GetDefaultFontStyle("Regular", 23))
                            .ColorAndOpacity(FLinearColor(.82f, .85f, .88f))
                            .Justification(ETextJustify::Center).WrapTextAt(1260)
                        ]
                    ]
                ]
            ]
        ];
    Viewport->AddViewportWidgetContent(Overlay.ToSharedRef(), 1000);
}

void ADirectorCutEnding::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (OriginalLegsSequenceActor && OriginalLegsSequenceActor->GetSequencePlayer())
    {
        OriginalLegsSequenceActor->GetSequencePlayer()->OnFinished.RemoveDynamic(this, &ADirectorCutEnding::FinishBranchScene);
    }
    if (CartSequenceActor && CartSequenceActor->GetSequencePlayer())
    {
        CartSequenceActor->GetSequencePlayer()->OnFinished.RemoveDynamic(this, &ADirectorCutEnding::FinishBranchScene);
    }
    if (IntroSequenceActor && IntroSequenceActor->GetSequencePlayer())
    {
        IntroSequenceActor->GetSequencePlayer()->OnFinished.RemoveDynamic(this, &ADirectorCutEnding::ShowChoice);
    }
    if (RevealSequenceActor && RevealSequenceActor->GetSequencePlayer())
    {
        RevealSequenceActor->GetSequencePlayer()->OnFinished.RemoveDynamic(this, &ADirectorCutEnding::FinishReveal);
    }
    if (HeroLegsSequenceActor && HeroLegsSequenceActor->GetSequencePlayer())
    {
        HeroLegsSequenceActor->GetSequencePlayer()->OnFinished.RemoveDynamic(this, &ADirectorCutEnding::FinishBranchScene);
    }
    if (Overlay.IsValid())
    {
        if (UGameViewportClient* Viewport = GetWorld()->GetGameViewport()) Viewport->RemoveViewportWidgetContent(Overlay.ToSharedRef());
        Overlay.Reset();
        ChoicePanel.Reset();
    }
    if (APlayerController* Controller = LocalController.Get())
    {
        if (bBlockedPlayerInput)
        {
            Controller->SetIgnoreMoveInput(false);
            Controller->SetIgnoreLookInput(false);
        }
        Controller->bShowMouseCursor = bPreviousMouseCursor;
        Controller->SetInputMode(FInputModeGameOnly());
        if (EndPlayReason == EEndPlayReason::Destroyed && PreviousViewTarget.IsValid()) Controller->SetViewTarget(PreviousViewTarget.Get());
    }
    Super::EndPlay(EndPlayReason);
}

#undef LOCTEXT_NAMESPACE

