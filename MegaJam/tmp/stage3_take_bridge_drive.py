"""Drive the normal character movement in PIE to test the new sections."""
import json
from pathlib import Path

import unreal as u

base = Path(r'C:/LHH/Epic_AI_MegaJam/MegaJam/tmp')
command = base / 'stage3_drive_command.json'
status = base / 'stage3_drive_result.json'
editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
world = editor.get_game_world()
assert world
pawn = u.GameplayStatics.get_player_character(world, 0)
assert pawn
performance = u.get_default_object(u.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings'))
old_throttle = performance.get_editor_property('bThrottleCPUWhenNotForeground')
performance.set_editor_property('bThrottleCPUWhenNotForeground', False)
last = {'id': None, 'frames': 0, 'elapsed': 0., 'started': False}


def drive(delta):
    if not editor.get_game_world():
        u.unregister_slate_post_tick_callback(handle)
        performance.set_editor_property('bThrottleCPUWhenNotForeground', old_throttle)
        return
    if not command.exists():
        return
    try:
        task = json.loads(command.read_text())
    except (OSError, ValueError):
        return
    if last['id'] != task['id']:
        last.update(id=task['id'], frames=0, elapsed=0., started=False)
    position = pawn.get_actor_location()
    move = pawn.get_component_by_class(u.CharacterMovementComponent)
    goal = task['x']
    dx = goal - position.x
    last['elapsed'] += delta
    if task.get('attempt_fall'):
        if position.x >= 5440:
            last['started'] = True
        if last['started'] and position.x <= 5375 and move.is_moving_on_ground():
            last['frames'] = 3
        elif not last['started'] or position.x < goal:
            pawn.add_movement_input(u.Vector(1, 0, 0), 1.0)
    elif abs(dx) > 18:
        pawn.add_movement_input(u.Vector(1, 0, 0), 1.0 if dx > 0 else -1.0)
        last['frames'] = 0
    elif move.is_moving_on_ground():
        last['frames'] += 1
    if last['frames'] == 3 or last['elapsed'] > 8.0:
        status.write_text(json.dumps({'id': task['id'], 'at': position.to_tuple(), 'ok': last['frames'] == 3}))
        command.unlink(missing_ok=True)


handle = u.register_slate_post_tick_callback(drive)
