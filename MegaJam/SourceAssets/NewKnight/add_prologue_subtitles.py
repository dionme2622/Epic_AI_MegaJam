import unreal
from pathlib import Path

P='/Game/Assets/Prologue/'
src=Path(r'D:\UnrealProject\Epic_AI_MegaJam\MegaJam\SourceAssets\NewKnight\Subtitles')
asset_tools=unreal.AssetToolsHelpers.get_asset_tools()
seq=unreal.load_asset(P+'LS_Prologue_LastBattle_v4')
assert seq
camera=next(a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label()=='Prologue_Camera')
plane=unreal.load_asset('/Engine/BasicShapes/Plane')

tasks=[]
for p in sorted(src.glob('*.png')):
    t=unreal.AssetImportTask();t.filename=str(p);t.destination_path=P+'Subtitles'
    t.automated=True;t.save=True;t.replace_existing=False;tasks.append(t)
asset_tools.import_asset_tasks(tasks)

mat=asset_tools.create_asset('M_Bilingual_Subtitle',P,unreal.Material,unreal.MaterialFactoryNew())
mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT)
mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property('two_sided',True)
sample=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionTextureSampleParameter2D,-350,0)
sample.set_editor_property('parameter_name','Caption')
unreal.MaterialEditingLibrary.connect_material_property(sample,'RGB',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
unreal.MaterialEditingLibrary.connect_material_property(sample,'A',unreal.MaterialProperty.MP_OPACITY)
unreal.MaterialEditingLibrary.recompile_material(mat)

captions=[('01_Victory',0,300),('02_Dragon_Rises',390,690),('03_Missing',720,900),
 ('04_Dev_Note',900,1050),('05_Dev_Note2',1050,1170),('06_Protest',1170,1380),
 ('07_Crawl',1380,1650),('08_Storage',1650,1800)]
for name,start,end in captions:
    tex=unreal.load_asset(P+'Subtitles/'+name)
    assert tex,name
    mi=asset_tools.create_asset('MI_'+name,P+'Subtitles',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    mi.set_editor_property('parent',mat)
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(mi,'Caption',tex)
    a=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0))
    a.set_actor_label('Subtitle_'+name);a.static_mesh_component.set_static_mesh(plane)
    a.static_mesh_component.set_material(0,mi)
    a.attach_to_actor(camera,'',unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,False)
    a.set_actor_relative_location(unreal.Vector(500,0,-145),False,False)
    a.set_actor_relative_rotation(unreal.Rotator(90,0,0),False,False)
    a.set_actor_relative_scale3d(unreal.Vector(4.5,.45,1))
    b=seq.add_possessable(a)
    vt=b.add_track(unreal.MovieSceneVisibilityTrack)
    s=vt.add_section();s.set_range(0,1800)
    ch=s.get_all_channels()[0]
    ch.add_key(unreal.FrameNumber(0),False)
    ch.add_key(unreal.FrameNumber(start),True)
    ch.add_key(unreal.FrameNumber(end),False)
    unreal.EditorAssetLibrary.save_loaded_asset(mi)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
unreal.EditorAssetLibrary.save_loaded_asset(seq)
unreal.EditorLevelLibrary.save_current_level()
unreal.log('PROLOGUE_SUBTITLES_OK '+str(len(captions)))
