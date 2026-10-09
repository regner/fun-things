extends Node3D
## Runs all delivered cars through production VehicleMotion in flat and Brackett environments.

const SAVE_PATH: String = "user://vehicle_tuning.tres"
const SMOKE_ARGUMENT: String = "--vehicle-harness-smoke"
const SMOKE_TICKS: int = 20
const FLAT_START := Transform3D(Basis.IDENTITY, Vector3(450.0, 0.05, 0.0))
const BRACKETT_START := Transform3D(
	Basis(Vector3.UP, -PI * 0.5), Vector3(-104.0, 0.05, -10.0)
)
const TUNING_KEYS: Array[Key] = [
	KEY_F1,
	KEY_F2,
	KEY_F3,
	KEY_F4,
	KEY_F5,
	KEY_F6,
	KEY_F7,
	KEY_F8,
	KEY_F9,
	KEY_F10,
]

@export var tuning: VehicleTuning

var _cars: Array[VehicleMotion] = []
var _active_car_index: int = 0
var _selected_tuning: int = 0
var _client_tick: int = 0
var _using_brackett: bool = false
var _smoke: bool = false
var _start_position: Vector3
var _default_tuning: VehicleTuning
var _notice: String = "F1-F10 select • +/- adjust • F12 save • Backspace defaults"

@onready var _input: DesktopDriveInput = $DesktopDriveInput as DesktopDriveInput
@onready var _camera_rig: Node3D = $CameraRig
@onready var _label: Label = $Hud/Panel/Margin/Label as Label


## Makes only the initially selected authored car collide before child tree entry.
func _enter_tree() -> void:
	var vehicles: Node = get_node("Vehicles")
	for index: int in vehicles.get_child_count():
		var car: VehicleMotion = vehicles.get_child(index) as VehicleMotion
		car.configure_simulation(index == _active_car_index)
		car.visible = index == _active_car_index


## Binds authored cars, loads tuning, and enforces capped standalone operation.
func _ready() -> void:
	Engine.max_fps = 60
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)
	for child: Node in $Vehicles.get_children():
		_cars.append(child as VehicleMotion)
	_default_tuning = tuning.duplicate(true) as VehicleTuning
	_load_saved_tuning()
	_apply_tuning()
	_reset_active_car()
	_smoke = SMOKE_ARGUMENT in OS.get_cmdline_user_args()
	if _smoke:
		_input.set_focused(true)
	_start_position = _active_car().global_position
	_update_hud()


## Samples standalone intent and applies the same fixed VehicleMotion step used by other callers.
func _physics_process(delta: float) -> void:
	_client_tick += 1
	var command: DriveCommand = _input.sample(_client_tick)
	if _smoke:
		command = DriveCommand.new(_client_tick, _client_tick, 1.0, 0.0, 0.0, false)
	_active_car().step(command, delta, VehicleMotion.StepMode.AUTHORITY)
	_camera_rig.global_position.x = _active_car().global_position.x
	_camera_rig.global_position.z = _active_car().global_position.z
	_update_hud()

	if _smoke and _client_tick >= SMOKE_TICKS:
		_finish_smoke()


## Handles car, environment, reset, and tuning shortcuts after GUI first refusal.
func _unhandled_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.is_pressed() or event.is_echo():
		return

	var key: Key = (event as InputEventKey).physical_keycode
	if key == KEY_1 or key == KEY_2 or key == KEY_3:
		_select_car(int(key) - int(KEY_1))
	elif key == KEY_R:
		_reset_active_car()
	elif key == KEY_F11:
		_using_brackett = not _using_brackett
		_reset_active_car()
	elif not _handle_tuning_key(key):
		return

	_update_hud()
	get_viewport().set_input_as_handled()


## Handles the standalone tuning shortcuts and reports whether the key was consumed.
func _handle_tuning_key(key: Key) -> bool:
	if key in TUNING_KEYS:
		_selected_tuning = TUNING_KEYS.find(key)
		_notice = "Selected %s" % tuning.display_name(_selected_tuning)
	elif key == KEY_EQUAL or key == KEY_KP_ADD:
		_adjust_selected(1.0)
	elif key == KEY_MINUS or key == KEY_KP_SUBTRACT:
		_adjust_selected(-1.0)
	elif key == KEY_F12:
		_save_tuning()
	elif key == KEY_BACKSPACE:
		_restore_defaults()
	else:
		return false
	return true


## Returns the currently controlled vehicle entity.
func _active_car() -> VehicleMotion:
	return _cars[_active_car_index]


## Transfers local development control without adding gameplay seat ownership.
func _select_car(index: int) -> void:
	if index < 0 or index >= _cars.size() or index == _active_car_index:
		return
	var previous_transform: Transform3D = _active_car().global_transform
	_active_car().configure_simulation(false)
	_active_car().visible = false
	_active_car_index = index
	_active_car().global_transform = previous_transform
	_active_car().visible = true
	_active_car().configure_simulation(true)
	_notice = "Driving %s" % _active_car().name


## Restores the selected flat-floor or Brackett start and clears carried motion.
func _reset_active_car() -> void:
	_active_car().global_transform = BRACKETT_START if _using_brackett else FLAT_START
	_active_car().neutralize()
	_notice = "Brackett match world" if _using_brackett else "Flat-floor test area"


## Applies one mutable harness copy without changing the checked-in resource.
func _apply_tuning() -> void:
	for car: VehicleMotion in _cars:
		car.tuning = tuning


## Loads only a valid production tuning resource from the per-user path.
func _load_saved_tuning() -> void:
	if not FileAccess.file_exists(SAVE_PATH):
		tuning = _default_tuning.duplicate(true) as VehicleTuning
		return
	var saved: Resource = ResourceLoader.load(SAVE_PATH, "", ResourceLoader.CACHE_MODE_IGNORE)
	if saved is VehicleTuning and (saved as VehicleTuning).is_valid():
		tuning = saved.duplicate(true) as VehicleTuning
		_notice = "Saved values active • Backspace restores decision-30 defaults"
	else:
		tuning = _default_tuning.duplicate(true) as VehicleTuning
		_notice = "Saved values invalid • decision-30 defaults active"


## Changes the selected tuning row and immediately shares it with every car.
func _adjust_selected(direction: float) -> void:
	tuning.adjust(_selected_tuning, direction)
	_apply_tuning()
	_notice = "%s = %.2f" % [
		tuning.display_name(_selected_tuning), tuning.value(_selected_tuning),
	]


## Persists a duplicate so the checked-in tuning resource retains its identity.
func _save_tuning() -> void:
	var error: Error = ResourceSaver.save(tuning.duplicate(true), SAVE_PATH)
	if error == OK:
		_notice = "Saved %s" % SAVE_PATH
		print("VEHICLE_DRIVE_TUNING ", JSON.stringify(tuning.as_dictionary()))
	else:
		_notice = "Save failed: %s" % error_string(error)
		push_error("Vehicle tuning save failed: %s" % error_string(error))


## Restores decision-30 defaults and removes the per-user override.
func _restore_defaults() -> void:
	tuning = _default_tuning.duplicate(true) as VehicleTuning
	_apply_tuning()
	if FileAccess.file_exists(SAVE_PATH):
		var error: Error = DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE_PATH))
		if error != OK:
			_notice = "Defaults active; override removal failed: %s" % error_string(error)
			return
	_notice = "Decision-30 defaults active; saved override removed"


## Presents current motion and tuning values without deciding simulation outcomes.
func _update_hud() -> void:
	var lines: Array[String] = [
		"Vehicle drive/tuning • 1/2/3 car • F11 flat/Brackett • R reset",
		"W/S throttle • A/D steer • Shift brake • Space handbrake",
		"%s • speed %.2f m/s" % [_active_car().name, _active_car().velocity.length()],
		_notice,
	]
	for index: int in tuning.value_count():
		var marker: String = ">" if index == _selected_tuning else " "
		lines.append("%s F%d %s: %.2f" % [
			marker, index + 1, tuning.display_name(index), tuning.value(index),
		])
	_label.text = "\n".join(lines)


## Exits the bounded headless smoke nonzero if the production car did not move.
func _finish_smoke() -> void:
	var travelled: float = _active_car().global_position.distance_to(_start_position)
	if travelled <= 0.2:
		push_error("VEHICLE_HARNESS_SMOKE failed: VehicleMotion did not move")
		get_tree().quit(1)
		return
	print("VEHICLE_HARNESS_SMOKE PASS distance=%.3f" % travelled)
	get_tree().quit(0)
