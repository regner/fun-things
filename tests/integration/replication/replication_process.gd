extends Node  # gdstyle:ignore=quality/max-class-variables
## Drives two real SessionService processes through saved Match replication and remote walking.

const MATCH_SCENE: PackedScene = preload("res://scenes/match/match.tscn")
const SESSION_IDENTITY_TIMEOUT_MSEC: int = 25_000
const HOST_RESULT_GRACE_MSEC: int = 3_000
const CLIENT_RESULT_GRACE_MSEC: int = 750
const REMOTE_PARTICIPANT_ID: int = 2
const REQUIRED_MOVEMENT_METRES: float = 0.5
const BOUNDARY_OBSERVATION_TICKS: int = 30
const POSITION_EPSILON: float = 0.01
const MAX_REMOTE_FRAME_JUMP_METRES: float = 0.5

var _role: String = ""
var _port: int = 0
var _deadline_msec: int = 0
var _match: Node3D
var _replication: MatchReplication
var _granted: bool = false
var _sequence: int = 0
var _receipt_printed: bool = false
var _host_result_msec: int = 0
var _boundary_attack_ticks: int = 0
var _boundary_start_x: float = 0.0
var _boundary_proved: bool = false
var _rejections: Dictionary[StringName, int] = {}
var _initial_generation: int = 0
var _respawn_generation: int = 0
var _death_triggered: bool = false
var _dead_observed: bool = false
var _respawn_observed: bool = false
var _reset_requested: bool = false
var _reset_observed: bool = false
var _respawn_observed_tick: int = 0
var _old_generation_envelope: Dictionary = {}
var _old_generation_attack_ticks: int = 0
var _old_generation_proved: bool = false
var _respawn_position_x: float = NAN
var _post_reset_input_open: bool = false
var _reset_position_x: float = NAN
var _capture_dir: String = ""
var _capture_count: int = 0
var _host_sequence: int = 0
var _remote_display_start_x: float = NAN
var _remote_display_previous_position: Vector3 = Vector3.INF
var _remote_display_max_jump: float = 0.0
var _remote_continuous: bool = false

@onready var _session: SessionService = $Session
@onready var _transport: ENetTransport = $Session/ENetTransport


## Starts one host or client through the production SessionService boundary.
func _ready() -> void:
	Engine.max_fps = 60
	_parse_arguments()
	if _role not in ["host", "client"] or _port <= 0:
		_finish(false, "arguments")
		return

	_session.changed.connect(_on_session_changed)
	_transport.peer_ready.connect(_on_transport_peer_ready)
	_session.participant_admitted.connect(_on_participant_admitted)
	_session.participant_disconnected.connect(_on_participant_disconnected)
	if not _session.register_transport(_transport).get("ok", false):
		_finish(false, "transport registration")
		return

	_deadline_msec = Time.get_ticks_msec() + SESSION_IDENTITY_TIMEOUT_MSEC
	if _role == "host":
		_session.host(
			{
				"provider_id": &"enet",
				"district_id": &"brackett_island",
				"capacity": 4,
				"provider_options": { "port": _port },
			}
		)
	else:
		var parsed: Dictionary = _transport.parse_endpoint("127.0.0.1", _port)
		_session.join(parsed.target)


## Submits deterministic client intent and verifies both processes observe authority movement.
func _physics_process(_delta: float) -> void:
	if Time.get_ticks_msec() >= _deadline_msec:
		_finish(false, "deadline")
		return
	if not is_instance_valid(_replication):
		return

	_drive_lifecycle_case()
	if _role == "client" and _granted:
		if _boundary_attack_ticks <= BOUNDARY_OBSERVATION_TICKS:
			_exercise_command_boundary()
		elif _respawn_observed and not _old_generation_proved:
			_exercise_old_generation_boundary()
		else:
			_sequence += 1
			_replication.predict_and_submit_local_command(
				FootCommand.new(_sequence, _sequence, Vector2.RIGHT, 0.0, false, false),
				_delta,
			)
	if _role == "host":
		_check_host_boundary()
		_step_host_player(_delta)
	else:
		_track_remote_presentation()
	_check_replication_result()


## Emits readiness only after ENet has successfully created and published the host peer.
func _on_transport_peer_ready(operation_id: int, _peer: MultiplayerPeer) -> void:
	if _role != "host":
		return
	print(
		"M1-A2.3 host_ready "
		+ JSON.stringify(
			{
				"event": "host_ready",
				"ok": true,
				"operation_id": operation_id,
				"port": _port,
			}
		)
	)


## Loads the same saved Match on both sides only after Session admission is active.
func _on_session_changed(view: Dictionary) -> void:
	if view.phase != SessionService.PHASE_ACTIVE or is_instance_valid(_match):
		return

	_match = MATCH_SCENE.instantiate() as Node3D
	add_child(_match)
	_replication = _match.get_node("Replication") as MatchReplication
	_replication.set_local_input_enabled(false)
	_replication.input_granted.connect(_on_input_granted)
	if not _replication.configure_network(
		view.session_id,
		view.local_participant_id,
		view.operation_kind == SessionService.OPERATION_HOST,
	):
		_finish(false, "match configuration")


## Mirrors the production Boot handoff from Session-owned peer mapping to Match.
func _on_participant_admitted(native_peer_id: int, participant_id: int) -> void:
	if not is_instance_valid(_replication):
		_finish(false, "host match missing")
		return
	if not _replication.admit_peer(native_peer_id, participant_id):
		_finish(false, "participant handoff")


## Applies production disconnect cleanup if a process exits before the receipt.
func _on_participant_disconnected(native_peer_id: int, participant_id: int) -> void:
	if is_instance_valid(_replication):
		_replication.remove_peer(native_peer_id, participant_id)


## Opens deterministic intent only after baseline installation and reliable handoff.
func _on_input_granted(participant_id: int) -> void:
	_granted = participant_id == REMOTE_PARTICIPANT_ID
	if _granted:
		_sequence = 0


## Repeats bounded actual-RPC probes so configured loss cannot erase rejection proof.
func _exercise_command_boundary() -> void:
	var actor: ActorMotion = _replication.actor_for_participant(REMOTE_PARTICIPANT_ID)
	if actor == null:
		return
	var entity_ref: Dictionary = _replication.lifecycle_view().entity_ref
	var envelope: Dictionary = {
		"session_id": _session.view().session_id,
		"match_revision": _replication.match_revision(),
		"entity_id": int(entity_ref.id),
		"generation": int(entity_ref.generation),
		"packet": PackedByteArray(),
	}
	var encoded: Dictionary = FootCommandCodec.encode(
		FootCommand.new(1, 1, Vector2.RIGHT, 0.0, false, false),
		1,
	)
	if _boundary_attack_ticks == 0:
		_boundary_start_x = actor.global_position.x
		_old_generation_envelope = envelope.duplicate(true)
		_old_generation_envelope.packet = (encoded.packet as PackedByteArray).duplicate()
	if _boundary_attack_ticks % 2 == 0:
		var oversize := PackedByteArray()
		oversize.resize(MeasuredReplicationCodec.MAX_PACKET_BYTES + 1)
		envelope.packet = oversize
	else:
		var malformed_packet: PackedByteArray = (encoded.packet as PackedByteArray).duplicate()
		malformed_packet[FootCommandCodec.PACKET_BYTES - 2] = 4
		envelope.packet = malformed_packet
	_replication._submit_command.rpc_id(1, envelope)
	_boundary_attack_ticks += 1
	if absf(actor.global_position.x - _boundary_start_x) > POSITION_EPSILON:
		_finish(false, "malformed command mutated state")
		return
	if _boundary_attack_ticks > BOUNDARY_OBSERVATION_TICKS:
		_boundary_proved = true


## Proves both rejected packets left the authoritative actor unchanged.
func _check_host_boundary() -> void:
	_rejections[&"PACKET_SIZE"] = _replication.command_rejection_count(&"PACKET_SIZE")
	_rejections[&"MALFORMED_COMMAND"] = _replication.command_rejection_count(
		&"MALFORMED_COMMAND"
	)
	if _boundary_proved:
		return
	var actor: ActorMotion = _replication.actor_for_participant(REMOTE_PARTICIPANT_ID)
	if actor == null:
		return
	if is_zero_approx(_boundary_start_x):
		_boundary_start_x = actor.global_position.x
		return
	if _rejections[&"PACKET_SIZE"] == 0 or _rejections[&"MALFORMED_COMMAND"] == 0:
		return
	_boundary_proved = (
		absf(actor.global_position.x - _boundary_start_x) <= POSITION_EPSILON
	)
	if not _boundary_proved:
		_finish(false, "rejected command mutated host state")


## Replays one old EntityRef envelope while proving the new life remains stationary.
func _exercise_old_generation_boundary() -> void:
	if _old_generation_envelope.is_empty():
		_finish(false, "old generation evidence missing")
		return
	_old_generation_attack_ticks += 1
	_replication._submit_command.rpc_id(1, _old_generation_envelope)
	if _old_generation_attack_ticks >= BOUNDARY_OBSERVATION_TICKS:
		_old_generation_proved = true


## Moves the host Courier so the joined client smooths a genuinely remote actor.
func _step_host_player(delta_seconds: float) -> void:
	if not _boundary_proved or _input_authority_acknowledgement() <= 0:
		return
	var actor: ActorMotion = _replication.actor_for_participant(1)
	if actor == null:
		return
	if is_nan(_remote_display_start_x):
		_remote_display_start_x = actor.global_position.x
	_host_sequence += 1
	actor.step(
		FootCommand.new(
			_host_sequence, _host_sequence, Vector2.RIGHT, 0.0, false, false
		),
		delta_seconds,
		ActorMotion.StepMode.AUTHORITY,
	)
	_remote_continuous = (
		actor.global_position.x >= _remote_display_start_x + REQUIRED_MOVEMENT_METRES
	)


## Reads the remote participant's consumed input watermark for deterministic readiness.
func _input_authority_acknowledgement() -> int:
	return _replication._input_authority.acknowledgement(REMOTE_PARTICIPANT_ID)


## Bounds passive remote presentation jumps before lifecycle reset can teleport actors.
func _track_remote_presentation() -> void:
	if not _boundary_proved or _remote_continuous:
		return
	var actor: ActorMotion = _replication.actor_for_participant(1)
	if actor == null:
		return
	var presentation: Node3D = actor.get_node_or_null("PresentationAnchor") as Node3D
	if presentation == null:
		return
	var position: Vector3 = presentation.global_position
	if is_nan(_remote_display_start_x):
		_remote_display_start_x = position.x
	if _remote_display_previous_position != Vector3.INF:
		_remote_display_max_jump = maxf(
			_remote_display_max_jump,
			position.distance_to(_remote_display_previous_position),
		)
		if _remote_display_max_jump > MAX_REMOTE_FRAME_JUMP_METRES:
			_finish(false, "remote presentation discontinuity")
			return
	_remote_display_previous_position = position
	_remote_continuous = (
		position.x >= _remote_display_start_x + REQUIRED_MOVEMENT_METRES
	)


## Drives host death, respawn, stale-generation rejection, and retained-peer reset.
func _drive_lifecycle_case() -> void:  # gdstyle:ignore=quality/max-branches
	if not _boundary_proved or _replication.player_count() != 2:
		return
	var view: Dictionary = _replication.lifecycle_view_for(REMOTE_PARTICIPANT_ID)
	if not view.has("entity_ref"):
		return
	var generation: int = int(view.entity_ref.generation)
	if _initial_generation == 0:
		_initial_generation = generation
	if not bool(view.get("alive", true)):
		_dead_observed = true
	if (
		_dead_observed
		and not _respawn_observed
		and bool(view.get("alive", false))
		and generation > _initial_generation
	):
		_respawn_observed = true
		_respawn_generation = generation
		_respawn_observed_tick = Engine.get_physics_frames()
		if _role == "client":
			_sequence = 0
	if (
		not _reset_observed
		and _replication.match_revision() > 1
		and bool(view.get("alive", false))
	):
		_reset_observed = generation > _respawn_generation
		if _reset_observed and _role == "client":
			_sequence = 0

	var remote_actor: ActorMotion = _replication.actor_for_participant(REMOTE_PARTICIPANT_ID)
	_check_old_generation_position(remote_actor)
	if _reset_observed and remote_actor != null:
		if is_nan(_reset_position_x):
			_reset_position_x = remote_actor.global_position.x
		_maybe_capture_remote(remote_actor.global_position.x)
		if remote_actor.global_position.x >= _reset_position_x + REQUIRED_MOVEMENT_METRES:
			_post_reset_input_open = (
				_role == "host"
				or _replication._prediction_owner().acknowledgement() > 0
			)
	if _role == "host":
		_drive_host_lifecycle(remote_actor)


## Triggers authoritative death and reset only after their preceding proofs complete.
func _drive_host_lifecycle(remote_actor: ActorMotion) -> void:
	if (
		not _death_triggered
		and remote_actor != null
		and remote_actor.global_position.x >= _boundary_start_x + REQUIRED_MOVEMENT_METRES
	):
		_death_triggered = _replication.trigger_test_death(REMOTE_PARTICIPANT_ID)
	if (
		_respawn_observed
		and _old_generation_proved
		and not _reset_requested
		and Engine.get_physics_frames() >= _respawn_observed_tick + 30
	):
		_reset_requested = _replication.request_match_reset(1)


## Proves delayed old-generation input cannot move the replacement actor body.
func _check_old_generation_position(remote_actor: ActorMotion) -> void:
	if _role != "host":
		return
	if not _respawn_observed or _old_generation_proved or remote_actor == null:
		return
	if is_nan(_respawn_position_x):
		_respawn_position_x = remote_actor.global_position.x
		return
	if absf(remote_actor.global_position.x - _respawn_position_x) > POSITION_EPSILON:
		_finish(false, "old generation command moved new life")
		return
	if (
		_role == "host"
		and Engine.get_physics_frames()
		>= _respawn_observed_tick + BOUNDARY_OBSERVATION_TICKS
	):
		_old_generation_proved = true


## Requires bounded authority, death/respawn, and reset receipts on both processes.
func _check_replication_result() -> void:  # gdstyle:ignore=quality/max-function-length
	if _receipt_printed:
		_complete_receipt_grace()
		return
	if (
		not _boundary_proved
		or _replication.player_count() != 2
		or not _dead_observed
		or not _respawn_observed
		or not _old_generation_proved
		or not _reset_observed
		or not _post_reset_input_open
		or not _remote_continuous
	):
		return
	var remote_actor: ActorMotion = _replication.actor_for_participant(REMOTE_PARTICIPANT_ID)
	if remote_actor == null:
		return
	var final_lifecycle: Dictionary = _replication.lifecycle_view_for(REMOTE_PARTICIPANT_ID)
	var final_generation: int = int(final_lifecycle.entity_ref.generation)

	if not _receipt_printed:
		_receipt_printed = true
		var prediction: Dictionary = _replication._prediction_owner().diagnostics()
		var prediction_bounded: bool = (
			_role == "host"
			or int(prediction.history_size) <= FootPrediction.HISTORY_CAPACITY
		)
		print(
			"M1-A2.3 "
			+ _role
			+ " "
			+ JSON.stringify(
				{
					"match_loaded": is_instance_valid(_match),
					"ok": true,
					"boundary_proved": _boundary_proved,
					"command_rejections": _rejections,
					"players": _replication.player_count(),
					"remote_x": remote_actor.global_position.x,
					"dead_observed": _dead_observed,
					"respawn_observed": _respawn_observed,
					"old_generation_proved": _old_generation_proved,
					"reset_observed": _reset_observed,
					"input_reopened": _post_reset_input_open,
					"prediction": prediction,
					"prediction_bounded": prediction_bounded,
					"remote_continuous": _remote_continuous,
					"remote_display_max_jump": _remote_display_max_jump,
					"match_revision": _replication.match_revision(),
					"generation": final_generation,
				}
			)
		)
	_complete_receipt_grace()


## Captures at most three externally requested continuity frames at spaced thresholds.
func _maybe_capture_remote(display_x: float) -> void:
	if _capture_dir.is_empty() or _capture_count >= 3 or is_nan(_reset_position_x):
		return
	if display_x - _reset_position_x < float(_capture_count + 1) * 0.15:
		return
	_capture_count += 1
	_capture_frame.call_deferred(_capture_count)


## Saves one actual viewport image outside the checkout for optional visual review.
func _capture_frame(frame_index: int) -> void:
	DirAccess.make_dir_recursive_absolute(_capture_dir)
	var image: Image = get_viewport().get_texture().get_image()
	image.save_png(_capture_dir.path_join("remote_%02d.png" % frame_index))


## Keeps the host alive long enough for the client to publish and exit its receipt.
func _complete_receipt_grace() -> void:
	var grace_msec: int = (
		CLIENT_RESULT_GRACE_MSEC if _role == "client" else HOST_RESULT_GRACE_MSEC
	)
	if _host_result_msec == 0:
		_host_result_msec = Time.get_ticks_msec() + grace_msec
	elif Time.get_ticks_msec() >= _host_result_msec:
		get_tree().quit(0)


## Reads only the harness role and endpoint arguments after the Godot separator.
func _parse_arguments() -> void:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--role="):
			_role = argument.trim_prefix("--role=")
		elif argument.begins_with("--port="):
			_port = argument.trim_prefix("--port=").to_int()
		elif argument.begins_with("--capture-dir="):
			_capture_dir = argument.trim_prefix("--capture-dir=")


## Emits one machine-readable process result before bounded failure exit.
func _finish(ok: bool, detail: String) -> void:
	print(
		"M1-A2.3 "
		+ _role
		+ " "
		+ JSON.stringify(
			{
				"boundary_proved": _boundary_proved,
				"command_rejections": _rejections,
				"detail": detail,
				"ok": ok,
			}
		)
	)
	get_tree().quit(0 if ok else 1)
