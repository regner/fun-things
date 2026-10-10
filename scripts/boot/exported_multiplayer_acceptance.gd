class_name ExportedMultiplayerAcceptance  # gdstyle:ignore=quality/max-class-variables
extends RefCounted
## Drives opt-in exported-build acceptance through production Session and Match APIs.

const PREFIX: String = "M1-A-GATE "
const ROLE_HOST: String = "host"
const ROLE_CLIENT: String = "client"
const SCENARIO_GAMEPLAY: String = "gameplay"
const SCENARIO_INCOMPATIBLE: String = "incompatible"
const SCENARIO_ADMISSION_TIMEOUT: String = "admission_timeout"
const SCENARIO_HOST_LOSS: String = "host_loss"
const SCENARIO_PLAYTEST: String = "playtest"
const SCENARIO_SUSTAINED: String = "sustained"
const PROCESS_TIMEOUT_MSEC: int = 120_000
const HANDSHAKE_TIMEOUT_SECONDS: float = 0.75
const REQUIRED_MOVEMENT_METRES: float = 0.5
const PREDICTED_DISPLACEMENT_EPSILON_METRES: float = 0.01
const STATIONARY_ROOT_EPSILON_METRES: float = 0.0001
const PRESENTATION_MOVEMENT_EPSILON_METRES: float = 0.001
const MAX_REMOTE_FRAME_JUMP_METRES: float = 0.5
const REMOTE_PARTICIPANT_ID: int = 2
const HOST_PARTICIPANT_ID: int = 1
const SUSTAINED_MOVEMENT_TICKS: int = 600
const SUSTAINED_SETTLE_TICKS: int = 45
const SUSTAINED_CLOSE_GRACE_TICKS: int = 120
const CONTINUITY_WINDOW_TICKS: int = 15
const MINIMUM_WINDOW_DISTANCE_METRES: float = 0.2
const MINIMUM_CLIENT_HOST_DISTANCE_RATIO: float = 0.3
const HOST_FINAL_AIM_YAW: float = 1.0
const CLIENT_FINAL_AIM_YAW: float = -1.0
const FACING_TOLERANCE_RADIANS: float = 0.15

var _tree: SceneTree
var _session: SessionService
var _transport: ENetTransport
var _match_provider: Callable
var _role: String = ""
var _scenario: String = ""
var _port: int = 0
var _deadline_msec: int = 0
var _replication: MatchReplication
var _raw_peer: ENetMultiplayerPeer
var _input_granted: bool = false
var _sequence: int = 0
var _host_sequence: int = 0
var _initial_positions: Dictionary[int, float] = {}
var _initial_generation: int = 0
var _respawn_generation: int = 0
var _dead_observed: bool = false
var _respawn_observed: bool = false
var _reset_requested: bool = false
var _reset_observed: bool = false
var _post_reset_start_x: float = NAN
var _host_moved: bool = false
var _client_moved: bool = false
var _remote_smoothed: bool = false
var _success_ready: bool = false
var _closing: bool = false
var _finished: bool = false
var _host_ready: bool = false
var _peer_seen: bool = false
var _auth_waiting: bool = false
var _auth_wait_started_msec: int = 0
var _auth_failure_elapsed_msec: int = 0
var _local_authority_receipts: int = 0
var _prediction_receipts_before_submit: int = 0
var _prediction_waiting_for_authority: bool = false
var _prediction_succeeded: bool = false
var _prediction_before_authority_receipt: bool = false
var _prediction_peak_history: int = 0
var _prediction_unacknowledged_displacement_metres: float = 0.0
var _remote_previous_root_position: Vector3 = Vector3.INF
var _remote_previous_display_position: Vector3 = Vector3.INF
var _remote_display_start_position: Vector3 = Vector3.INF
var _remote_display_max_jump_metres: float = 0.0
var _remote_stationary_root_frames: int = 0
var _remote_stationary_display_displacement_metres: float = 0.0
var _sustained_tick: int = 0
var _sustained_previous_positions: Dictionary[int, Vector3] = {}
var _sustained_distances: Dictionary[int, float] = {}
var _sustained_window_previous: Vector3 = Vector3.INF
var _sustained_window_distance: float = 0.0
var _sustained_window_failures: int = 0
var _sustained_minimum_window_metres: float = INF
var _sustained_local_yaw_min: float = INF
var _sustained_local_yaw_max: float = -INF


## Parses the explicit acceptance arguments without changing ordinary launches.
static func options_from_arguments(arguments: PackedStringArray) -> Dictionary:
	var options: Dictionary = {}
	for argument: String in arguments:
		if argument.begins_with("--m1-a-gate-role="):
			options.role = argument.trim_prefix("--m1-a-gate-role=")
		elif argument.begins_with("--m1-a-gate-scenario="):
			options.scenario = argument.trim_prefix("--m1-a-gate-scenario=")
		elif argument.begins_with("--m1-a-gate-port="):
			options.port = argument.trim_prefix("--m1-a-gate-port=").to_int()
	return options


## Reports whether one launch requested the opt-in exported acceptance path.
static func requested(options: Dictionary) -> bool:
	return options.get("role", "") in [ROLE_HOST, ROLE_CLIENT]


## Injects process owners and starts one bounded production session operation.
func configure(
	tree: SceneTree,
	session: SessionService,
	transport: ENetTransport,
	match_provider: Callable,
	options: Dictionary,
) -> bool:
	_tree = tree
	_session = session
	_transport = transport
	_match_provider = match_provider
	_role = options.get("role", "")
	_scenario = options.get("scenario", "")
	_port = int(options.get("port", 0))
	if (
		_role not in [ROLE_HOST, ROLE_CLIENT]
		or _scenario not in [
			SCENARIO_GAMEPLAY,
			SCENARIO_INCOMPATIBLE,
			SCENARIO_ADMISSION_TIMEOUT,
			SCENARIO_HOST_LOSS,
			SCENARIO_PLAYTEST,
			SCENARIO_SUSTAINED,
		]
		or _port <= 0
	):
		return false

	_deadline_msec = Time.get_ticks_msec() + PROCESS_TIMEOUT_MSEC
	_session.changed.connect(_on_session_changed)
	_session.completed.connect(_on_session_completed)
	_session.participant_admitted.connect(_on_participant_admitted)
	_session.participant_disconnected.connect(_on_participant_disconnected)
	_transport.peer_ready.connect(_on_peer_ready)
	_transport.disconnected.connect(_on_transport_disconnected)
	if _scenario == SCENARIO_ADMISSION_TIMEOUT:
		_session.handshake_timeout_seconds = HANDSHAKE_TIMEOUT_SECONDS

	if _role == ROLE_CLIENT and _scenario == SCENARIO_ADMISSION_TIMEOUT:
		_start_silent_auth_client()
	else:
		_start_session_operation()
	return true


## Advances only acceptance orchestration; gameplay remains owned by production components.
func physics_process(delta_seconds: float) -> void:
	if _finished:
		return
	if Time.get_ticks_msec() >= _deadline_msec and _scenario != SCENARIO_PLAYTEST:
		_finish(false, "PROCESS_TIMEOUT")
		return
	if _scenario not in [SCENARIO_GAMEPLAY, SCENARIO_PLAYTEST, SCENARIO_SUSTAINED]:
		return

	_bind_match()
	if _scenario == SCENARIO_PLAYTEST:
		return
	if not is_instance_valid(_replication) or _replication.player_count() != 2:
		return
	if _scenario == SCENARIO_SUSTAINED:
		_step_sustained(delta_seconds)
		return
	_step_gameplay(delta_seconds)
	_observe_lifecycle()


## Starts the normal host or join flow after any compatibility override is installed.
func _start_session_operation() -> void:
	if _scenario == SCENARIO_INCOMPATIBLE and _role == ROLE_CLIENT:
		var compatibility: Dictionary = {
			"protocol_version": 1,
			"content_id": "development",
			"district_id": &"brackett_island",
			"topology_revision": 0,
			"definition_set_id": "development",
		}
		if not _session.configure_compatibility(compatibility).get("ok", false):
			_finish(false, "COMPATIBILITY_SETUP")
			return

	if _role == ROLE_HOST:
		var hosted: Dictionary = _session.host(
			{
				"provider_id": &"enet",
				"district_id": &"brackett_island",
				"capacity": 4,
				"provider_options": { "port": _port, "bind_address": "127.0.0.1" },
			}
		)
		if not hosted.get("ok", false):
			_finish(false, "HOST_REJECTED")
	else:
		var parsed: Dictionary = _transport.parse_endpoint("127.0.0.1", _port)
		if not parsed.get("ok", false) or not _session.join(parsed.target).get("ok", false):
			_finish(false, "JOIN_REJECTED")


## Opens a real ENet client that deliberately withholds its authentication response.
func _start_silent_auth_client() -> void:
	var scene_multiplayer := _tree.get_multiplayer() as SceneMultiplayer
	scene_multiplayer.auth_timeout = HANDSHAKE_TIMEOUT_SECONDS
	scene_multiplayer.auth_callback = _ignore_auth_payload
	scene_multiplayer.peer_authenticating.connect(_on_raw_peer_authenticating)
	scene_multiplayer.peer_authentication_failed.connect(_on_raw_authentication_failed)
	scene_multiplayer.server_disconnected.connect(_on_raw_server_disconnected)
	_raw_peer = ENetMultiplayerPeer.new()
	var error: Error = _raw_peer.create_client("127.0.0.1", _port, 0, 0, 4)
	if error != OK:
		_finish(false, "RAW_CLIENT_CREATE")
		return
	scene_multiplayer.multiplayer_peer = _raw_peer


## Ignores the host handshake so SceneMultiplayer's admission deadline must close the peer.
func _ignore_auth_payload(_peer_id: int, _payload: PackedByteArray) -> void:
	pass


## Records the monotonic start of the raw client's authentication deadline.
func _on_raw_peer_authenticating(_peer_id: int) -> void:
	if _auth_waiting:
		return
	_auth_waiting = true
	_auth_wait_started_msec = Time.get_ticks_msec()
	_print_event(
		{
			"event": "auth_waiting",
			"ok": true,
			"role": _role,
			"started_msec": _auth_wait_started_msec,
			"timeout_msec": roundi(HANDSHAKE_TIMEOUT_SECONDS * 1000.0),
		}
	)


## Accepts only an authentication failure delivered after the configured deadline.
func _on_raw_authentication_failed(_peer_id: int) -> void:
	if not _auth_waiting:
		_finish(false, "AUTH_FAILED_BEFORE_WAITING")
		return
	_auth_failure_elapsed_msec = Time.get_ticks_msec() - _auth_wait_started_msec
	var timeout_msec: int = roundi(HANDSHAKE_TIMEOUT_SECONDS * 1000.0)
	if _auth_failure_elapsed_msec < timeout_msec:
		_finish(false, "AUTH_FAILED_BEFORE_DEADLINE")
		return
	_finish(true, "HANDSHAKE_TIMEOUT")


## Rejects server loss because only peer_authentication_failed proves the deadline.
func _on_raw_server_disconnected() -> void:
	var detail: String = (
		"SERVER_DISCONNECTED_DURING_AUTH"
		if _auth_waiting
		else "SERVER_DISCONNECTED_BEFORE_AUTH"
	)
	_finish(false, detail)


## Emits host endpoint readiness without a startup sleep.
func _on_peer_ready(_operation_id: int, _peer: MultiplayerPeer) -> void:
	if _role != ROLE_HOST:
		return
	_host_ready = true
	_print_event(
		{
			"event": "host_ready",
			"ok": true,
			"port": _port,
			"scenario": _scenario,
		}
	)


## Records current session phases and handles expected client-side failures.
func _on_session_changed(view: Dictionary) -> void:
	_print_event(
		{
			"event": "session",
			"failure": String(view.get("failure", {}).get("code", &"")),
			"phase": String(view.phase),
			"role": _role,
		}
	)
	if _role != ROLE_CLIENT:
		return
	var failure_code: StringName = view.get("failure", {}).get("code", &"")
	if _scenario == SCENARIO_INCOMPATIBLE and failure_code == &"INCOMPATIBLE":
		_closing = true
	if view.phase != SessionService.PHASE_IDLE:
		return
	if _scenario == SCENARIO_HOST_LOSS:
		var host_loss: bool = failure_code == &"HOST_LOST"
		_finish(host_loss, "HOST_LOST" if host_loss else "WRONG_FAILURE")
	elif _scenario == SCENARIO_SUSTAINED:
		var host_closed_after_success: bool = failure_code == &"HOST_LOST" and _success_ready
		_finish(
			host_closed_after_success,
			"" if host_closed_after_success else "SUSTAINED_HOST_LOST_EARLY",
		)


## Observes admitted identities and requests host-loss exit only after real admission.
func _on_participant_admitted(_native_peer_id: int, _participant_id: int) -> void:
	_peer_seen = true
	_print_event({ "event": "participant_admitted", "ok": true, "role": _role })
	if _scenario == SCENARIO_HOST_LOSS and _role == ROLE_HOST:
		_print_event({ "event": "host_loss_exit", "ok": true, "role": _role })
		_tree.quit(0)


## Lets a successful gameplay client close first, then cleanly retires the host.
func _on_participant_disconnected(_native_peer_id: int, _participant_id: int) -> void:
	if _role == ROLE_HOST and _success_ready:
		_begin_clean_close()


## Accepts expected pre-admission rejection or timeout only after a real peer was seen.
func _on_transport_disconnected(
	_operation_id: int,
	_connection_token: int,
	_native_peer_id: int,
	_failure: Dictionary,
) -> void:
	_peer_seen = true
	if _role != ROLE_HOST or not _host_ready:
		return
	if _scenario in [SCENARIO_INCOMPATIBLE, SCENARIO_ADMISSION_TIMEOUT]:
		_success_ready = true
		_begin_clean_close()


## Binds the saved Match after Boot has completed its ordinary ACTIVE handoff.
func _bind_match() -> void:
	if is_instance_valid(_replication):
		return
	var match: Node3D = _match_provider.call() as Node3D
	if not is_instance_valid(match):
		return
	_replication = match.get_node_or_null("Replication") as MatchReplication
	if _replication == null:
		_finish(false, "MATCH_REPLICATION_MISSING")
		return
	_replication.input_granted.connect(_on_input_granted)
	_replication.input_recovered.connect(_on_input_recovered)
	_replication.movement_applied.connect(_on_movement_applied)
	if _scenario in [SCENARIO_GAMEPLAY, SCENARIO_SUSTAINED]:
		_replication.set_local_input_enabled(false)
		var rig: LocalRig = match.get_node_or_null("LocalRig") as LocalRig
		if rig != null and _role == ROLE_HOST:
			rig.set_actor_control_enabled(false)
	_print_event(
		{
			"event": "match_ready",
			"brackett_loaded": match.get_node_or_null("World") != null,
			"ok": match.get_node_or_null("World") != null,
			"role": _role,
		}
	)


## Opens client deterministic intent only after production hydration grants input.
func _on_input_granted(participant_id: int) -> void:
	if participant_id == REMOTE_PARTICIPANT_ID:
		_input_granted = true
		_sequence = 0


## Keeps deterministic acceptance numbering aligned with production input recovery.
func _on_input_recovered(participant_id: int) -> void:
	if participant_id == REMOTE_PARTICIPANT_ID:
		_sequence = 0


## Confirms a retained prediction existed before the next local authority receipt.
func _on_movement_applied(participant_id: int) -> void:
	if _role != ROLE_CLIENT or participant_id != REMOTE_PARTICIPANT_ID:
		return
	_local_authority_receipts += 1
	if (
		_prediction_waiting_for_authority
		and _local_authority_receipts > _prediction_receipts_before_submit
	):
		_prediction_before_authority_receipt = true
		_prediction_waiting_for_authority = false


## Moves both real players and records prediction and remote smoothing measurements.
func _step_gameplay(delta_seconds: float) -> void:
	var host_actor: ActorMotion = _replication.actor_for_participant(HOST_PARTICIPANT_ID)
	var client_actor: ActorMotion = _replication.actor_for_participant(REMOTE_PARTICIPANT_ID)
	if host_actor == null or client_actor == null:
		return
	if not _initial_positions.has(HOST_PARTICIPANT_ID):
		_initial_positions[HOST_PARTICIPANT_ID] = host_actor.global_position.x
		_initial_positions[REMOTE_PARTICIPANT_ID] = client_actor.global_position.x

	if _role == ROLE_HOST:
		var rig: LocalRig = _replication.get_parent().get_node_or_null("LocalRig") as LocalRig
		if rig != null:
			rig.set_actor_control_enabled(false)
		_host_sequence += 1
		host_actor.step(
			FootCommand.new(
				_host_sequence, _host_sequence, Vector2.RIGHT, 0.0, false, false
			),
			delta_seconds,
			ActorMotion.StepMode.AUTHORITY,
		)
		_host_moved = _host_moved or (
			host_actor.global_position.x
			>= _initial_positions[HOST_PARTICIPANT_ID] + REQUIRED_MOVEMENT_METRES
		)
		_client_moved = _client_moved or (
			client_actor.global_position.x
			>= _initial_positions[REMOTE_PARTICIPANT_ID] + REQUIRED_MOVEMENT_METRES
		)
	else:
		if _input_granted:
			_submit_and_measure_prediction(client_actor, delta_seconds)
		_client_moved = _client_moved or (
			client_actor.global_position.x
			>= _initial_positions[REMOTE_PARTICIPANT_ID] + REQUIRED_MOVEMENT_METRES
		)
		_track_remote_presentation(host_actor)


## Submits one command and proves local replay moved before its authority receipt.
func _submit_and_measure_prediction(actor: ActorMotion, delta_seconds: float) -> void:
	_sequence += 1
	var before_position: Vector3 = actor.global_position
	var receipts_before: int = _local_authority_receipts
	var prediction: FootPrediction = _replication._prediction_owner()
	var acknowledgement_before: int = prediction.acknowledgement()
	var predicted: bool = _replication.predict_and_submit_local_command(
		FootCommand.new(_sequence, _sequence, Vector2.RIGHT, 0.0, false, false),
		delta_seconds,
	)
	var displacement: float = actor.global_position.distance_to(before_position)
	var history_size: int = prediction.history_size()
	_prediction_peak_history = maxi(_prediction_peak_history, history_size)
	if (
		predicted
		and receipts_before == _local_authority_receipts
		and _sequence > acknowledgement_before
		and history_size > 0
		and displacement > PREDICTED_DISPLACEMENT_EPSILON_METRES
	):
		_prediction_succeeded = true
		_prediction_waiting_for_authority = true
		_prediction_receipts_before_submit = receipts_before
		_prediction_unacknowledged_displacement_metres = maxf(
			_prediction_unacknowledged_displacement_metres,
			displacement,
		)


## Proves presentation advances on stationary-root frames with bounded frame jumps.
func _track_remote_presentation(actor: ActorMotion) -> void:
	if _remote_smoothed or _dead_observed:
		return
	var presentation: Node3D = actor.get_node_or_null("PresentationAnchor") as Node3D
	if presentation == null:
		return
	var root_position: Vector3 = actor.global_position
	var display_position: Vector3 = presentation.global_position
	if _remote_display_start_position == Vector3.INF:
		_remote_display_start_position = display_position
		_remote_previous_root_position = root_position
		_remote_previous_display_position = display_position
		return

	var root_delta: float = root_position.distance_to(_remote_previous_root_position)
	var display_delta: float = display_position.distance_to(_remote_previous_display_position)
	_remote_display_max_jump_metres = maxf(_remote_display_max_jump_metres, display_delta)
	if _remote_display_max_jump_metres > MAX_REMOTE_FRAME_JUMP_METRES:
		_finish(false, "REMOTE_PRESENTATION_JUMP")
		return
	if (
		root_delta <= STATIONARY_ROOT_EPSILON_METRES
		and display_delta > PRESENTATION_MOVEMENT_EPSILON_METRES
	):
		_remote_stationary_root_frames += 1
		_remote_stationary_display_displacement_metres += display_delta
	_remote_previous_root_position = root_position
	_remote_previous_display_position = display_position
	_remote_smoothed = (
		display_position.distance_to(_remote_display_start_position)
		>= REQUIRED_MOVEMENT_METRES
		and _remote_stationary_root_frames > 0
		and _remote_stationary_display_displacement_metres
		> PRESENTATION_MOVEMENT_EPSILON_METRES
	)


## Holds real client intent for ten seconds and measures continuity and replicated facing.
func _step_sustained(delta_seconds: float) -> void:
	var host_actor: ActorMotion = _replication.actor_for_participant(HOST_PARTICIPANT_ID)
	var client_actor: ActorMotion = _replication.actor_for_participant(REMOTE_PARTICIPANT_ID)
	if host_actor == null or client_actor == null:
		return
	if _role == ROLE_CLIENT and not _input_granted:
		return
	if _sustained_previous_positions.is_empty():
		_sustained_previous_positions = {
			HOST_PARTICIPANT_ID: host_actor.global_position,
			REMOTE_PARTICIPANT_ID: client_actor.global_position,
		}
		_sustained_distances = { HOST_PARTICIPANT_ID: 0.0, REMOTE_PARTICIPANT_ID: 0.0 }
		_sustained_window_previous = _display_position(client_actor)

	_sustained_tick += 1
	var movement_active: bool = _sustained_tick <= SUSTAINED_MOVEMENT_TICKS
	var movement_phase: int = floori(float(_sustained_tick - 1) / 60.0)
	var direction: Vector2 = Vector2.RIGHT if movement_phase % 2 == 0 else Vector2.LEFT
	if not movement_active:
		direction = Vector2.ZERO
	_drive_sustained_local(direction, movement_active, host_actor, delta_seconds)
	_measure_sustained_motion(host_actor, client_actor, movement_active)
	var local_actor: ActorMotion = host_actor if _role == ROLE_HOST else client_actor
	_sustained_local_yaw_min = minf(_sustained_local_yaw_min, local_actor.rotation.y)
	_sustained_local_yaw_max = maxf(_sustained_local_yaw_max, local_actor.rotation.y)
	if _sustained_tick < SUSTAINED_MOVEMENT_TICKS + SUSTAINED_SETTLE_TICKS:
		return

	_complete_sustained()


## Applies one deterministic held command through the role's production movement path.
func _drive_sustained_local(
	direction: Vector2,
	movement_active: bool,
	host_actor: ActorMotion,
	delta_seconds: float,
) -> void:
	if _role == ROLE_HOST:
		_host_sequence += 1
		var host_yaw: float = (
			sin(float(_sustained_tick) * 0.03) * 1.2
			if movement_active
			else HOST_FINAL_AIM_YAW
		)
		host_actor.step(
			FootCommand.new(
				_host_sequence, _host_sequence, direction, host_yaw, false, false
			),
			delta_seconds,
			ActorMotion.StepMode.AUTHORITY,
		)
		return

	_sequence += 1
	var client_yaw: float = (
		cos(float(_sustained_tick) * 0.03) * 1.2
		if movement_active
		else CLIENT_FINAL_AIM_YAW
	)
	_replication.predict_and_submit_local_command(
		FootCommand.new(_sequence, _sequence, direction, client_yaw, false, false),
		delta_seconds,
	)


## Completes sustained acceptance only after distance, continuity, and facing all pass.
func _complete_sustained() -> void:
	var host_distance: float = float(_sustained_distances[HOST_PARTICIPANT_ID])
	var client_distance: float = float(_sustained_distances[REMOTE_PARTICIPANT_ID])
	_success_ready = (
		(_role == ROLE_HOST or _sustained_window_failures == 0)
		and host_distance > 1.0
		and client_distance >= host_distance * MINIMUM_CLIENT_HOST_DISTANCE_RATIO
		and _sustained_local_yaw_max - _sustained_local_yaw_min >= 1.5
		and _sustained_facing_converged()
	)
	if (
		_success_ready
		and _role == ROLE_HOST
		and _sustained_tick
		>= SUSTAINED_MOVEMENT_TICKS + SUSTAINED_SETTLE_TICKS + SUSTAINED_CLOSE_GRACE_TICKS
	):
		_begin_clean_close()


## Accumulates both paths and rejects any stationary quarter-second client display window.
func _measure_sustained_motion(
	host_actor: ActorMotion,
	client_actor: ActorMotion,
	movement_active: bool,
) -> void:
	for participant_id: int in [HOST_PARTICIPANT_ID, REMOTE_PARTICIPANT_ID]:
		var actor: ActorMotion = (
			host_actor if participant_id == HOST_PARTICIPANT_ID else client_actor
		)
		var previous: Vector3 = _sustained_previous_positions[participant_id]
		_sustained_distances[participant_id] = (
			float(_sustained_distances[participant_id])
			+ actor.global_position.distance_to(previous)
		)
		_sustained_previous_positions[participant_id] = actor.global_position
	if _role != ROLE_CLIENT or not movement_active:
		return

	var display_position: Vector3 = _display_position(client_actor)
	_sustained_window_distance += display_position.distance_to(_sustained_window_previous)
	_sustained_window_previous = display_position
	if _sustained_tick % CONTINUITY_WINDOW_TICKS != 0:
		return

	_sustained_minimum_window_metres = minf(
		_sustained_minimum_window_metres, _sustained_window_distance
	)
	if _sustained_window_distance < MINIMUM_WINDOW_DISTANCE_METRES:
		_sustained_window_failures += 1
	_sustained_window_distance = 0.0


## Reads the authored presentation pose used by the local camera and player.
func _display_position(actor: ActorMotion) -> Vector3:
	var presentation: Node3D = actor.get_node_or_null("PresentationAnchor") as Node3D
	return presentation.global_position if presentation != null else actor.global_position


## Checks both simulated facings after the moving aim targets settle.
func _sustained_facing_converged() -> bool:
	if not is_instance_valid(_replication):
		return false
	var host_actor: ActorMotion = _replication.actor_for_participant(HOST_PARTICIPANT_ID)
	var client_actor: ActorMotion = _replication.actor_for_participant(REMOTE_PARTICIPANT_ID)
	if host_actor == null or client_actor == null:
		return false
	return (
		absf(angle_difference(host_actor.rotation.y, HOST_FINAL_AIM_YAW))
		<= FACING_TOLERANCE_RADIANS
		and absf(angle_difference(client_actor.rotation.y, CLIENT_FINAL_AIM_YAW))
		<= FACING_TOLERANCE_RADIANS
	)


## Drives death, respawn, reset, and post-reset input through their production owners.
func _observe_lifecycle() -> void:
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
	if (
		not _reset_observed
		and _replication.match_revision() > 1
		and bool(view.get("alive", false))
		and generation > _respawn_generation
	):
		_reset_observed = true
		_input_granted = _role == ROLE_HOST
		_sequence = 0

	if _role == ROLE_HOST:
		_drive_host_lifecycle()
	else:
		_check_client_success()


## Requests terminal transitions only after both players have moved under authority.
func _drive_host_lifecycle() -> void:
	if _host_moved and _client_moved and not _dead_observed:
		if not _replication.trigger_test_death(REMOTE_PARTICIPANT_ID):
			_finish(false, "DEATH_TRIGGER_REJECTED")
		return
	if _respawn_observed and not _reset_requested:
		_reset_requested = _replication.request_match_reset(HOST_PARTICIPANT_ID)
		if not _reset_requested:
			_finish(false, "RESET_REJECTED")
	if _reset_observed:
		# The client receipt independently requires post-reset input and motion before leave.
		_success_ready = true


## Requires prediction, remote smoothing, lifecycle, and post-reset movement on the client.
func _check_client_success() -> void:
	if not _reset_observed or not _input_granted:
		return
	var actor: ActorMotion = _replication.actor_for_participant(REMOTE_PARTICIPANT_ID)
	if actor == null:
		return
	if is_nan(_post_reset_start_x):
		_post_reset_start_x = actor.global_position.x
		return
	if (
		actor.global_position.x >= _post_reset_start_x + REQUIRED_MOVEMENT_METRES
		and _client_moved
		and _prediction_succeeded
		and _prediction_before_authority_receipt
		and _prediction_peak_history > 0
		and _prediction_unacknowledged_displacement_metres
		> PREDICTED_DISPLACEMENT_EPSILON_METRES
		and _remote_smoothed
	):
		_success_ready = true
		_begin_clean_close()


## Leaves through SessionService and waits for its cleanup completion before exit.
func _begin_clean_close() -> void:
	if _closing:
		return
	_closing = true
	if _scenario == SCENARIO_SUSTAINED and _role == ROLE_HOST:
		_replication.set_physics_process(false)
	if not _session.leave().get("ok", false):
		_finish(false, "LEAVE_REJECTED")


## Emits the final receipt only after ordinary Session cleanup restores IDLE.
func _on_session_completed(_operation_id: int, result: Dictionary) -> void:
	if _finished or not _closing:
		return
	var failure_code: String = String(result.get("failure", {}).get("code", &""))
	var expected_client_rejection: bool = (
		_role == ROLE_CLIENT
		and _scenario == SCENARIO_INCOMPATIBLE
		and failure_code == "INCOMPATIBLE"
	)
	if expected_client_rejection:
		_finish(true, failure_code)
	elif _success_ready and result.get("ok", false):
		_finish(true, "")
	elif _scenario == SCENARIO_INCOMPATIBLE and _role == ROLE_CLIENT:
		_finish(false, failure_code)


## Prints one machine-readable event for runner readiness and review receipts.
func _print_event(event: Dictionary) -> void:
	print(PREFIX + JSON.stringify(event))


## Emits one terminal receipt and exits with a truthful process status.
func _finish(ok: bool, detail: String) -> void:
	if _finished:
		return
	_finished = true
	_print_event(_result_receipt(ok, detail))
	_tree.quit(0 if ok else 1)


## Builds the complete review receipt without changing acceptance state.
func _result_receipt(ok: bool, detail: String) -> Dictionary:
	var prediction_history_bounded: bool = (
		_role == ROLE_HOST
		or not is_instance_valid(_replication)
		or (
			_prediction_peak_history <= FootPrediction.HISTORY_CAPACITY
			and int(_replication._prediction_owner().diagnostics().history_size)
			<= FootPrediction.HISTORY_CAPACITY
		)
	)
	return {
		"auth_failure_elapsed_msec": _auth_failure_elapsed_msec,
		"auth_timeout_msec": roundi(HANDSHAKE_TIMEOUT_SECONDS * 1000.0),
		"auth_waiting": _auth_waiting,
		"brackett_loaded": (
			is_instance_valid(_replication)
			and _replication.get_parent().get_node_or_null("World") != null
		),
		"client_moved": _client_moved,
		"dead_observed": _dead_observed,
		"detail": detail,
		"event": "finished",
		"host_moved": _host_moved,
		"match_revision": (
			_replication.match_revision() if is_instance_valid(_replication) else 0
		),
		"ok": ok,
		"peer_seen": _peer_seen,
		"prediction_before_authority_receipt": _prediction_before_authority_receipt,
		"prediction_bounded": prediction_history_bounded,
		"prediction_peak_history": _prediction_peak_history,
		"prediction_succeeded": _prediction_succeeded,
		"prediction_unacknowledged_displacement_metres": (
			_prediction_unacknowledged_displacement_metres
		),
		"remote_display_max_jump_metres": _remote_display_max_jump_metres,
		"remote_smoothed": _remote_smoothed,
		"remote_stationary_display_displacement_metres": (
			_remote_stationary_display_displacement_metres
		),
		"remote_stationary_root_frames": _remote_stationary_root_frames,
		"reset_observed": _reset_observed,
		"respawn_observed": _respawn_observed,
		"role": _role,
		"scenario": _scenario,
		"steam_class_absent": not ClassDB.class_exists("Steam"),
		"steam_singleton_absent": not Engine.has_singleton("Steam"),
	}.merged(_sustained_receipt())


## Builds sustained fields separately so every terminal scenario shares one receipt shape.
func _sustained_receipt() -> Dictionary:
	return {
		"sustained_client_distance_metres": float(
			_sustained_distances.get(REMOTE_PARTICIPANT_ID, 0.0)
		),
		"sustained_continuity_window_failures": _sustained_window_failures,
		"sustained_duration_seconds": (
			float(mini(_sustained_tick, SUSTAINED_MOVEMENT_TICKS)) / 60.0
		),
		"sustained_facing_converged": _scenario == SCENARIO_SUSTAINED and _success_ready,
		"sustained_facing_span_radians": (
			0.0
			if is_inf(_sustained_local_yaw_min)
			else _sustained_local_yaw_max - _sustained_local_yaw_min
		),
		"sustained_host_distance_metres": float(
			_sustained_distances.get(HOST_PARTICIPANT_ID, 0.0)
		),
		"sustained_minimum_window_metres": (
			0.0
			if is_inf(_sustained_minimum_window_metres)
			else _sustained_minimum_window_metres
		),
	}
