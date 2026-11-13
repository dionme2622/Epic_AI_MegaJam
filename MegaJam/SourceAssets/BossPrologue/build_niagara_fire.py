"""Create a procedural Niagara dragon breath; no flipbook/image dependency."""
import unreal

P = '/Game/DirectorCut/Prologue/Cinematic/'
lib = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
ml = unreal.MaterialEditingLibrary
mat = unreal.load_asset(P+'M_Niagara_DragonFire') if lib.does_asset_exist(P+'M_Niagara_DragonFire') else at.create_asset('M_Niagara_DragonFire',P,unreal.Material,unreal.MaterialFactoryNew())
ml.delete_all_material_expressions(mat)
mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property('two_sided',True)
mat.set_editor_property('used_with_niagara_sprites',True)
def node(cls): return ml.create_material_expression(mat,cls)
def wire(a,b,pin='',out=''): ml.connect_material_expressions(a,out,b,pin)
uv=node(unreal.MaterialExpressionTextureCoordinate)
custom=node(unreal.MaterialExpressionCustom)
custom.set_editor_property('code', 'float2 p=(UV-0.5)*2; float r=length(p); float a=pow(saturate(1-r),1.7); return float4(lerp(float3(5,0.12,0.005),float3(14,5,0.15),a),a);')
custom.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT4)
inp=unreal.CustomInput(); inp.set_editor_property('input_name','UV')
custom.set_editor_property('inputs',[inp]); wire(uv,custom,'UV')
rgb=node(unreal.MaterialExpressionComponentMask); rgb.set_editor_property('r',True); rgb.set_editor_property('g',True); rgb.set_editor_property('b',True)
wire(custom,rgb); ml.connect_material_property(rgb,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
alpha=node(unreal.MaterialExpressionComponentMask); alpha.set_editor_property('a',True); alpha.set_editor_property('r',False); alpha.set_editor_property('g',False)
wire(custom,alpha)
pc=node(unreal.MaterialExpressionParticleColor)
mul=node(unreal.MaterialExpressionMultiply); wire(alpha,mul,'A'); wire(pc,mul,'B','A')
ml.connect_material_property(mul,'',unreal.MaterialProperty.MP_OPACITY)
ml.recompile_material(mat); lib.save_loaded_asset(mat)

path=P+'NS_DragonBreath'
system=unreal.load_asset(path) if lib.does_asset_exist(path) else at.duplicate_asset('NS_DragonBreath',P,unreal.load_asset('/Niagara/DefaultAssets/Templates/Systems/FountainLightweight'))
prefix=system.get_path_name()+':'
objs=[o for o in unreal.ObjectIterator() if isinstance(o,unreal.Object) and unreal.SystemLibrary.get_path_name(o).startswith(prefix)]
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def setprop(obj, prop, value):
 unreal.SystemLibrary.execute_console_command(w,'set '+unreal.SystemLibrary.get_path_name(obj)+' '+prop+' '+value)
for o in objs:
 name=o.get_class().get_name()
 if name=='NiagaraStatelessEmitter':
  setprop(o,'SpawnInfos','((Type=Rate,Rate=(Min=240,Max=240)))')
  setprop(o,'FixedBounds','(Min=(X=-1200,Y=-400,Z=-400),Max=(X=1200,Y=400,Z=400),IsValid=1)')
 if name=='NiagaraSpriteRendererProperties': o.set_editor_property('material',mat)
 if name=='NiagaraStatelessModule_InitializeParticle':
  setprop(o,'LifetimeDistribution','(Mode=UniformRange,Min=0.35,Max=0.65)')
  setprop(o,'SpriteSizeDistribution','(Mode=NonUniformRange,Min=(X=35,Y=35),Max=(X=100,Y=100))')
 if name=='NiagaraStatelessModule_AddVelocity':
  setprop(o,'VelocityType','Linear')
  setprop(o,'LinearVelocityDistribution','(Mode=NonUniformRange,Min=(X=-1000,Y=-95,Z=-75),Max=(X=-700,Y=95,Z=100))')
 if name in ['NiagaraStatelessModule_GravityForce','NiagaraStatelessModule_AccelerationForce','NiagaraStatelessModule_ShapeLocation']:
  setprop(o,'bModuleEnabled','False')
lib.save_loaded_asset(system)
unreal.log('NIAGARA_FIRE_BUILT '+system.get_path_name())
