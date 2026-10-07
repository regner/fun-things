class_name S02DesktopInput
extends Node
## Collects unhandled local input; focus transitions require a fresh neutral state.

signal suspended

const ACTIONS: Array[StringName] = [
	&"s02_forward", &"s02_back", &"s02_left", &"s02_right", &"s02_fire",
]

var active: bool = true
var menu_open: bool = false
var _held: Dictionary[StringName, Dictionary] = {}


## Listens to the actual game window as well as application lifecycle notifications.
func _ready() -> void:
	get_window().focus_exited.connect(_on_window_focus_lost)
	get_window().focus_entered.connect(_on_window_focus_gained)
	active = get_window().has_focus()


## Translates unconsumed bound events without deciding motion or shot outcomes.
func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"s02_menu") and not event.is_echo():
		menu_open = not menu_open
		clear()
		get_viewport().set_input_as_handled()
		return

	if not event is InputEventKey:
		return

	var key: Key = (event as InputEventKey).physical_keycode
	for action: StringName in ACTIONS:
		if not event.is_action(action):
			continue
		var bindings: Dictionary = _held.get(action, {})
		if not event.is_pressed():
			bindings.erase(key)
		elif active and not menu_open and not event.is_echo():
			bindings[key] = true
		_held[action] = bindings
		get_viewport().set_input_as_handled()


## Cancels controls on OS focus loss and prevents automatic held-key resumption.
func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		set_focused(false)
	elif what == NOTIFICATION_APPLICATION_FOCUS_IN:
		set_focused(true)


## Cancels held controls when this game's window loses desktop focus.
func _on_window_focus_lost() -> void:
	set_focused(false)


## Allows fresh key presses when the game window regains desktop focus.
func _on_window_focus_gained() -> void:
	set_focused(true)


## Exposes the same focus transition for lifecycle and fixture outcome checks.
func set_focused(focused: bool) -> void:
	active = focused
	clear()


## Clears keyboard intent; repeat echoes cannot resume controls after suspension.
func clear() -> void:
	_held.clear()
	suspended.emit()


## Returns facing-relative intent with no device access in the simulation owner.
func sample() -> Dictionary:
	if not active or menu_open:
		return { "move": 0.0, "turn": 0.0, "fire": false }

	return {
		"move": _strength(&"s02_forward") - _strength(&"s02_back"),
		"turn": _strength(&"s02_right") - _strength(&"s02_left"),
		"fire": _strength(&"s02_fire") > 0.0,
	}


## Aggregates supported physical aliases without erasing another still-held binding.
func _strength(action: StringName) -> float:
	return 0.0 if _held.get(action, {}).is_empty() else 1.0
