#include "Stage4RgbPanel.h"

#include "Brushes/SlateNoResource.h"
#include "Brushes/SlateRoundedBoxBrush.h"
#include "ColorSignalPuzzle.h"
#include "DirectorCutGraphics.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "Layout/Clipping.h"
#include "Rendering/DrawElements.h"
#include "Styling/CoreStyle.h"
#include "UObject/StrongObjectPtr.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SConstraintCanvas.h"
#include "Widgets/Layout/SScaleBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SLeafWidget.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"

#define LOCTEXT_NAMESPACE "Stage4RgbPanel"

namespace
{
    constexpr float ArtworkWidth = 1672.f;
    constexpr float ArtworkHeight = 941.f;
    constexpr float DialCenters[] = {450.f, 836.f, 1221.f};
    constexpr float DialY = 524.f;
    constexpr float DialAngles[] = {-137.f, -106.f, -74.f, -43.f};
    static_assert(UE_ARRAY_COUNT(DialAngles) == AColorSignalPuzzle::RgbMaxLevel + 1);

    const FLinearColor Brass = FColor::FromHex(TEXT("FFE6AF"));
    const FLinearColor IndicatorColors[] = {
        FColor::FromHex(TEXT("FF303D")),
        FColor::FromHex(TEXT("72F544")),
        FColor::FromHex(TEXT("397CFF")),
    };
    const FSlateRoundedBoxBrush Jewel(FLinearColor::White, 10.f);
    const FSlateRoundedBoxBrush StatusPlate(FLinearColor(FColor::FromHex(TEXT("372015"))), 10.f, Brass, 1.f);
    const FSlateRoundedBoxBrush Keycap(Brass, 5.f);

    using FPuzzleRef = TWeakObjectPtr<AColorSignalPuzzle>;

    class FConsolePaint
    {
    public:
        FConsolePaint(const FGeometry& InGeometry, FSlateWindowElementList& InElements, int32 InLayer)
            : Geometry(InGeometry), Elements(InElements), Layer(InLayer)
        {
        }

        FPaintGeometry At(FVector2f Position, FVector2f Size) const
        {
            return Geometry.ToPaintGeometry(Size, FSlateLayoutTransform(Position));
        }

        void Box(const FSlateBrush& Brush, FVector2f Position, FVector2f Size, FLinearColor Tint, int32 Depth = 0) const
        {
            FSlateDrawElement::MakeBox(Elements, Layer + Depth, At(Position, Size), &Brush, ESlateDrawEffect::None, Tint);
        }

        void Line(FVector2f From, FVector2f To, FLinearColor Tint, float Thickness, int32 Depth) const
        {
            FSlateDrawElement::MakeLines(Elements, Layer + Depth, Geometry.ToPaintGeometry(),
                TArray<FVector2f>{From, To}, ESlateDrawEffect::None, Tint, true, Thickness);
        }

        void Triangle(FVector2f A, FVector2f B, FVector2f C, FLinearColor Light, FLinearColor Shadow, int32 Depth) const
        {
            TArray<FSlateVertex> Vertices;
            Vertices.Add(Vertex(A, Light));
            Vertices.Add(Vertex(B, Shadow));
            Vertices.Add(Vertex(C, Light));
            Mesh(Vertices, {0, 1, 2}, Depth);
        }

        // Multiple rings share vertices to shade the curved metal and glass continuously.
        void Disc(FVector2f Center, float Radius, TConstArrayView<float> Rings,
            TFunctionRef<FLinearColor(int32, float)> Shade, int32 Depth = 1) const
        {
            constexpr int32 Segments = 80;
            TArray<FSlateVertex> Vertices;
            TArray<SlateIndex> Indices;
            Vertices.Reserve(Rings.Num() * Segments);
            Indices.Reserve((Rings.Num() - 1) * Segments * 6);
            for (int32 Ring = 0; Ring < Rings.Num(); ++Ring)
            {
                for (int32 Segment = 0; Segment < Segments; ++Segment)
                {
                    const float Angle = 2.f * UE_PI * Segment / Segments;
                    const FVector2f Radial(FMath::Cos(Angle), FMath::Sin(Angle));
                    const float RingRadius = Rings[Ring];
                    Vertices.Add(Vertex(Center + Radial * Radius * RingRadius, Shade(Ring, Radial.Y * RingRadius)));
                    if (Ring == 0)
                    {
                        continue;
                    }
                    const int32 Inner = (Ring - 1) * Segments;
                    const int32 Next = (Segment + 1) % Segments;
                    const SlateIndex A = Inner + Segment;
                    const SlateIndex B = Inner + Next;
                    const SlateIndex C = A + Segments;
                    const SlateIndex D = B + Segments;
                    Indices.Append({A, C, D, A, D, B});
                }
            }
            Mesh(Vertices, Indices, Depth);
        }

    private:
        FSlateVertex Vertex(FVector2f Position, FLinearColor Tint) const
        {
            return FSlateVertex::Make<ESlateVertexRounding::Disabled>(Geometry.GetAccumulatedRenderTransform(),
                Position, FVector2f(.5f, .5f), Tint.ToFColorSRGB());
        }

        void Mesh(const TArray<FSlateVertex>& Vertices, const TArray<SlateIndex>& Indices, int32 Depth) const
        {
            // Texture-free Slate geometry. Colors are supplied per vertex.
            FSlateDrawElement::MakeCustomVerts(Elements, Layer + Depth, FSlateResourceHandle(),
                Vertices, Indices, nullptr, 0, 0);
        }

        const FGeometry& Geometry;
        FSlateWindowElementList& Elements;
        int32 Layer;
    };

    void PaintMix(const FConsolePaint& Paint, FLinearColor Mixed, bool bLit)
    {
        constexpr float Rings[] = {0.f, .43f, .69f, .86f, .95f, .98f, 1.f};
        const FLinearColor Night = FColor::FromHex(TEXT("201719"));
        const FLinearColor Full = bLit ? Mixed : Night;
        const FLinearColor Rim = FColor::FromHex(TEXT("160E10"));
        const FLinearColor Shades[] = {
            bLit ? FMath::Lerp(Full, FLinearColor::White, .30f) : Full,
            bLit ? FMath::Lerp(Full, FLinearColor::White, .13f) : Full,
            Full * .86f, Full * .57f, Full * .28f, Rim, Rim,
        };
        Paint.Disc({836.f, 185.f}, 99.f, Rings, [&](int32 Ring, float Y)
        {
            const float Glint = .82f + .33f * FMath::Max(0.f, -Y);
            FLinearColor Color = Shades[Ring] * Glint;
            Color.A = 1.f;
            return Color;
        });
    }

    void PaintDial(const FConsolePaint& Paint, float CenterX, int32 Value)
    {
        const FVector2f Center(CenterX, DialY);
        constexpr float RingStops[] = {0.f, .49f, .53f, .58f, .65f, .68f, .74f, .91f, .98f, 1.f};
        const FColor RingColors[] = {
            FColor::FromHex(TEXT("24140D")), FColor::FromHex(TEXT("221209")), FColor::FromHex(TEXT("1D1008")),
            FColor::FromHex(TEXT("301A0C")), FColor::FromHex(TEXT("422710")), FColor::FromHex(TEXT("60421C")),
            FColor::FromHex(TEXT("B6813A")), FColor::FromHex(TEXT("B78340")), FColor::FromHex(TEXT("BB8A4B")),
            FColor::FromHex(TEXT("AC7837")),
        };
        Paint.Disc(Center, 121.f, RingStops, [&](int32 Ring, float Y)
        {
            FLinearColor Color = FLinearColor(RingColors[Ring]) * (1.f - Y * .55f);
            Color.A = 1.f;
            return Color;
        });

        for (const float Angle : DialAngles)
        {
            const float Radians = FMath::DegreesToRadians(Angle);
            const FVector2f Direction(FMath::Cos(Radians), FMath::Sin(Radians));
            Paint.Line(Center + Direction * 96.f + FVector2f(0.f, 2.f),
                Center + Direction * 115.f + FVector2f(0.f, 2.f), Brass, 8.f, 2);
            Paint.Line(Center + Direction * 96.f, Center + Direction * 115.f,
                FColor::FromHex(TEXT("1F100A")), 7.f, 3);
        }

        const float Heading = FMath::DegreesToRadians(DialAngles[Value]);
        const FVector2f Forward(FMath::Cos(Heading), FMath::Sin(Heading));
        const FVector2f Side(-Forward.Y, Forward.X);
        Paint.Triangle(Center + Forward * 110.f, Center + Forward * 46.f + Side * 13.f,
            Center + Forward * 46.f - Side * 13.f,
            FColor::FromHex(TEXT("FFF0B7")), FColor::FromHex(TEXT("9D641F")), 4);

        constexpr float KnobStops[] = {0.f, .68f, .88f, .92f, .98f, 1.f};
        const FColor KnobColors[] = {
            FColor::FromHex(TEXT("B47D39")), FColor::FromHex(TEXT("A87739")), FColor::FromHex(TEXT("9E6F32")),
            FColor::FromHex(TEXT("D8A852")), FColor::FromHex(TEXT("754B23")), FColor::FromHex(TEXT("3D2410")),
        };
        Paint.Disc(Center, 61.f, KnobStops, [&](int32 Ring, float Y)
        {
            FLinearColor Color = FLinearColor(KnobColors[Ring]) * (1.f - Y * .64f);
            Color.A = 1.f;
            return Color;
        }, 5);
    }

    void PaintIndicators(const FConsolePaint& Paint, float DialX, int32 Value, FLinearColor Tint)
    {
        for (int32 Index = 0; Index < AColorSignalPuzzle::RgbMaxLevel; ++Index)
        {
            const FVector2f TopLeft(DialX - 97.f + 66.f * Index, 619.f);
            const bool bLit = Index < Value;
            Paint.Box(Jewel, TopLeft, {60.f, 50.f}, FColor::FromHex(TEXT("1B1213")), 2);
            Paint.Box(Jewel, TopLeft + FVector2f(4.f, 4.f), {52.f, 42.f},
                bLit ? Tint : FLinearColor(FColor::FromHex(TEXT("332322"))), 3);
            Paint.Box(Jewel, TopLeft + FVector2f(7.f, 7.f), {46.f, 36.f},
                bLit ? FMath::Lerp(Tint, FLinearColor::White, .22f) : FLinearColor(FColor::FromHex(TEXT("412F2A"))), 4);
            Paint.Box(Jewel, TopLeft + FVector2f(10.f, 9.f), {40.f, 12.f},
                bLit ? FMath::Lerp(Tint, FLinearColor::White, .50f) : FLinearColor(FColor::FromHex(TEXT("543E35"))), 5);
        }
    }

    class SVaultConsoleArtwork : public SLeafWidget
    {
    public:
        SLATE_BEGIN_ARGS(SVaultConsoleArtwork) {}
            SLATE_ARGUMENT(FPuzzleRef, Puzzle)
            SLATE_ARGUMENT(UTexture2D*, Texture)
        SLATE_END_ARGS()

        void Construct(const FArguments& Args)
        {
            Puzzle = Args._Puzzle;
            Texture.Reset(Args._Texture);
            Artwork.SetResourceObject(Texture.Get());
            Artwork.SetImageSize(FVector2f(ArtworkWidth, ArtworkHeight));
            Artwork.DrawAs = ESlateBrushDrawType::Image;
        }

        virtual FVector2D ComputeDesiredSize(float) const override
        {
            return {ArtworkWidth, ArtworkHeight};
        }

        virtual int32 OnPaint(const FPaintArgs&, const FGeometry& Geometry, const FSlateRect&,
            FSlateWindowElementList& Elements, int32 Layer, const FWidgetStyle&, bool) const override
        {
            const FConsolePaint Paint(Geometry, Elements, Layer);
            Paint.Box(Artwork, {0.f, 0.f}, {ArtworkWidth, ArtworkHeight}, FLinearColor::White);
            const AColorSignalPuzzle* State = Puzzle.Get();
            if (!State || State->DialValues.Num() != AColorSignalPuzzle::RgbChannelCount)
            {
                return Layer;
            }

            const auto& Values = State->DialValues;
            constexpr float Max = AColorSignalPuzzle::RgbMaxLevel;
            const FLinearColor Mix(Values[0] / Max, Values[1] / Max, Values[2] / Max);
            // The physical title plate sits in front of the lower edge of the lens.
            Elements.PushClip(FSlateClippingZone(Paint.At({731.f, 81.f}, {210.f, 181.f})));
            PaintMix(Paint, Mix, Values[0] || Values[1] || Values[2]);
            Elements.PopClip();

            for (int32 Channel = 0; Channel < AColorSignalPuzzle::RgbChannelCount; ++Channel)
            {
                const float X = DialCenters[Channel];
                Elements.PushClip(FSlateClippingZone(Paint.At({X - 123.f, 398.f}, {246.f, 212.f})));
                PaintDial(Paint, X, FMath::Clamp(Values[Channel], 0, AColorSignalPuzzle::RgbMaxLevel));
                Elements.PopClip();
                PaintIndicators(Paint, X, Values[Channel], IndicatorColors[Channel]);
            }
            return Layer + 5;
        }

    private:
        FPuzzleRef Puzzle;
        TStrongObjectPtr<UTexture2D> Texture;
        FSlateBrush Artwork;
    };

    const FButtonStyle& ConsoleButtonStyle()
    {
        static const FButtonStyle Style = FButtonStyle()
            .SetNormal(FSlateNoResource())
            .SetHovered(FSlateRoundedBoxBrush(FLinearColor(1.f, .70f, .33f, .065f), 20.f))
            .SetPressed(FSlateRoundedBoxBrush(FLinearColor(1.f, .70f, .33f, .12f), 20.f))
            .SetDisabled(FSlateNoResource())
            .SetNormalPadding(FMargin(0))
            .SetPressedPadding(FMargin(0));
        return Style;
    }

    TSharedRef<SWidget> InstructionKey(const FText& Key, const FText& Label)
    {
        return SNew(SHorizontalBox)
            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)
            [
                SNew(SBorder).BorderImage(&Keycap).Padding(FMargin(8.f, 1.f))
                [
                    SNew(STextBlock).Text(Key).Font(FCoreStyle::GetDefaultFontStyle("Bold", 19))
                    .ColorAndOpacity(FLinearColor(FColor::FromHex(TEXT("291708"))))
                ]
            ]
            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(8.f, 0.f, 0.f, 0.f)
            [
                SNew(STextBlock).Text(Label).Font(FCoreStyle::GetDefaultFontStyle("Regular", 21))
                .ColorAndOpacity(Brass)
            ];
    }

    void AddControl(SConstraintCanvas& Canvas, FPuzzleRef Puzzle, FMargin Bounds, FText Label,
        TFunction<void(AColorSignalPuzzle&)> Action, bool bShowLabel)
    {
        Canvas.AddSlot()
        .Anchors(FAnchors(0.f, 0.f))
        .Alignment(FVector2D::ZeroVector)
        .Offset(Bounds)
        [
            SNew(SButton)
            .ButtonStyle(&ConsoleButtonStyle())
            .Cursor(EMouseCursor::Hand)
            .IsFocusable(false)
            .IsEnabled_Lambda([Puzzle] { return Puzzle.IsValid() && Puzzle->bActive && !Puzzle->bSolved; })
            .AccessibleText(Label)
            .Text(Label)
            .ForegroundColor(bShowLabel ? Brass : FLinearColor::Transparent)
            .HAlign(HAlign_Center)
            .VAlign(VAlign_Center)
            .OnClicked_Lambda([Puzzle, Action = MoveTemp(Action)]
            {
                if (AColorSignalPuzzle* State = Puzzle.Get(); State && State->bActive && !State->bSolved)
                {
                    const auto* Controller = Cast<ADirectorCutPlayerController>(State->GetWorld()->GetFirstPlayerController());
                    if (!Controller || !Controller->IsGraphicsMenuOpen())
                    {
                        Action(*State);
                    }
                }
                return FReply::Handled();
            })
        ];
    }
}

TSharedRef<SWidget> BuildStage4RgbPanel(AColorSignalPuzzle& Puzzle)
{
    UTexture2D* ArtworkTexture = LoadObject<UTexture2D>(nullptr,
        TEXT("/Game/Stage4Integrated/UI/T_Stage4VaultConsole.T_Stage4VaultConsole"));
    const FPuzzleRef State(&Puzzle);
    const TSharedRef<SConstraintCanvas> Controls = SNew(SConstraintCanvas).Visibility(EVisibility::SelfHitTestInvisible);
    const FText Channels[] = {
        LOCTEXT("RedControl", "Step Red"), LOCTEXT("GreenControl", "Step Green"), LOCTEXT("BlueControl", "Step Blue"),
    };
    for (int32 Channel = 0; Channel < AColorSignalPuzzle::RgbChannelCount; ++Channel)
    {
        AddControl(*Controls, State, {DialCenters[Channel] - 138.f, 323.f, 276.f, 350.f}, Channels[Channel],
            [Channel](AColorSignalPuzzle& Panel) { Panel.RotateDial(Channel); }, !ArtworkTexture);
    }
    AddControl(*Controls, State, {416.f, 815.f, 273.f, 76.f}, LOCTEXT("Reset", "Reset"),
        [](AColorSignalPuzzle& Panel) { Panel.ResetDials(); }, !ArtworkTexture);
    AddControl(*Controls, State, {988.f, 815.f, 270.f, 76.f}, LOCTEXT("Exit", "Exit"),
        [](AColorSignalPuzzle& Panel) { Panel.LeavePuzzle(); }, !ArtworkTexture);

    Controls->AddSlot()
    .Anchors(FAnchors(0.f, 0.f))
    .Alignment(FVector2D::ZeroVector)
    .Offset(FMargin(220.f, 707.f, 1232.f, 88.f))
    [
        SNew(SBorder).BorderImage(&StatusPlate).HAlign(HAlign_Center).VAlign(VAlign_Center)
        .Visibility(EVisibility::HitTestInvisible)
        [
            SNew(SVerticalBox)
            + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)
            [
                SNew(STextBlock)
                .Text_Lambda([State]
                {
                    return State.IsValid() && State->bSolved
                        ? LOCTEXT("Unlocked", "VAULT UNLOCKED")
                        : LOCTEXT("Clue", "Blue leads. Red is one step above green. No channel is dark.");
                })
                .Font(FCoreStyle::GetDefaultFontStyle("Bold", 30))
                .ColorAndOpacity(Brass)
            ]
            + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0.f, 3.f, 0.f, 0.f)
            [
                SNew(SHorizontalBox)
                .Visibility_Lambda([State]
                {
                    return State.IsValid() && State->bSolved ? EVisibility::Collapsed : EVisibility::HitTestInvisible;
                })
                + SHorizontalBox::Slot().AutoWidth().Padding(0.f, 0.f, 25.f, 0.f)
                [InstructionKey(LOCTEXT("ChannelKeys", "1 / 2 / 3"), LOCTEXT("ChangeChannels", "Step each color or click its dial"))]
                + SHorizontalBox::Slot().AutoWidth().Padding(0.f, 0.f, 25.f, 0.f)
                [InstructionKey(LOCTEXT("ResetKey", "R"), LOCTEXT("Reset", "Reset"))]
                + SHorizontalBox::Slot().AutoWidth().Padding(0.f, 0.f, 25.f, 0.f)
                [InstructionKey(LOCTEXT("ExitKey", "E"), LOCTEXT("Exit", "Exit"))]
                + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)
                [
                    SNew(STextBlock).Text(LOCTEXT("AutomaticCheck", "Checks after each change"))
                    .Font(FCoreStyle::GetDefaultFontStyle("Regular", 21))
                    .ColorAndOpacity(Brass)
                ]
            ]
        ]
    ];

    return SNew(SOverlay).Visibility(EVisibility::SelfHitTestInvisible)
        + SOverlay::Slot()
        [
            SNew(SBorder)
            .Padding(0)
            .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
            .BorderBackgroundColor(FLinearColor(0.f, 0.f, 0.f, .88f))
            .Visibility(EVisibility::HitTestInvisible)
        ]
        + SOverlay::Slot().Padding(16.f, 10.f)
        [
            SNew(SScaleBox)
            .Stretch(EStretch::ScaleToFit)
            .StretchDirection(EStretchDirection::Both)
            [
                SNew(SBox).WidthOverride(ArtworkWidth).HeightOverride(ArtworkHeight)
                [
                    SNew(SOverlay).Visibility(EVisibility::SelfHitTestInvisible)
                    + SOverlay::Slot()
                    [
                        SNew(SVaultConsoleArtwork)
                        .Visibility(EVisibility::HitTestInvisible)
                        .AccessibleText(LOCTEXT("ArtworkDescription", "Vault Light Console"))
                        .ForceVolatile(true)
                        .Puzzle(State)
                        .Texture(ArtworkTexture)
                    ]
                    + SOverlay::Slot()
                    [
                        Controls
                    ]
                ]
            ]
        ];
}

#undef LOCTEXT_NAMESPACE
