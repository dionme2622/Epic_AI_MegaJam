import unreal as u
import sys
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
assert world
graphics=u.get_world_subsystem(world,u.load_class(None,"/Script/MegaJam.DirectorCutGraphicsSubsystem"))
graphics.set_high(u.DirectorCutGraphicsOption.SHADOWS,sys.argv[1]=="on")
