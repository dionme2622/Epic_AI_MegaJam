#include "Stage4ShadowTheatre.h"

#include "Camera/PlayerCameraManager.h"
#include "Components/CapsuleComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/SpotLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "DirectorCutGraphics.h"
#include "DirectorCutInteractionData.h"
#include "DirectorCutTest.h"
#include "Engine/GameViewportClient.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"
#include "Sound/SoundBase.h"
#include "Stage2ShadowPrototype.h"
#include "Stage4ShadowStandIn.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"

#define LOCTEXT_NAMESPACE "Stage4ShadowTheatre"

namespace
{
    constexpr float WallY = -273.f;
    constexpr float ExhibitX = 2885.f;
    constexpr float SetEnd = 3140.f;
    constexpr float RecoveryDuration = 3.1f;
    constexpr float StandX[] = {220.f, 1370.f, 2690.f};

    struct FDeck
    {
        float Left;
        float Right;
        float Height;
    };

    // These indices match the hand-authored mesh and collision arrays in Stage4.
    constexpr FDeck Decks[] = {{-475,350,0}, {440,580,0}, {680,820,22}, {915,1080,37},
        {1190,1534,0}, {1644,1799,35}, {1900,2188,18}, {2294,2455,0}, {2560,3330,0}};
    constexpr uint32 FixedDecks = (1 << 0) | (1 << 4) | (1 << 6) | (1 << 8);
    constexpr uint32 WestDecks[] = {(1 << 1) | (1 << 2) | (1 << 3), 1 << 3};
    constexpr uint32 EastDecks[] = {1 << 5, 1 << 7};

    enum EStation { None = -1, Entrance, Center, Island };

    int32 StationAt(double X)
    {
        if (X >= -20. && X <= 342.) return Entrance;
        if (X >= 1215. && X <= 1518.) return Center;
        if (X >= 1928. && X <= 2160.) return Island;
        return None;
    }

    FVector LampPosition(bool bWest, float Angle)
    {
        // Each lamp has two marked shooting positions on its bracket.
        return bWest ? FVector(655.f + Angle * 165.f, 580.f, 309.f)
            : FVector(2040.f + Angle * 170.f, 565.f, 291.f);
    }

    FVector ProjectToWall(const FVector& Point, const FVector& Source)
    {
        const double Stretch = (WallY - Source.Y) / (Point.Y - Source.Y);
        return Source + (Point - Source) * Stretch;
    }

    FVector CuePoint(const UStaticMeshComponent& Rig)
    {
        // The central tower sill has a flat edge that stays readable against the masonry.
        return Rig.GetRelativeTransform().TransformPosition({0.f, 0.f, 102.f});
    }
}

AStage4ShadowTheatre::AStage4ShadowTheatre()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickGroup = TG_PostPhysics;
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("StageOrigin"));
    auto Prop = [&](const TCHAR* Name, bool bCastShadow)
    {
        UStaticMeshComponent* Mesh = CreateDefaultSubobject<UStaticMeshComponent>(FName(Name));
        Mesh->SetupAttachment(RootComponent);
        Mesh->SetMobility(EComponentMobility::Movable);
        Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Mesh->SetCastShadow(bCastShadow);
        Mesh->bAffectDistanceFieldLighting = false;
        return Mesh;
    };
    WestRig = Prop(TEXT("WestRig"), false);
    EastRig = Prop(TEXT("EastRig"), false);
    WestMarker = Prop(TEXT("WestMarker"), false);
    EastMarker = Prop(TEXT("EastMarker"), false);
    Glass = Prop(TEXT("Glass"), false);
    Exhibit = Prop(TEXT("Exhibit"), true);
    WestGuide = Prop(TEXT("WestGuide"), false);
    EastGuide = Prop(TEXT("EastGuide"), false);

    DisplayLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("DisplayLight"));
    DisplayLight->SetupAttachment(RootComponent);
    DisplayLight->SetMobility(EComponentMobility::Movable);
    DisplayLight->SetLightColor(FLinearColor(1.f, .56f, .24f));
    DisplayLight->SetIntensity(90.f);
    DisplayLight->SetAttenuationRadius(450.f);
    DisplayLight->SetCastShadows(false);
}

void AStage4ShadowTheatre::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);
    WestRig->SetRelativeLocation({748.f, 0.f, 198.f});
    EastRig->SetRelativeLocation({1930.f, 0.f, 200.f});
    WestRig->SetRelativeScale3D({1.f, 1.f, 342.f / 421.f});
    EastRig->SetRelativeScale3D({1.f, 1.f, 340.f / 459.f});
    Exhibit->SetRelativeLocation(FVector(ExhibitX, -114.f, 93.f) + ExhibitOffset);
    Exhibit->SetRelativeRotation(FRotator(0.f, -18.f, 0.f));
    Exhibit->SetRelativeScale3D(FVector(2.05f));
    Glass->SetRelativeLocation(FVector(ExhibitX, -114.f, 93.f) + ExhibitOffset);
    DisplayLight->SetRelativeLocation(FVector(ExhibitX + 10.f, -42.f, 217.f) + ExhibitOffset);
    WestGuide->SetVisibility(false);
    EastGuide->SetVisibility(false);
}

void AStage4ShadowTheatre::BeginPlay()
{
    Super::BeginPlay();
    // Instance data from the previous puzzle also supplies the two castle meshes.
    WestRig->SetRelativeLocation({748.f, 0.f, 198.f});
    EastRig->SetRelativeLocation({1930.f, 0.f, 200.f});
    WestRig->SetRelativeScale3D({1.f, 1.f, 342.f / 421.f});
    EastRig->SetRelativeScale3D({1.f, 1.f, 340.f / 459.f});
    WestGuide->SetVisibility(false);
    EastGuide->SetVisibility(false);
    UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
    InitializeDecks(Cube);
    InitializeCues(Cube);
    UpdateDecks(0.f, 0);

    if (UGameViewportClient* Viewport = GetWorld()->GetGameViewport())
    {
        Overlay = SNew(SOverlay).Visibility(EVisibility::HitTestInvisible)
            + SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Bottom).Padding(18.f, 12.f)
            [
                SNew(SBox).WidthOverride(600.f)
                [
                SNew(SBorder).Padding(FMargin(17.f, 7.f))
                .Visibility_Lambda([this] { return Prompt.IsEmpty() ? EVisibility::Collapsed : EVisibility::HitTestInvisible; })
                .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                .BorderBackgroundColor(FLinearColor(.047f, .023f, .033f, .93f))
                [
                    SNew(SVerticalBox)
                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)
                    [
                        SNew(STextBlock)
                        .Text_Lambda([this] { return Heading; })
                        .Font(FCoreStyle::GetDefaultFontStyle("Bold", 14))
                        .ColorAndOpacity(FLinearColor(.95f, .66f, .29f))
                    ]
                    + SVerticalBox::Slot().AutoHeight().Padding(0.f, 2.f, 0.f, 0.f).HAlign(HAlign_Center)
                    [
                        SNew(SBox).WidthOverride(560.f)
                        [
                            SNew(STextBlock)
                            .Text_Lambda([this] { return Prompt; })
                            .Font(FCoreStyle::GetDefaultFontStyle("Regular", 14))
                            .ColorAndOpacity(FLinearColor(.9f, .85f, .77f))
                            .WrapTextAt(550.f)
                            .Justification(ETextJustify::Center)
                        ]
                    ]
                ]
                ]
            ];
        Viewport->AddViewportWidgetContent(Overlay.ToSharedRef(), 7);
    }
}

void AStage4ShadowTheatre::InitializeDecks(UStaticMesh* Cube)
{
    DeckRestPositions.SetNum(UE_ARRAY_COUNT(Decks));
    DeckOpenness.SetNum(UE_ARRAY_COUNT(Decks));
    PreviewOutlines.SetNum(UE_ARRAY_COUNT(Decks) * 4);
    WorkMarks.SetNum(UE_ARRAY_COUNT(Decks));
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Decks); ++Index)
    {
        const FDeck& Deck = Decks[Index];
        if (DeckScenery.IsValidIndex(Index) && IsValid(DeckScenery[Index]))
        {
            DeckRestPositions[Index] = DeckScenery[Index]->GetComponentLocation();
        }
        DeckOpenness[Index] = (FixedDecks & (1 << Index)) ? 1.f : 0.f;
        if (!PreviewMaterial || !Cube || (FixedDecks & (1 << Index)))
        {
            continue;
        }
        auto Mark = [&](FVector Position, FVector Size)
        {
            auto* Component = NewObject<UStaticMeshComponent>(this);
            Component->SetupAttachment(RootComponent);
            Component->SetStaticMesh(Cube);
            Component->SetMaterial(0, PreviewMaterial);
            Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            Component->SetCastShadow(false);
            Component->SetRelativeTransform(FTransform(FQuat::Identity, Position, Size / 100.f));
            Component->SetVisibility(false);
            Component->RegisterComponent();
            return Component;
        };
        const float X = (Deck.Left + Deck.Right) * .5f;
        const float Width = Deck.Right - Deck.Left - 8.f;
        const float Z = Deck.Height + 70.f;
        for (int32 Edge = 0; Edge < 4; ++Edge)
        {
            const bool bHorizontal = Edge < 2;
            const float Side = Edge % 2 ? 1.f : -1.f;
            const FVector Position(X + (bHorizontal ? 0.f : Side * Width * .5f), WallY + 3.f,
                Z + (bHorizontal ? Side * 10.f : 0.f));
            PreviewOutlines[Index * 4 + Edge] = Mark(Position, bHorizontal ? FVector(Width, 2.5f, 3.5f) : FVector(3.5f, 2.5f, 20.f));
        }
        WorkMarks[Index] = Mark({X, 99.f, Deck.Height + 2.f}, {Width, 4.f, 3.f});
    }
}

void AStage4ShadowTheatre::InitializeCues(UStaticMesh* Cube)
{
    AngleCues.SetNum(4);
    CueIndicators.SetNum(4);
    for (int32 Lane = 0; Lane < 2; ++Lane)
    {
        const bool bWest = Lane == 0;
        UStaticMeshComponent* Marker = bWest ? WestMarker.Get() : EastMarker.Get();
        const UStaticMeshComponent& Rig = bWest ? *WestRig : *EastRig;
        for (int32 Angle = 0; Angle < 2; ++Angle)
        {
            UStaticMeshComponent* Cue = Marker;
            if (Angle == 1)
            {
                Cue = NewObject<UStaticMeshComponent>(this);
                Cue->SetupAttachment(RootComponent);
                Cue->SetStaticMesh(Marker->GetStaticMesh());
                Cue->SetCollisionEnabled(ECollisionEnabled::NoCollision);
                Cue->SetCastShadow(false);
                Cue->RegisterComponent();
            }
            FVector Position = ProjectToWall(CuePoint(Rig), LampPosition(bWest, Angle));
            Position.Y = WallY + 5.f;
            Cue->SetRelativeLocation(Position);
            Cue->SetRelativeScale3D(FVector(.71f));
            AngleCues[Lane * 2 + Angle] = Cue;
            if (Cube && PreviewMaterial)
            {
                auto* Indicator = NewObject<UStaticMeshComponent>(this);
                Indicator->SetupAttachment(RootComponent);
                Indicator->SetStaticMesh(Cube);
                Indicator->SetMaterial(0, PreviewMaterial);
                Indicator->SetCollisionEnabled(ECollisionEnabled::NoCollision);
                Indicator->SetCastShadow(false);
                Indicator->SetRelativeLocation(Position + FVector(0.f, 6.f, -21.f));
                Indicator->SetRelativeScale3D({.23f, .02f, .032f});
                Indicator->SetVisibility(false);
                Indicator->RegisterComponent();
                CueIndicators[Lane * 2 + Angle] = Indicator;
            }
        }
    }
}

void AStage4ShadowTheatre::UpdateLamp(FRetake& Retake, USpotLightComponent* Lamp, UStaticMeshComponent& Rig,
    TObjectPtr<UStaticMeshComponent>& Projection, const TCHAR* ProjectionName, bool bWest, bool bShadows, float DeltaSeconds)
{
    if (Retake.Angle != INDEX_NONE)
    {
        Retake.CurrentAngle = FMath::FInterpConstantTo(Retake.CurrentAngle, static_cast<float>(Retake.Angle), DeltaSeconds, 3.15f);
    }
    const FVector Source = LampPosition(bWest, Retake.CurrentAngle);
    const FVector Point = ProjectToWall(CuePoint(Rig), Source);
    Retake.Cue = INDEX_NONE;
    for (int32 Index = 0; Index < 2; ++Index)
    {
        const int32 CueIndex = (bWest ? 0 : 2) + Index;
        const UStaticMeshComponent* Marker = AngleCues[CueIndex];
        const bool bAligned = FMath::Abs(Marker->GetRelativeLocation().X - Point.X) < 5.f;
        if (bAligned)
        {
            Retake.Cue = Index;
        }
        if (CueIndicators[CueIndex])
        {
            CueIndicators[CueIndex]->SetVisibility(bShadows && bAligned);
        }
    }
    if (Lamp)
    {
        const FVector Aim(Point.X, WallY, Point.Z + 25.f);
        Lamp->SetWorldLocationAndRotation(GetActorTransform().TransformPosition(Source),
            GetActorTransform().TransformVectorNoScale(Aim - Source).Rotation());
    }
    UpdateProjection(Projection, Rig, ProjectionName, Source, bShadows);
}

void AStage4ShadowTheatre::UpdateLanes(float DeltaSeconds, int32 Station, bool bShadows)
{
    UpdateLamp(WestRetake, WestLamp, *WestRig, WestProjection, TEXT("WestProjection"), true, bShadows, DeltaSeconds);
    UpdateLamp(EastRetake, EastLamp, *EastRig, EastProjection, TEXT("EastProjection"), false, bShadows, DeltaSeconds);
    uint32 Preview = 0;
    if (bShadows)
    {
        if (Station == Entrance && WestRetake.Cue != INDEX_NONE) Preview = WestDecks[WestRetake.Cue];
        if ((Station == Center || Station == Island) && EastRetake.Cue != INDEX_NONE) Preview = EastDecks[EastRetake.Cue];
    }
    UpdateDecks(DeltaSeconds, Preview);
}

void AStage4ShadowTheatre::UpdateDecks(float DeltaSeconds, uint32 Preview)
{
    uint32 Open = FixedDecks;
    if (WestCut != INDEX_NONE) Open |= WestDecks[WestCut];
    if (EastCut != INDEX_NONE) Open |= EastDecks[EastCut];
    const auto* Graphics = GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>();
    const bool bWorkLights = Graphics && !Graphics->IsHigh(EDirectorCutGraphicsOption::Shadows);
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Decks); ++Index)
    {
        const bool bOpen = (Open & (1 << Index)) != 0;
        if (WorkMarks[Index])
        {
            WorkMarks[Index]->SetVisibility(bWorkLights && bOpen && DeckOpenness[Index] >= 1.f);
        }
        for (int32 Edge = 0; Edge < 4; ++Edge)
        {
            if (UStaticMeshComponent* Outline = PreviewOutlines[Index * 4 + Edge])
            {
                Outline->SetVisibility((Preview & (1 << Index)) != 0);
            }
        }
        if (FixedDecks & (1 << Index))
        {
            continue;
        }
        if (!DeckScenery.IsValidIndex(Index) || !DeckCollision.IsValidIndex(Index)
            || !DeckScenery[Index] || !DeckCollision[Index])
        {
            continue;
        }
        float& Openness = DeckOpenness[Index];
        Openness = FMath::FInterpConstantTo(Openness, bOpen ? 1.f : 0.f, DeltaSeconds, 1.95f);
        const float Slide = FMath::SmoothStep(0.f, 1.f, Openness);
        // Stow each stone deck behind the set wall. The collision becomes
        // walkable only when the full landing surface has arrived.
        DeckScenery[Index]->SetWorldLocation(DeckRestPositions[Index] +
            GetActorTransform().TransformVectorNoScale({0.f, -450.f * (1.f - Slide), 0.f}));
        DeckScenery[Index]->SetVisibility(Openness > 0.f);
        DeckCollision[Index]->SetCollisionEnabled(bOpen && Openness >= 1.f
            ? ECollisionEnabled::QueryAndPhysics : ECollisionEnabled::NoCollision);
    }
}

void AStage4ShadowTheatre::UpdateProjection(TObjectPtr<UStaticMeshComponent>& Projection, UStaticMeshComponent& Rig, const TCHAR* ComponentName,
    const FVector& SourcePosition, bool bShadows)
{
    const bool bVisible = bShadows && IsValid(SilhouetteMaterial) && Rig.GetStaticMesh();
    if (!Projection && bVisible)
    {
        Projection = NewObject<UStaticMeshComponent>(this, FName(ComponentName));
        Projection->SetupAttachment(RootComponent);
        Projection->SetMobility(EComponentMobility::Movable);
        Projection->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Projection->SetCastShadow(false);
        Projection->bAffectDistanceFieldLighting = false;
        Projection->SetStaticMesh(Rig.GetStaticMesh());
        for (int32 Slot = 0; Slot < Projection->GetNumMaterials(); ++Slot)
        {
            Projection->SetMaterial(Slot, SilhouetteMaterial);
        }
        Projection->RegisterComponent();
    }
    if (!Projection)
    {
        return;
    }
    Projection->SetVisibility(bVisible);
    if (!bVisible)
    {
        return;
    }

    // Project the same castle geometry onto the wall plane along the lamp rays.
    // This keeps the cue readable even when the renderer falls back to low-res
    // shadow maps. The visible castle and its hit envelope use the same motion.
    const FVector RigPosition = Rig.GetRelativeLocation();
    const double Stretch = (WallY - SourcePosition.Y) / (RigPosition.Y - SourcePosition.Y);
    FVector Projected = SourcePosition + (RigPosition - SourcePosition) * Stretch;
    Projected.Y = WallY;
    FVector Scale = Rig.GetRelativeScale3D() * Stretch;
    Scale.Y = .018;
    Projection->SetRelativeTransform(FTransform(FQuat::Identity, Projected, Scale));
}

void AStage4ShadowTheatre::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    ADirectorCutDragon* Dragon = Cast<ADirectorCutDragon>(UGameplayStatics::GetPlayerCharacter(this, 0));
    if (!Dragon)
    {
        return;
    }

    const FVector P = GetActorTransform().InverseTransformPosition(Dragon->GetActorLocation());
    const bool bPastGate = !IsValid(EntranceDoor) || EntranceDoor->bOpen;
    const bool bInside = bPastGate && P.X >= -315.f && P.X < SetEnd + ExhibitOffset.X + 50.f;
    const float Framing = bInside ? FMath::SmoothStep(-315.f, 55.f, static_cast<float>(P.X)) : 0.f;
    const double Extension = ExhibitOffset.X * FMath::SmoothStep(2950., 3710., P.X);
    Dragon->SetTheatreCameraFraming(Framing, GetActorLocation().X + FMath::Clamp(P.X, 485., 2370. + Extension));
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
    if (P.Z < -165.f && (!StandInPuzzle || !StandInPuzzle->OwnsRecovery(P.X + GetActorLocation().X)))
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
        if (Checkpoint == 2 && (!StandInPuzzle || StandInPuzzle->bReachedExhibit)
            && FMath::Abs(X - ExhibitX - ExhibitOffset.X) <= 125.f
            && Controller->WasInputKeyJustPressed(EKeys::E))
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

bool AStage4ShadowTheatre::GetInteractionPrompt(const ADirectorCutDragon& Dragon, FDirectorCutInteractionPrompt& Out) const
{
    if (bRecovered || RecoveryTime >= 0.f || (IsValid(EntranceDoor) && !EntranceDoor->bOpen)
        || !Dragon.GetCharacterMovement()->IsMovingOnGround())
    {
        return false;
    }

    const FVector Local = GetActorTransform().InverseTransformPosition(Dragon.GetActorLocation());
    if (Checkpoint == 2 && (!StandInPuzzle || StandInPuzzle->bReachedExhibit)
        && FMath::Abs(Local.X - ExhibitX - ExhibitOffset.X) <= 125.f)
    {
        Out = {FText::FromString(TEXT("E")), LOCTEXT("RecoverLegsKeyKo", "다리 되찾기"),
            LOCTEXT("RecoverLegsKeyEn", "Recover your legs"),
            GetActorTransform().TransformPosition(FVector(ExhibitX, -65.f, 205.f) + ExhibitOffset)};
        return true;
    }

    const int32 Station = StationAt(Local.X);
    if (Station == None || ResetFlash > 0.f || CutFlash > 0.f)
    {
        return false;
    }

    const auto* Graphics = GetWorld()->GetSubsystem<UDirectorCutGraphicsSubsystem>();
    const FRetake& Retake = Station == Entrance ? WestRetake : EastRetake;
    const int32 Committed = Station == Entrance ? WestCut : EastCut;
    const bool bCanCut = (!Graphics || Graphics->IsHigh(EDirectorCutGraphicsOption::Shadows))
        && Retake.Cue != INDEX_NONE && Retake.Cue != Committed && FMath::Abs(Retake.CurrentAngle - Retake.Angle) <= .04f;
    Out = {FText::FromString(bCanCut ? TEXT("E") : TEXT("Q / R")),
        bCanCut ? LOCTEXT("LockShotKeyKo", "이 장면 확정") : LOCTEXT("AimLightKeyKo", "조명 방향 바꾸기"),
        bCanCut ? LOCTEXT("LockShotKeyEn", "Lock this shot") : LOCTEXT("AimLightKeyEn", "Aim the lamp"),
        GetActorTransform().TransformPosition({Local.X, -65.f, Local.Z + 100.f})};
    return true;
}

void AStage4ShadowTheatre::SetCheckpoint(ADirectorCutDragon& Dragon, int32 Index)
{
    Checkpoint = Index;
    const float Height = Dragon.GetCapsuleComponent()->GetScaledCapsuleHalfHeight() + 2.f;
    Dragon.SetPuzzleRespawnPoint(GetActorTransform().TransformPosition({StandX[Index], 0.f, Height}));
}

void AStage4ShadowTheatre::ReturnToMark(ADirectorCutDragon& Dragon)
{
    ++ResetCount;
    ResetFlash = .85f;
    SetCheckpoint(Dragon, Checkpoint);
    const float Height = Dragon.GetCapsuleComponent()->GetScaledCapsuleHalfHeight() + 3.f;
    Dragon.StopJumping();
    Dragon.GetCharacterMovement()->StopMovementImmediately();
    Dragon.TeleportTo(GetActorTransform().TransformPosition({StandX[Checkpoint], 0.f, Height}),
        Dragon.GetActorRotation(), false, true);
    Dragon.GetCharacterMovement()->SetMovementMode(MOVE_Falling);
    if (APlayerController* Controller = Cast<APlayerController>(Dragon.GetController()); Controller && Controller->PlayerCameraManager)
    {
        Controller->PlayerCameraManager->StartCameraFade(.70f, 0.f, .35f, FLinearColor::Black, false, false);
    }
    Heading = LOCTEXT("Miss", "MISSED MARK");
    Prompt = LOCTEXT("Retry", "Back to the last safe platform.");
}

void AStage4ShadowTheatre::UpdatePrompt(float X, int32 Station, bool bShadows)
{
    if (ResetFlash > 0.f)
    {
        return;
    }
    if (Checkpoint == 2 && (!StandInPuzzle || StandInPuzzle->bReachedExhibit)
        && FMath::Abs(X - ExhibitX - ExhibitOffset.X) <= 125.f)
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
        const FText Unset = LOCTEXT("Unset", "--");
        const FText Set = Committed == INDEX_NONE ? Unset : FText::AsNumber(Committed + 1);
        const FText Shot = Preview.Angle == INDEX_NONE ? Unset : FText::AsNumber(Preview.Angle + 1);
        Prompt = FText::Format(
            LOCTEXT("Controls", "Q / R  Aim lamp     E  Cut    |    Preview {0} / Cut {1}\n{2}"),
            Shot, Set,
            Station == Island ? LOCTEXT("NextShot", "Line up a shot that reaches the display platform.")
                : LOCTEXT("ShotHint", "Use the castle's shadow to line up a brass mark. Compare the paths."));
    }
}

void AStage4ShadowTheatre::UpdateCostume(ADirectorCutDragon& Dragon, bool bUseCostume)
{
    if (CostumeDragon.Get() == &Dragon && bUseCostume == bCostumeApplied)
    {
        return;
    }
    for (UStaticMeshComponent* Boot : Boots)
    {
        if (IsValid(Boot))
        {
            Boot->DestroyComponent();
        }
    }
    Boots.Reset();
    CostumeDragon = &Dragon;
    bCostumeApplied = bUseCostume;
    if (!bUseCostume || !KnightGreave)
    {
        return;
    }

    USkeletalMeshComponent* Mesh = Dragon.GetMesh();
    for (const FName Bone : {FName("Shin_L"), FName("Shin_R")})
    {
        if (Mesh->GetBoneIndex(Bone) == INDEX_NONE)
        {
            continue;
        }
        auto* Boot = NewObject<UStaticMeshComponent>(&Dragon);
        Boot->SetStaticMesh(KnightGreave);
        Boot->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Boot->SetupAttachment(Mesh, Bone);
        Boot->SetAbsolute(false, false, true);
        Boot->RegisterComponent();
        Boots.Add(Boot);
    }
}

void AStage4ShadowTheatre::StartRecovery(ADirectorCutDragon& Dragon)
{
    bRecovered = true;
    RecoveryTime = 0.f;
    RecoveryPositionX = GetActorTransform().InverseTransformPosition(Dragon.GetActorLocation()).X;
    RecoveryFloorZ = GetActorTransform().InverseTransformPosition(Dragon.GetActorLocation()).Z
        - Dragon.GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
    Dragon.GetCharacterMovement()->StopMovementImmediately();
    RecoveryController = Cast<APlayerController>(Dragon.GetController());
    if (APlayerController* Controller = RecoveryController.Get())
    {
        Controller->SetIgnoreMoveInput(true);
    }
    Heading = LOCTEXT("Taking", "FINAL TAKE");
    Prompt = LOCTEXT("Opening", "Opening the display case...");
    if (RecoveryCue)
    {
        UGameplayStatics::PlaySoundAtLocation(this, RecoveryCue, Exhibit->GetComponentLocation());
    }
}

void AStage4ShadowTheatre::UpdateRecovery(float DeltaSeconds)
{
    const float Previous = RecoveryTime;
    RecoveryTime += DeltaSeconds;
    const float Lift = FMath::SmoothStep(.1f, 1.4f, RecoveryTime);
    const float Install = FMath::SmoothStep(1.25f, 2.05f, RecoveryTime);
    Glass->SetRelativeLocation(FVector(ExhibitX, -114.f, 93.f + 265.f * Lift) + ExhibitOffset);
    Exhibit->SetRelativeLocation(FMath::Lerp(FVector(ExhibitX, -114.f, 93.f) + ExhibitOffset,
        FVector(RecoveryPositionX, 0.f, RecoveryFloorZ + 48.f), Install));
    Exhibit->SetRelativeScale3D(FVector(FMath::Lerp(2.05f, .25f, Install)));
    DisplayLight->SetIntensity(FMath::Lerp(90.f, 175.f, Lift));
    if (Previous < 2.04f && RecoveryTime >= 2.04f)
    {
        Exhibit->SetVisibility(false);
        if (APlayerController* Controller = RecoveryController.Get(); Controller && Controller->PlayerCameraManager)
        {
            Controller->PlayerCameraManager->StartCameraFade(.34f, 0.f, .42f, FLinearColor(1.f, .74f, .44f), false, false);
        }
        Heading = LOCTEXT("Final", "DIRECTOR'S CUT");
        Prompt = LOCTEXT("Done", "Original legs restored.");
    }
    if (RecoveryTime >= RecoveryDuration)
    {
        if (APlayerController* Controller = RecoveryController.Get())
        {
            Controller->SetIgnoreMoveInput(false);
        }
        RecoveryController.Reset();
        RecoveryTime = -1.f;
        FinishMessage = 5.f;
    }
}

void AStage4ShadowTheatre::EndPlay(const EEndPlayReason::Type Reason)
{
    if (APlayerController* Controller = RecoveryController.Get())
    {
        Controller->SetIgnoreMoveInput(false);
    }
    if (Overlay.IsValid() && GetWorld() && GetWorld()->GetGameViewport())
    {
        GetWorld()->GetGameViewport()->RemoveViewportWidgetContent(Overlay.ToSharedRef());
    }
    Overlay.Reset();
    Super::EndPlay(Reason);
}

#undef LOCTEXT_NAMESPACE
