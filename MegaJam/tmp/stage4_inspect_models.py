import unreal
from pathlib import Path
result=[]
paths = [
'/Game/DirectorCut/Dragon/Origin/SK_Dragon_Origin',
'/Game/DirectorCut/Dragon/SM_Dragon_Lower',
'/Game/ShadowBodyStage/SM_DragonLowerBody',
]
for path in paths:
    a=unreal.load_asset(path)
    result.append(str(a))
    if not a: continue
    result.append(str([x for x in dir(a) if any(k in x for k in ('bone','bounds','material','section','socket'))]))
    for method in ('get_bounding_box','get_bounds'):
        if hasattr(a,method):
            try: result.append(str(getattr(a,method)()))
            except Exception as e: result.append(str(e))
    if isinstance(a,unreal.SkeletalMesh):
        component=unreal.SkeletalMeshComponent()
        component.set_skeletal_mesh_asset(a)
        for i in range(component.get_num_bones()):
            n=component.get_bone_name(i)
            result.append(str(n) + ' ' + str(component.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT)))
result.append(str([x for x in dir(unreal.LevelEditorSubsystem) if 'level' in x or 'viewport' in x]))
Path(r'C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/stage4_models.txt').write_text('\n'.join(result),encoding='utf-8')
