import unreal,json,traceback
out={}
try:
 base='/Game/DirectorCut/Dragon/Upper/'
 src=unreal.load_asset(base+'SK_Dragon_UpperArmature_Idle')
 test=unreal.EditorAssetLibrary.duplicate_asset(base+'SK_Dragon_UpperArmature_Idle',base+'SK_Dragon_UpperArmature_Idle_OrientationTest')
 assert test
 combat=unreal.load_asset(base+'SK_Dragon_UpperArmature_Combat_Idle')
 rot=unreal.AnimationLibrary.get_bone_pose_for_frame(combat,'root',0,False).rotation
 n=unreal.AnimationLibrary.get_num_keys(src)
 poses=[unreal.AnimationLibrary.get_bone_pose_for_frame(src,'root',i,False) for i in range(n)]
 c=test.get_editor_property('controller')
 out['rotation']=str(rot);out['count']=n
 out['success']=c.set_bone_track_keys('root',[p.translation for p in poses],[rot for p in poses],[p.scale3d for p in poses])
 unreal.EditorAssetLibrary.save_loaded_asset(test)
 out['after']=str(unreal.AnimationLibrary.get_bone_pose_for_frame(test,'root',0,False))
except:out['error']=traceback.format_exc()
open('C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/test_edit.json','w').write(json.dumps(out,indent=2))
