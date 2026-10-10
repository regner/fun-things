class_name LocalRig
extends Node
## Owns local desktop intent, retained player HUD context, and accepted-body camera follow.

signal leave_requested
signal interaction_requested

var _client_tick: int = 0
var _vehicle_tick: int = 0
var _controlled_actor: ActorMotion
var _controlled_vehicle: VehicleMotion
var _actor_control_enabled: bool = false
var _interaction_input_enabled: bool = true

@onready var _input: DesktopFootInput = $Input as DesktopFootInput
@onready var _drive_input: DesktopDriveInput = $DriveInput as DesktopDriveInput
@onready var _camera_anchor: Node3D = $CameraAnchor as Node3D
@onready var _camera: Camera3D = $CameraAnchor/Camera3D as Camera3D
@onready var _hud: Hud = get_node("UI/HUD") as Hud


## Starts disabled until the enclosing match coordinator supplies a controlled actor.
func _ready() -> void:
	set_physics_process(false)
	_input.set_focused(false)
	_drive_input.set_focused(false)


## Releases held intent before this local process-owned rig leaves the match tree.
func _exit_tree() -> void:
	unbind_actor()


## Emits one raw interaction press after UI has had first opportunity to consume E.
func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"ui_cancel"):
		get_viewport().set_input_as_handled()
		leave_requested.emit()
		return
	if (
		_interaction_input_enabled
		and not event.is_echo()
		and event.is_action_pressed(&"interact")
		and (
			is_instance_valid(_controlled_actor)
			or is_instance_valid(_controlled_vehicle)
		)
	):
		get_viewport().set_input_as_handled()
		interaction_requested.emit()


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
	if _controlled_actor == actor and _controlled_vehicle == null:
		_follow_controlled_actor()
		return true

	unbind_actor()
	_controlled_actor = actor
	_client_tick = 0
	_actor_control_enabled = true
	_input.bind_aim(_camera, actor)
	_input.set_focused(get_window().has_focus())
	_drive_input.set_focused(false)
	_hud.bind_player(actor)
	_follow_controlled_actor()
	set_physics_process(true)
	return true


## Binds a client replica for aim/HUD while MatchReplication owns command submission.
func bind_replica_actor(actor: ActorMotion) -> bool:
	if actor == null or not is_instance_valid(actor) or not actor.is_inside_tree():
		return false
	if _controlled_actor != actor or _controlled_vehicle != null:
		unbind_actor()
		_controlled_actor = actor
		_client_tick = 0
		_input.bind_aim(_camera, actor)
		_hud.bind_player(actor)
	_actor_control_enabled = false
	set_physics_process(false)
	_input.set_focused(get_window().has_focus())
	_drive_input.set_focused(false)
	_follow_controlled_actor()
	return true


## Transfers camera/input ownership to a confirmed vehicle while retaining player HUD data.
func bind_vehicle(vehicle: VehicleMotion) -> bool:
	if vehicle == null or not is_instance_valid(vehicle) or not vehicle.is_inside_tree():
		return false
	if _controlled_vehicle == vehicle:
		follow_vehicle_display(vehicle)
		return true

	set_physics_process(false)
	_actor_control_enabled = false
	_input.set_focused(false)
	if is_instance_valid(_controlled_actor):
		_controlled_actor.neutralize()
	_controlled_vehicle = vehicle
	reset_vehicle_command_sequence()
	_drive_input.set_focused(get_window().has_focus())
	follow_vehicle_display(vehicle)
	return true


## Gates the saved drive collector without changing confirmed vehicle ownership.
func set_vehicle_input_enabled(enabled: bool) -> void:
	_drive_input.set_focused(
		enabled and is_instance_valid(_controlled_vehicle) and get_window().has_focus()
	)


## Enables or disables the physical interaction seam without owning action sequencing.
func set_interaction_input_enabled(enabled: bool) -> void:
	_interaction_input_enabled = enabled


## Enables or neutralizes standalone authority while retaining dead-state HUD presence.
func set_actor_control_enabled(enabled: bool) -> void:
	_actor_control_enabled = enabled and is_instance_valid(_controlled_actor)
	_input.set_focused(_actor_control_enabled and get_window().has_focus())
	_drive_input.set_focused(false)
	if is_instance_valid(_controlled_actor) and not _actor_control_enabled:
		_controlled_actor.neutralize()


## Opens or closes client collection without granting simulation authority.
func set_replica_input_enabled(enabled: bool) -> void:
	_actor_control_enabled = false
	set_physics_process(false)
	var focused: bool = enabled and get_window().has_focus()
	_input.set_focused(
		focused and is_instance_valid(_controlled_actor) and _controlled_vehicle == null
	)
	_drive_input.set_focused(focused and is_instance_valid(_controlled_vehicle))
	if is_instance_valid(_controlled_actor) and not enabled:
		_controlled_actor.neutralize()


## Neutralizes and forgets the current actor without owning its lifetime.
func unbind_actor() -> void:
	set_physics_process(false)
	_actor_control_enabled = false
	_input.set_focused(false)
	_drive_input.set_focused(false)
	_hud.unbind_player()
	if is_instance_valid(_controlled_actor):
		_controlled_actor.neutralize()
	_controlled_actor = null
	_controlled_vehicle = null
	reset_vehicle_command_sequence()


## Samples vehicle intent only while an authoritative descriptor confirms local control.
func sample_vehicle_command() -> DriveCommand:
	if not is_instance_valid(_controlled_vehicle):
		return null
	_vehicle_tick += 1
	return _drive_input.sample(_vehicle_tick)


## Restarts command numbering after a reliable vehicle control-revision transition.
func reset_vehicle_command_sequence() -> void:
	_vehicle_tick = 0
	_drive_input.reset_sequence()


## Injects the process session owner into the HUD's read-only presentation seam.
func bind_session(source: Node) -> bool:
	return _hud.bind_session(source)


## Injects the authoritative replicated roster used for joined-client peer counts.
func bind_authoritative_roster(source: Node) -> bool:
	return _hud.bind_authoritative_roster(source)


## Injects the player lifecycle owner without making LocalRig a lifecycle writer.
func bind_lifecycle(source: Node) -> bool:
	return _hud.bind_lifecycle(source)


## Centres the camera on a predicted presentation without enabling standalone simulation.
func follow_actor_display(actor: ActorMotion) -> void:
	if actor == null:
		return
	var presentation: Node3D = actor.get_node_or_null("PresentationAnchor") as Node3D
	_camera_anchor.global_position = (
		presentation.global_position if presentation != null else actor.global_position
	)


## Centres the camera on a vehicle presentation without granting seat authority.
func follow_vehicle_display(vehicle: VehicleMotion) -> void:
	if vehicle == null:
		return
	var presentation: Node3D = vehicle.get_node_or_null("PresentationAnchor") as Node3D
	_camera_anchor.global_position = (
		presentation.global_position if presentation != null else vehicle.global_position
	)


## Returns the current foot binding retained for HUD and exit restoration.
func controlled_actor() -> ActorMotion:
	return _controlled_actor


## Returns the acceptance-only vehicle camera/control binding.
func controlled_vehicle() -> VehicleMotion:
	return _controlled_vehicle


## Keeps the authored 47-metre camera offset centred on the controlled body.
func _follow_controlled_actor() -> void:
	if not is_instance_valid(_controlled_actor):
		return

	_camera_anchor.global_position = _controlled_actor.global_position
