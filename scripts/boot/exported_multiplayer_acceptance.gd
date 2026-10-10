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
const PROCESS_TIMEOUT_MSEC: int = 120_000
const HANDSHAKE_TIMEOUT_SECONDS: float = 0.75
const REQUIRED_MOVEMENT_METRES: float = 0.5
const REMOTE_PARTICIPANT_ID: int = 2
const HOST_PARTICIPANT_ID: int = 1

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
	if _scenario not in [SCENARIO_GAMEPLAY, SCENARIO_PLAYTEST]:
		return

	_bind_match()
	if _scenario == SCENARIO_PLAYTEST:
		return
	if not is_instance_valid(_replication) or _replication.player_count() != 2:
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


## Emits readiness only after the raw client has reached authentication.
func _on_raw_peer_authenticating(_peer_id: int) -> void:
	_print_event({ "event": "auth_waiting", "ok": true, "role": _role })


## Accepts only SceneMultiplayer's bounded authentication failure in this scenario.
func _on_raw_authentication_failed(_peer_id: int) -> void:
	_finish(true, "HANDSHAKE_TIMEOUT")


## Treats host removal as timeout only after the silent client reached the auth phase.
func _on_raw_server_disconnected() -> void:
	_finish(true, "HANDSHAKE_TIMEOUT")


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


## Moves both real players and reads the remote presentation anchor for smoothing proof.
func _step_gameplay(delta_seconds: float) -> void:
	var host_actor: ActorMotion = _replication.actor_for_participant(HOST_PARTICIPANT_ID)
	var client_actor: ActorMotion = _replication.actor_for_participant(REMOTE_PARTICIPANT_ID)
	if host_actor == null or client_actor == null:
		return
	if not _initial_positions.has(HOST_PARTICIPANT_ID):
		_initial_positions[HOST_PARTICIPANT_ID] = host_actor.global_position.x
		_initial_positions[REMOTE_PARTICIPANT_ID] = client_actor.global_position.x

	if _role == ROLE_HOST:
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
			_sequence += 1
			_replication.predict_and_submit_local_command(
				FootCommand.new(
					_sequence, _sequence, Vector2.RIGHT, 0.0, false, false
				),
				delta_seconds,
			)
		_client_moved = _client_moved or (
			client_actor.global_position.x
			>= _initial_positions[REMOTE_PARTICIPANT_ID] + REQUIRED_MOVEMENT_METRES
		)
		var presentation: Node3D = host_actor.get_node_or_null("PresentationAnchor") as Node3D
		if presentation != null:
			_remote_smoothed = _remote_smoothed or (
				presentation.global_position.x
				>= _initial_positions[HOST_PARTICIPANT_ID] + REQUIRED_MOVEMENT_METRES
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
		and _remote_smoothed
	):
		_success_ready = true
		_begin_clean_close()


## Leaves through SessionService and waits for its cleanup completion before exit.
func _begin_clean_close() -> void:
	if _closing:
		return
	_closing = true
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
	_print_event(
		{
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
			"prediction_bounded": (
				_role == ROLE_HOST
				or not is_instance_valid(_replication)
				or int(_replication._prediction_owner().diagnostics().history_size)
				<= FootPrediction.HISTORY_CAPACITY
			),
			"remote_smoothed": _remote_smoothed,
			"reset_observed": _reset_observed,
			"respawn_observed": _respawn_observed,
			"role": _role,
			"scenario": _scenario,
			"steam_class_absent": not ClassDB.class_exists("Steam"),
			"steam_singleton_absent": not Engine.has_singleton("Steam"),
		}
	)
	_tree.quit(0 if ok else 1)
