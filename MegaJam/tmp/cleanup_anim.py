import unreal,json
p='/Game/DirectorCut/Dragon/Upper/SK_Dragon_UpperArmature_Idle_OrientationTest'
result=unreal.EditorAssetLibrary.delete_asset(p)
open('C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/cleanup.json','w').write(json.dumps({'deleted_test':result}))
