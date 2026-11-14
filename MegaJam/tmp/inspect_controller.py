import unreal,json
c=unreal.load_asset('/Game/DirectorCut/Dragon/Upper/SK_Dragon_UpperArmature_Idle').get_editor_property('controller')
ns=[x for x in dir(c) if not x.startswith('_')]
out={'methods':ns}
for n in ['initialize_model','set_model','populate_with_existing_model','open_bracket','close_bracket','add_bone_track','set_bone_track_keys','set_number_of_frames','set_frame_rate']:
 if hasattr(c,n):out[n]=str(getattr(c,n).__doc__)
open('C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/controller.json','w').write(json.dumps(out,indent=2))
