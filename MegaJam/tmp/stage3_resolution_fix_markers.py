import unreal as u

world = u.get_editor_subsystem(u.UnrealEditorSubsystem)
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
assert world.get_editor_world().get_path_name() == "/Game/DirectorCut/Stage/Stage3_.Stage3_"
assert levels.load_level("/Game/Stage3Integrated/Sections/L_Resolution")
items = {actor.get_actor_label(): actor for actor in actors.get_all_level_actors()}
controller = items["Resolution_Controller"]
markers = [items[f"Archive Resolution Choice {index}"] for index in range(1, 4)]
assert list(controller.get_editor_property("GuidanceArrows")) == markers
for index, marker in enumerate(markers, 1):
    marker.modify()
    marker.set_actor_location(u.Vector([400, 720, 1040][index - 1], -170, 160), False, True)
    component = marker.get_component_by_class(u.TextRenderComponent)
    component.modify()
    component.set_world_size(120)
    component.set_horizontal_alignment(u.HorizTextAligment.EHTA_CENTER)
    component.set_vertical_alignment(u.VerticalTextAligment.EVRTA_TEXT_CENTER)
    component.set_text_render_color(u.Color(43, 23, 40, 255))
assert levels.save_current_level()
assert levels.load_level("/Game/DirectorCut/Stage/Stage3_")
u.log("STAGE3 RESOLUTION MARKERS ADJUSTED")
