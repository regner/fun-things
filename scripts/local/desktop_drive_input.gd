class_name DesktopDriveInput
extends Node
## Collects development desktop controls without owning vehicle outcomes.

const ACTIONS: Array[StringName] = [
	&"drive_throttle",
	&"drive_reverse",
	&"drive_steer_left",
	&"drive_steer_right",
	&"drive_brake",
	&"drive_handbrake",
]

var _focused: bool = true
var _sequence: int = 0
var _held: Dictionary[StringName, Dictionary] = {}


## Tracks physical drive bindings through the same viewport seam as foot controls.
func _unhandled_input(event: InputEvent) -> void:
	if not _focused or not (event is InputEventKey or event is InputEventMouseButton):
		return
	for action: StringName in ACTIONS:
		if not event.is_action(action):
			continue
		var bindings: Dictionary = _held.get(action, {})
		var identity: String = _binding_id(event)
		if not event.is_pressed():
			bindings.erase(identity)
		elif not event.is_echo():
			bindings[identity] = true
		_held[action] = bindings
		get_viewport().set_input_as_handled()


## Clears held local intent when the application loses focus.
func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		set_focused(false)
	elif what == NOTIFICATION_APPLICATION_FOCUS_IN:
		set_focused(true)


## Samples one complete typed command for the current fixed tick.
func sample(client_tick: int) -> DriveCommand:
	_sequence += 1
	if not _focused:
		return DriveCommand.neutral(_sequence, client_tick)

	var throttle: float = _action_strength(&"drive_throttle") - _action_strength(
		&"drive_reverse"
	)
	var steer: float = _action_strength(&"drive_steer_right") - _action_strength(
		&"drive_steer_left"
	)
	var brake: float = _action_strength(&"drive_brake")
	var handbrake: bool = _action_strength(&"drive_handbrake") > 0.0
	return DriveCommand.new(_sequence, client_tick, throttle, steer, brake, handbrake)


## Restarts numbered intent only after a confirmed control-revision transition.
func reset_sequence() -> void:
	_sequence = 0
	_held.clear()


## Allows enclosing ownership to gate collection at confirmed seat transitions.
func set_focused(focused: bool) -> void:
	if _focused == focused:
		return
	_focused = focused
	_held.clear()


## Aggregates every physical alias bound to one drive action.
func _action_strength(action: StringName) -> float:
	return 0.0 if _held.get(action, {}).is_empty() else 1.0


## Distinguishes physical bindings so releasing one alias cannot release another.
func _binding_id(event: InputEvent) -> String:
	if event is InputEventKey:
		var key := event as InputEventKey
		return "key:%d:%d" % [key.physical_keycode, key.location]
	var button := event as InputEventMouseButton
	return "mouse:%d" % button.button_index
