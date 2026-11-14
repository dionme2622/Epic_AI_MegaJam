import unreal as u
api=u.get_editor_subsystem(u.EditorActorSubsystem); levels=u.get_editor_subsystem(u.LevelEditorSubsystem);lib=u.EditorAssetLibrary
def actors():return {a.get_actor_label():a for a in api.get_all_level_actors()}
def make_text(a,label,text,location,size=48,color=(255,221,140,255)):
 obj=a.get(label)
 if not obj:
  obj=api.spawn_actor_from_class(u.TextRenderActor,u.Vector(*location),u.Rotator(0,0,90));obj.set_actor_label(label)
 obj.set_actor_location(u.Vector(*location),False,True);obj.set_folder_path('Stage3/New Puzzles')
 c=obj.get_component_by_class(u.TextRenderComponent);c.set_text(text);c.set_world_size(size);c.set_text_render_color(u.Color(*color));c.set_horizontal_alignment(u.HorizTextAligment.EHTA_CENTER)
 a[label]=obj;return obj
def mesh(a,label,path,location,scale=(1,1,1)):
 obj=a.get(label)
 if not obj:
  obj=api.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*location),u.Rotator());obj.set_actor_label(label)
 obj.set_actor_location(u.Vector(*location),False,True);obj.set_actor_scale3d(u.Vector(*scale));obj.set_folder_path('Stage3/New Puzzles')
 c=obj.static_mesh_component;c.set_static_mesh(lib.load_asset(path));c.set_collision_profile_name('NoCollision');c.set_cast_shadow(False)
 a[label]=obj;return obj
assert levels.load_level('/Game/Stage3Integrated/Sections/L_Bloom')
a=actors();controller=a['Bloom_Controller']
controller.set_editor_property('bUseFilmEditing',False);controller.set_editor_property('bUseShutterPuzzle',True);controller.set_editor_property('TargetShutterMask',5)
for old in controller.get_editor_property('FilmScenes'):
 if old:old.set_actor_hidden_in_game(True)
clues=[]
for x,name,state in [(350,'STAR','OPEN'),(900,'MOON','CLOSED'),(1450,'SUN','OPEN')]:
 c=make_text(a,'Bloom Shutter Clue '+name,state,(x,-105,278),57,(255,221,126,255));c.set_actor_hidden_in_game(True);clues.append(c)
controller.set_editor_property('ShutterClues',clues)
if 'Bloom_Instructions' in a:a['Bloom_Instructions'].get_component_by_class(u.TextRenderComponent).set_text('B: BLOOM OFF  |  READ THE SHUTTERS')
if 'Bloom_ConsoleLabel' in a:a['Bloom_ConsoleLabel'].get_component_by_class(u.TextRenderComponent).set_text('E: LIGHT BOARD')
assert levels.save_current_level()
assert levels.load_level('/Game/Stage3Integrated/Sections/L_Resolution')
a=actors();controller=a['Resolution_Controller']
controller.set_editor_property('bUseStationChoices',False);controller.set_editor_property('bUseReelHunt',True);controller.set_editor_property('ReelSequence',[2,1,3]);controller.set_editor_property('ReelInteractionDistance',225.0)
for old in controller.get_editor_property('GuidanceArrows'):
 if old:old.set_actor_hidden_in_game(True)
for i in range(1,6):
 old=a.get('Resolution_DotPattern_'+str(i))
 if old:old.set_actor_hidden_in_game(True)
for i in range(1,4):
 old=a.get('Resolution_Guide_'+str(i))
 if old:old.set_actor_hidden_in_game(True)
stations=[]
for x,symbol in [(400,'Star'),(720,'Moon'),(1040,'Sun')]:
 station=mesh(a,'Reel Station '+symbol,'/Game/Stage3Integrated/Archive/SM_S3_Bloom'+symbol,(x,-155,160),(.72,.72,.72));stations.append(station)
 make_text(a,'Reel Station Label '+symbol,symbol.upper()+'  [E]',(x,-125,265),32)
controller.set_editor_property('ReelStations',stations)
# A framed low-resolution monitor: the film order is revealed only in LOW.
monitor=mesh(a,'Film Decoder Frame','/Engine/BasicShapes/Cube',(720,-255,382),(9,.10,.84))
monitor.static_mesh_component.set_material(0,lib.load_asset('/Game/Stage4Integrated/Theatre/M09_Iron'))
hint=make_text(a,'Film Decoder Low Resolution Clue','MOON  >  STAR  >  SUN',(720,-230,374),54,(255,222,128,255));hint.set_actor_hidden_in_game(True)
controller.set_editor_property('GuidanceArrows',[hint])
make_text(a,'Film Decoder Header','LOW-RES FILM DECODER',(720,-230,435),30)
assert levels.save_current_level()
assert levels.load_level('/Game/DirectorCut/Stage/Stage3_')
a=actors()
for i in (2,4):
 old=a.get('Archive Mosaic Frame '+str(i))
 if old:old.set_actor_hidden_in_game(True)
assert levels.save_current_level()
u.log('STAGE3 NEW SHUTTER AND REEL PUZZLES SAVED')
