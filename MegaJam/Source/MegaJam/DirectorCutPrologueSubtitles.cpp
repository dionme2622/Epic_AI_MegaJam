#include "DirectorCutPrologueSubtitles.h"
#include "Engine/GameViewportClient.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Components/StaticMeshComponent.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SScaleBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"

namespace
{
const TCHAR* CaptionTags[] = {TEXT("PrologueCaption01"),TEXT("PrologueCaption02"),TEXT("PrologueCaption03"),TEXT("PrologueCaption04")};
const TCHAR* CaptionKo[] = {TEXT("각오해라, 드래곤!!!"),TEXT("크하하!! 통구이로 만들어주지!!!!!!"),TEXT("잠깐… 내 다리는 어디 갔지?"),TEXT("화면에 안 나온다고 다리를 떼어 가?")};
const TCHAR* CaptionEn[] = {TEXT("Prepare yourself, dragon!"),TEXT("Ha ha ha! I'll roast you alive!"),TEXT("Wait... Where did my legs go?"),TEXT("You took my legs because they were off camera?")};
}
void UDirectorCutPrologueSubtitles::OnWorldBeginPlay(UWorld& World)
{
    Super::OnWorldBeginPlay(World);
    if (!World.IsGameWorld() || !World.GetOutermost()->GetName().EndsWith(TEXT("L_BossPrologue"))) return;
    Captions.SetNum(4);
    for (TActorIterator<AStaticMeshActor> It(&World); It; ++It)
        for (int32 i=0;i<4;++i) if (It->ActorHasTag(FName(CaptionTags[i])))
        {
            Captions[i]=*It;
            // Sequencer continues driving actor visibility; only the old image mesh is hidden.
            It->GetStaticMeshComponent()->SetVisibility(false);
        }
    UGameViewportClient* Viewport=World.GetGameViewport();
    if (!Viewport) return;
    auto TextLine=[this](int32 Line,int32 Size,FLinearColor Color)
    {
        return SNew(STextBlock).Text_Lambda([this,Line]
        {
            if (ActiveCaption==INDEX_NONE) return FText::GetEmpty();
            if (Line==0) return FText::FromString(ActiveCaption==0?TEXT("용사 (Hero)"):TEXT("드래곤 (Dragon)"));
            return FText::FromString(Line==1?CaptionKo[ActiveCaption]:CaptionEn[ActiveCaption]);
        }).Font(FCoreStyle::GetDefaultFontStyle("Regular",Size)).ColorAndOpacity(Color)
          .Justification(ETextJustify::Center).WrapTextAt(1260);
    };
    Overlay=SNew(SOverlay).Visibility(EVisibility::SelfHitTestInvisible)
      +SOverlay::Slot().HAlign(HAlign_Fill).VAlign(VAlign_Bottom).Padding(70,0,70,55)
      [ SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::DownOnly)
        .Visibility_Lambda([this]{return ActiveCaption!=INDEX_NONE?EVisibility::HitTestInvisible:EVisibility::Collapsed;})
        [ SNew(SBox).WidthOverride(1350)
          [ SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
            .BorderBackgroundColor(FLinearColor(.005f,.01f,.018f,.85f)).Padding(FMargin(36,12))
            [ SNew(SVerticalBox)
              +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,6)[TextLine(0,20,FLinearColor(.92f,.71f,.35f))]
              +SVerticalBox::Slot().AutoHeight()[TextLine(1,30,FLinearColor(.95f,.94f,.87f))]
              +SVerticalBox::Slot().AutoHeight().Padding(0,5,0,0)[TextLine(2,23,FLinearColor(.82f,.85f,.88f))]
            ]
          ]
        ]
      ];
    Viewport->AddViewportWidgetContent(Overlay.ToSharedRef(),1000);
}
void UDirectorCutPrologueSubtitles::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    ActiveCaption=INDEX_NONE;
    for(int32 i=0;i<Captions.Num();++i)
        if(Captions[i].IsValid()&&!Captions[i]->IsHidden()){ActiveCaption=i;break;}
}
void UDirectorCutPrologueSubtitles::Deinitialize()
{
    if(Overlay) if(UGameViewportClient* V=GetWorld()->GetGameViewport()) V->RemoveViewportWidgetContent(Overlay.ToSharedRef());
    Overlay.Reset();Super::Deinitialize();
}
TStatId UDirectorCutPrologueSubtitles::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UDirectorCutPrologueSubtitles,STATGROUP_Tickables);
}
