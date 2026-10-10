class_name DesktopFootInput
extends Node
## Collects desktop foot intent while requiring fresh input after every focus loss.

signal suspended

const ACTIONS: Array[StringName] = [
	&"foot_move_forward",
	&"foot_move_back",
	&"foot_move_left",
	&"foot_move_right",
	&"foot_fire",
	&"foot_alt",
]
const AIM_RAY_EPSILON: float = 0.0001
const AIM_DISTANCE_EPSILON_SQUARED: float = 0.0001

var active: bool = true
var _sequence: int = 0
var _held: Dictionary[StringName, Dictionary] = {}
var _aim_camera: Camera3D
var _aim_actor: ActorMotion
var _mouse_position: Vector2 = Vector2.ZERO


## Connects both window and application focus sources before collecting intent.
func _ready() -> void:
	get_window().focus_exited.connect(_on_window_focus_lost)
	get_window().focus_entered.connect(_on_window_focus_gained)
	active = get_window().has_focus()
	_mouse_position = get_viewport().get_visible_rect().size * 0.5


## Tracks only unconsumed gameplay bindings so UI can handle its input first.
func _unhandled_input(event: InputEvent) -> void:
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
		elif active and not event.is_echo():
			bindings[identity] = true
		_held[action] = bindings
		get_viewport().set_input_as_handled()


## Neutralizes held intent on operating-system application focus transitions.
func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		set_focused(false)
	elif what == NOTIFICATION_APPLICATION_FOCUS_IN:
		set_focused(true)


## Supplies the authored camera and controlled actor used only to derive aim yaw.
func bind_aim(camera: Camera3D, actor: ActorMotion) -> void:
	if _aim_camera == camera and _aim_actor == actor:
		return

	_aim_camera = camera
	_aim_actor = actor
	_mouse_position = get_viewport().get_visible_rect().size * 0.5


## Samples one numbered command without applying motion or gameplay outcomes.
func sample(client_tick: int) -> FootCommand:
	_sequence += 1
	var aim_yaw: float = _sample_aim_yaw(_mouse_position)
	if not active:
		return FootCommand.new(_sequence, client_tick, Vector2.ZERO, aim_yaw, false, false)

	var move := Vector2(
		action_strength(&"foot_move_right") - action_strength(&"foot_move_left"),
		action_strength(&"foot_move_back") - action_strength(&"foot_move_forward")
	).limit_length(1.0)
	return FootCommand.new(
		_sequence,
		client_tick,
		move,
		aim_yaw,
		action_strength(&"foot_fire") > 0.0,
		action_strength(&"foot_alt") > 0.0
	)


## Exposes focus control for enclosing lifecycle owners and deterministic tests.
func set_focused(focused: bool) -> void:
	if active == focused:
		return

	active = focused
	clear()


## Restarts held sequence numbering only after a host-authorized input rebind.
func reset_sequence() -> void:
	_sequence = 0
	clear()


## Clears every physical alias so focus regain cannot resume a stale held control.
func clear() -> void:
	_held.clear()
	suspended.emit()


## Aggregates physical aliases without releasing another still-held binding.
func action_strength(action: StringName) -> float:
	return 0.0 if _held.get(action, {}).is_empty() else 1.0


## Projects one screen point onto the actor plane for independent aim checks.
func aim_yaw_for_screen(screen_position: Vector2) -> float:
	return _sample_aim_yaw(screen_position)


## Cancels controls when this game window loses desktop focus.
func _on_window_focus_lost() -> void:
	set_focused(false)


## Allows only subsequent fresh events when this game window regains focus.
func _on_window_focus_gained() -> void:
	set_focused(true)


## Resolves mouse aim while retaining facing for unavailable or degenerate rays.
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


## Gives each keyboard or mouse alias an independent held-state identity.
func _binding_id(event: InputEvent) -> String:
	if event is InputEventKey:
		return "key:%d" % (event as InputEventKey).physical_keycode
	return "mouse:%d" % (event as InputEventMouseButton).button_index
