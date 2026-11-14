import unreal,json,traceback
out={}
try:
 base='/Game/DirectorCut/Dragon/Upper/'
 source=unreal.load_asset(base+'SK_Dragon_UpperArmature_Run')
 idle=unreal.load_asset(base+'SK_Dragon_UpperArmature_Idle')
 n=unreal.AnimationLibrary.get_num_keys(source)
 poses=[unreal.AnimationLibrary.get_bone_pose_for_frame(source,'root',i,False) for i in range(n)]
 r=poses[0].rotation
 assert all(abs(abs(p.rotation.x*r.x+p.rotation.y*r.y+p.rotation.z*r.z+p.rotation.w*r.w)-1)<0.0001 for p in poses), 'Root rotation varies: refusing to replace animation.'
 path=base+'SK_Dragon_UpperArmature_Run_Upright'
 assert not unreal.EditorAssetLibrary.does_asset_exist(path), 'Destination already exists'
 a=unreal.EditorAssetLibrary.duplicate_asset(base+'SK_Dragon_UpperArmature_Run',path);assert a
 q=unreal.AnimationLibrary.get_bone_pose_for_frame(idle,'root',0,False).rotation
 assert a.get_editor_property('controller').set_bone_track_keys('root',[p.translation for p in poses],[q]*n,[p.scale3d for p in poses])
 assert unreal.EditorAssetLibrary.save_loaded_asset(a,only_if_is_dirty=False)
 out={'success':True,'frames':n,'asset':path,'rotation':str(q)}
except:out['error']=traceback.format_exc()
open('C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/run_upright_result.json','w').write(json.dumps(out,indent=2))
