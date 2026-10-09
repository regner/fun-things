class_name S02DesktopInput
extends Node
## Collects desktop devices; focus transitions require a fresh neutral control state.

signal suspended

const ACTIONS: Array[StringName] = [
	&"s02_forward", &"s02_back", &"s02_left", &"s02_right",
	&"s02_fire", &"s02_fire_alt",
]
const AIM_RAY_EPSILON: float = 0.0001
const AIM_DISTANCE_EPSILON_SQUARED: float = 0.0001

var active: bool = true
var menu_open: bool = false
var _held: Dictionary[StringName, Dictionary] = {}
var _aim_camera: Camera3D
var _aim_actor: S02ActorMotion
var _mouse_position: Vector2 = Vector2.ZERO


## Listens to the actual game window as well as application lifecycle notifications.
func _ready() -> void:
	get_window().focus_exited.connect(_on_window_focus_lost)
	get_window().focus_entered.connect(_on_window_focus_gained)
	active = get_window().has_focus()
	_mouse_position = get_viewport().get_visible_rect().size * 0.5


## Translates unconsumed bound events without deciding motion or shot outcomes.
func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"s02_menu") and not event.is_echo():
		menu_open = not menu_open
		clear()
		get_viewport().set_input_as_handled()
		return

	if event is InputEventMouseMotion:
		_mouse_position = (event as InputEventMouseMotion).position
		return
	if not (event is InputEventKey or event is InputEventMouseButton):
		return

	for action: StringName in ACTIONS:
		if not event.is_action(action):
			continue
		var bindings: Dictionary = _held.get(action, {})
		var identity: String = _binding_id(event)
		if not event.is_pressed():
			bindings.erase(identity)
		elif active and not menu_open and not event.is_echo():
			bindings[identity] = true
		_held[action] = bindings
		get_viewport().set_input_as_handled()


## Cancels controls on OS focus loss and prevents automatic held-input resumption.
func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		set_focused(false)
	elif what == NOTIFICATION_APPLICATION_FOCUS_IN:
		set_focused(true)


## Cancels held controls when this game's window loses desktop focus.
func _on_window_focus_lost() -> void:
	set_focused(false)


## Allows fresh input when the game window regains desktop focus.
func _on_window_focus_gained() -> void:
	set_focused(true)


## Supplies the actual viewport camera and actor plane used to collect mouse aim.
func bind_aim(camera: Camera3D, actor: S02ActorMotion) -> void:
	_aim_camera = camera
	_aim_actor = actor
	_mouse_position = get_viewport().get_visible_rect().size * 0.5


## Exposes the same focus transition for lifecycle and fixture outcome checks.
func set_focused(focused: bool) -> void:
	active = focused
	clear()


## Clears desktop intent; repeat echoes cannot resume controls after suspension.
func clear() -> void:
	_held.clear()
	suspended.emit()


## Returns world-relative movement, ground-plane aim yaw and bounded firing intent.
func sample() -> Dictionary:
	var aim_yaw: float = _sample_aim_yaw(_mouse_position)
	if not active or menu_open:
		return { "move": Vector2.ZERO, "aim_yaw": aim_yaw, "fire": false }

	return {
		"move": Vector2(
			action_strength(&"s02_right") - action_strength(&"s02_left"),
			action_strength(&"s02_back") - action_strength(&"s02_forward")
		).limit_length(1.0),
		"aim_yaw": aim_yaw,
		"fire": action_strength(&"s02_fire") > 0.0 or (
			action_strength(&"s02_fire_alt") > 0.0),
	}


## Aggregates supported physical aliases without erasing another still-held binding.
func action_strength(action: StringName) -> float:
	return 0.0 if _held.get(action, {}).is_empty() else 1.0


## Projects one viewport point onto the actor's horizontal plane without querying collision.
func aim_yaw_for_screen(screen_position: Vector2) -> float:
	return _sample_aim_yaw(screen_position)


## Resolves the current ray intersection, retaining facing for a degenerate centre aim.
func _sample_aim_yaw(screen_position: Vector2) -> float:
	if not is_instance_valid(_aim_camera) or not is_instance_valid(_aim_actor):
		return 0.0

	var origin: Vector3 = _aim_camera.project_ray_origin(screen_position)
	var direction: Vector3 = _aim_camera.project_ray_normal(screen_position)
	if absf(direction.y) <= AIM_RAY_EPSILON:
		return _aim_actor.rotation.y

	var distance: float = (_aim_actor.global_position.y - origin.y) / direction.y
	if distance < 0.0:
		return _aim_actor.rotation.y

	var ground_point: Vector3 = origin + direction * distance
	var planar: Vector3 = ground_point - _aim_actor.global_position
	planar.y = 0.0
	if planar.length_squared() <= AIM_DISTANCE_EPSILON_SQUARED:
		return _aim_actor.rotation.y
	return atan2(-planar.x, -planar.z)


## Gives each physical binding an independent held-state identity.
func _binding_id(event: InputEvent) -> String:
	if event is InputEventKey:
		return "key:%d" % (event as InputEventKey).physical_keycode
	return "mouse:%d" % (event as InputEventMouseButton).button_index
