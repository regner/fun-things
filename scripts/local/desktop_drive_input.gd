class_name DesktopDriveInput
extends Node
## Collects development desktop controls without owning vehicle outcomes.

var _focused: bool = true


## Clears held local intent when the application loses focus.
func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		_focused = false
	elif what == NOTIFICATION_APPLICATION_FOCUS_IN:
		_focused = true


## Samples one complete typed command for the current fixed tick.
func sample(sequence: int) -> DriveCommand:
	if not _focused:
		return DriveCommand.neutral(sequence, sequence)

	var throttle := Input.get_axis(&"s02_back", &"s02_forward")
	var steer := Input.get_axis(&"s02_left", &"s02_right")
	var brake := 1.0 if Input.is_action_pressed(&"drive_brake") else 0.0
	var handbrake := Input.is_action_pressed(&"drive_handbrake")
	return DriveCommand.new(sequence, sequence, throttle, steer, brake, handbrake)


## Allows bounded harnesses to establish focus without synthesizing device events.
func set_focused(focused: bool) -> void:
	_focused = focused
