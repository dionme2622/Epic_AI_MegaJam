#include "DirectorCutWallNote.h"

#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

#define LOCTEXT_NAMESPACE "DirectorCutWallNote"

ADirectorCutWallNote::ADirectorCutWallNote()
{
    auto* Mount = CreateDefaultSubobject<USceneComponent>(TEXT("Mount"));
    SetRootComponent(Mount);

    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> Paper(
        TEXT("/Game/Stage1Generated/Refined/M_Dev_Paper.M_Dev_Paper"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> InkMaterial(
        TEXT("/Game/Stage4Integrated/Theatre/M03_Slate.M03_Slate"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> Brass(
        TEXT("/Game/Stage4Integrated/Theatre/M06_Gold.M06_Gold"));

    const auto AddDetail = [this, Mount](FName Name, UStaticMesh* Mesh, UMaterialInterface* Material,
        const FVector& Location, const FVector& Scale)
    {
        auto* Detail = CreateDefaultSubobject<UStaticMeshComponent>(Name);
        Detail->SetupAttachment(Mount);
        Detail->SetStaticMesh(Mesh);
        Detail->SetMaterial(0, Material);
        Detail->SetRelativeLocation(Location);
        Detail->SetRelativeScale3D(Scale);
        Detail->SetCollisionProfileName(TEXT("NoCollision"));
        Detail->SetCastShadow(false);
        return Detail;
    };

    AddDetail(TEXT("Sheet"), Cube.Object, Paper.Object, {0., .85, 0.}, {.37, .017, .45})
        ->SetRelativeRotation(FRotator(4., 0., 0.));
    AddDetail(TEXT("Pin"), Sphere.Object, Brass.Object, {0., 2.4, 15.}, {.059, .043, .059});
    AddDetail(TEXT("InkHeading"), Cube.Object, InkMaterial.Object, {1., 2.4, 6.5}, {.21, .009, .025});
    AddDetail(TEXT("InkLineOne"), Cube.Object, InkMaterial.Object, {-1., 2.4, -1.5}, {.25, .009, .014});
    AddDetail(TEXT("InkLineTwo"), Cube.Object, InkMaterial.Object, {1., 2.4, -7.5}, {.21, .009, .014});
    AddDetail(TEXT("InkLineThree"), Cube.Object, InkMaterial.Object, {-2.5, 2.4, -13.5}, {.14, .009, .014});
}

bool ADirectorCutWallNote::IsInReach(const FVector& PlayerPosition) const
{
    const FVector Offset = GetActorTransform().InverseTransformPositionNoScale(PlayerPosition);
    // The character is on the side-scrolling track in front of the back wall.
    return FMath::Abs(Offset.X) <= InteractionDistance && FMath::Abs(Offset.Z) <= 150.
        && Offset.Y >= -5. && Offset.Y <= 400.;
}

FVector ADirectorCutWallNote::GetPromptAnchor() const
{
    return GetActorTransform().TransformPosition({0., 6., 31.});
}

void ADirectorCutWallNote::GetText(FText& Korean, FText& English) const
{
    switch (Note)
    {
    case EDirectorCutWallNote::Wheel:
        Korean = LOCTEXT("WheelKo", "그래픽 설정의 Model Detail에 따라 바퀴 모양이 달라짐. 둥근 원본은 잘 굴러감. 각진 검수본은 황동 받침 위에서 미끄러지지 않음.");
        English = LOCTEXT("WheelEn", "The wheel changes shape with Model Detail. The round master rolls freely. The angular proof holds on the brass cradle.");
        break;
    case EDirectorCutWallNote::Lens:
        Korean = LOCTEXT("LensKo", "소품은 두 조각으로 제작. 카메라에서 봤을 땐 열쇠 하나처럼 보여야 함.");
        English = LOCTEXT("LensEn", "The prop comes in two pieces. Through the lens it should look like a single key.");
        break;
    case EDirectorCutWallNote::TwoTakes:
        Korean = LOCTEXT("TwoTakesKo", "두 표시등이 한 프레임에 켜져야 함. 첫 번째 테이크는 지우지 말 것.");
        English = LOCTEXT("TwoTakesEn", "Both lamps need to show in the same frame. Keep the first take.");
        break;
    case EDirectorCutWallNote::Projection:
        Korean = LOCTEXT("ProjectionKo", "그래픽 설정의 Resolution에 따라 같은 필름도 다르게 보인다. 작은 검수본에선 잔흠집이 묻혀 이어 붙인 자리가 더 잘 보인다.");
        English = LOCTEXT("ProjectionEn", "The same film looks different at each Resolution setting. Fine scratches vanish on the small proof, making the splices easier to see.");
        break;
    case EDirectorCutWallNote::VaultLighting:
        Korean = LOCTEXT("LightingKo", "파란 조명이 가장 밝다. 빨강은 초록보다 한 칸 위. 모든 조명은 켜둔다.");
        English = LOCTEXT("LightingEn", "Blue gets top billing. Red sits one notch above green. Every lamp stays lit.");
        break;
    case EDirectorCutWallNote::ShadowRetake:
        Korean = LOCTEXT("RetakeKo", "지난 테이크에선 성벽 그림자의 윤곽이 벽에 그린 선과 딱 맞았다.");
        English = LOCTEXT("RetakeEn", "In the last take, the castle shadow fit the outline painted on the wall.");
        break;
    case EDirectorCutWallNote::ShadowFerry:
        Korean = LOCTEXT("FerryKo", "스위치는 배우 대신 그림자에 반응한다. 대기 신호가 남아 있으면 발판도 정지 상태.");
        English = LOCTEXT("FerryEn", "The switches respond to shadows. As long as the hold signal stays lit, so does the ferry brake.");
        break;
    case EDirectorCutWallNote::UpperSwitch:
        Korean = LOCTEXT("UpperSwitchKo", "위쪽 스위치의 촬영 기록은 신호가 끊겼다 돌아올 때 갱신된다.");
        English = LOCTEXT("UpperSwitchEn", "The upper switch logs a new take when it sees the signal return.");
        break;
    }
}

#undef LOCTEXT_NAMESPACE
