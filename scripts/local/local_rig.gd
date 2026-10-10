class_name LocalRig
extends Node
## Owns local desktop intent and the fixed north-up camera for one controlled foot actor.

signal leave_requested

var _client_tick: int = 0
var _controlled_actor: ActorMotion
var _actor_control_enabled: bool = false

@onready var _input: DesktopFootInput = $Input as DesktopFootInput
@onready var _camera_anchor: Node3D = $CameraAnchor as Node3D
@onready var _camera: Camera3D = $CameraAnchor/Camera3D as Camera3D
@onready var _hud: Hud = get_node("UI/HUD") as Hud


## Starts disabled until the enclosing match coordinator supplies a controlled actor.
func _ready() -> void:
	set_physics_process(false)
	_input.set_focused(false)


## Releases held intent before this local process-owned rig leaves the match tree.
func _exit_tree() -> void:
	unbind_actor()


## Handles the standard menu action after UI has had the first opportunity to consume it.
func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"ui_cancel"):
		get_viewport().set_input_as_handled()
		leave_requested.emit()


## Samples and applies exactly one standalone authority command per fixed physics tick.
func _physics_process(delta: float) -> void:
	if not is_instance_valid(_controlled_actor):
		unbind_actor()
		return
	if not _actor_control_enabled:
		_controlled_actor.neutralize()
		return

	_follow_controlled_actor()
	_client_tick += 1
	var command: FootCommand = _input.sample(_client_tick)
	_controlled_actor.step(command, delta, ActorMotion.StepMode.AUTHORITY)
	_follow_controlled_actor()


## Binds one actor idempotently and enables local collection only after dependencies exist.
func bind_actor(actor: ActorMotion) -> bool:
	if actor == null or not is_instance_valid(actor) or not actor.is_inside_tree():
		return false
	if _controlled_actor == actor:
		_follow_controlled_actor()
		return true

	unbind_actor()
	_controlled_actor = actor
	_client_tick = 0
	_actor_control_enabled = true
	_input.bind_aim(_camera, actor)
	_input.set_focused(get_window().has_focus())
	_hud.bind_player(actor)
	_follow_controlled_actor()
	set_physics_process(true)
	return true


## Binds a client replica for aim/HUD while MatchReplication owns command submission.
func bind_replica_actor(actor: ActorMotion) -> bool:
	if actor == null or not is_instance_valid(actor) or not actor.is_inside_tree():
		return false
	if _controlled_actor != actor:
		unbind_actor()
		_controlled_actor = actor
		_client_tick = 0
		_input.bind_aim(_camera, actor)
		_hud.bind_player(actor)
	_actor_control_enabled = false
	set_physics_process(false)
	_input.set_focused(get_window().has_focus())
	_follow_controlled_actor()
	return true


## Enables or neutralizes standalone authority while retaining dead-state HUD presence.
func set_actor_control_enabled(enabled: bool) -> void:
	_actor_control_enabled = enabled and is_instance_valid(_controlled_actor)
	_input.set_focused(_actor_control_enabled and get_window().has_focus())
	if is_instance_valid(_controlled_actor) and not _actor_control_enabled:
		_controlled_actor.neutralize()


## Opens or closes client collection without granting simulation authority.
func set_replica_input_enabled(enabled: bool) -> void:
	_actor_control_enabled = false
	set_physics_process(false)
	_input.set_focused(
		enabled and is_instance_valid(_controlled_actor) and get_window().has_focus()
	)
	if is_instance_valid(_controlled_actor) and not enabled:
		_controlled_actor.neutralize()


## Neutralizes and forgets the current actor without owning its lifetime.
func unbind_actor() -> void:
	set_physics_process(false)
	_actor_control_enabled = false
	_input.set_focused(false)
	_hud.unbind_player()
	if is_instance_valid(_controlled_actor):
		_controlled_actor.neutralize()
	_controlled_actor = null


## Injects the process session owner into the HUD's read-only presentation seam.
func bind_session(source: Node) -> bool:
	return _hud.bind_session(source)


## Injects the authoritative replicated roster used for joined-client peer counts.
func bind_authoritative_roster(source: Node) -> bool:
	return _hud.bind_authoritative_roster(source)


## Injects the player lifecycle owner without making LocalRig a lifecycle writer.
func bind_lifecycle(source: Node) -> bool:
	return _hud.bind_lifecycle(source)


## Returns the current binding for enclosing coordinators and contract tests.
func controlled_actor() -> ActorMotion:
	return _controlled_actor


## Keeps the authored 47-metre camera offset centred on the controlled body.
func _follow_controlled_actor() -> void:
	if not is_instance_valid(_controlled_actor):
		return

	_camera_anchor.global_position = _controlled_actor.global_position
