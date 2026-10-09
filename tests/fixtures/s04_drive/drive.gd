class_name S04Drive
extends Node3D
## Coordinates standalone input, shared car simulation, reset, camera and tuning presentation.

const SAVE_PATH: String = "user://drive_tuning.tres"
const TUNING_KEYS: Array[Key] = [
	KEY_F1, KEY_F2, KEY_F3, KEY_F4, KEY_F5, KEY_F6, KEY_F7, KEY_F8, KEY_F9,
]

@export var tuning: S04DriveTuning

var _selected_tuning: int = 0
var _start_transform: Transform3D
var _test_command: Dictionary = {}
var _test_command_enabled: bool = false
var _notice: String = "F1-F9 select • +/- adjust • F12 save + print"

@onready var _car: S04Kinematic = $Car
@onready var _input: S04DesktopInput = $Input
@onready var _camera_rig: S04CameraRig = $CameraRig
@onready var _hud: S04DriveHud = $Hud


## Enables authoritative collision before the child body enters the scene tree.
func _enter_tree() -> void:
	var car: S04Kinematic = get_node("Car")
	car.configure(true)


## Binds the saved scene parts and records the authored reset pose.
func _ready() -> void:
	assert(tuning != null)
	_start_transform = _car.global_transform
	_camera_rig.bind(_car)
	_update_hud()


## Applies collected or explicitly injected intent before each standalone simulation step.
func _physics_process(delta: float) -> void:
	var command: Dictionary = _test_command if _test_command_enabled else _input.drive_sample()
	_car.step(command, delta, tuning)
	_update_hud()


## Handles scene-only reset and tuning shortcuts after GUI has had first refusal.
func _unhandled_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.is_pressed() or event.is_echo():
		return

	var key: Key = (event as InputEventKey).physical_keycode
	if key == KEY_R:
		reset_car()
	elif key in TUNING_KEYS:
		_selected_tuning = TUNING_KEYS.find(key)
		_notice = "Selected %s" % tuning.display_name(_selected_tuning)
	elif key == KEY_EQUAL or key == KEY_KP_ADD:
		_adjust_selected(1.0)
	elif key == KEY_MINUS or key == KEY_KP_SUBTRACT:
		_adjust_selected(-1.0)
	elif key == KEY_F12:
		_save_and_print_tuning()
	else:
		return

	_update_hud()
	get_viewport().set_input_as_handled()


## Restores the authored start pose and clears all carried movement and local intent.
func reset_car() -> void:
	_car.global_transform = _start_transform
	_car.neutralize()
	_input.clear()
	_notice = "Car reset to the start"
	_camera_rig.bind(_car)


## Installs synthetic intent for the bounded standalone smoke check.
func set_test_command(command: Dictionary) -> void:
	_test_command = command.duplicate(true)
	_test_command_enabled = true


## Returns control to the desktop collector after a bounded smoke injection.
func clear_test_command() -> void:
	_test_command.clear()
	_test_command_enabled = false


## Exposes physical car state without reaching through the saved composition.
func car_state() -> Dictionary:
	return _car.motion_state()


## Changes the selected resource value without moving gameplay rules into the HUD.
func _adjust_selected(direction: float) -> void:
	tuning.adjust(_selected_tuning, direction)
	_notice = "%s = %.2f" % [
		tuning.display_name(_selected_tuning), tuning.value(_selected_tuning),
	]


## Saves a duplicate so the scene resource keeps its repository identity, then prints values.
func _save_and_print_tuning() -> void:
	var saved: S04DriveTuning = tuning.duplicate(true) as S04DriveTuning
	var error: Error = ResourceSaver.save(saved, SAVE_PATH)
	var values: String = JSON.stringify(tuning.as_dictionary())
	if error == OK:
		_notice = "Saved %s; values printed to stdout" % SAVE_PATH
		print("S04_DRIVE_TUNING ", values)
	else:
		_notice = "Save failed (%s); values printed to stdout" % error_string(error)
		push_error("S04 drive tuning save failed: %s" % error_string(error))
		print("S04_DRIVE_TUNING ", values)


## Pushes current physical state and resource values into the presentation-only HUD.
func _update_hud() -> void:
	_hud.update_display(_car.velocity.length(), tuning, _selected_tuning, _notice)
