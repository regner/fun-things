class_name S04TMatch  # gdstyle:ignore=quality/max-class-variables
extends Node3D
## Exercises authoritative seat transfer between the existing predicted foot and car bodies.

const EXIT_STOP_SPEED_MPS: float = 0.5
const PARKED_SPEED_MPS: float = 0.01
const SNAPSHOT_INTERVAL_TICKS: int = 2
const DRIVE_BEFORE_DISCONNECT_TICKS: int = 30
const RACE_CLAIMANT_ID: int = 1

var role: String = ""
var port: int = 0
var peer_id: int = 0
var active: bool = false
var host_tick: int = 0
var input_tick: int = 0
var action_sequence: int = 0
var control_revision: int = 1
var local_mode: String = "foot"
var local_vehicle: String = ""
var host_mode: String = "foot"
var host_vehicle: String = ""
var seat_claimant: int = 0
var latest_input: Dictionary = {}
var processed_input_tick: int = 0
var pending_action: bool = false
var stage: String = "connecting"
var stage_tick: int = 0
var stopped_exit_count: int = 0
var race_complete: bool = false
var traffic_ai_active: bool = true
var coasting: bool = false
var coast_start: Vector3 = Vector3.ZERO
var transition_request_ms: int = 0
var first_control_ms: int = 0
var history_clean: bool = true
var ownership_clean: bool = true
var moving_rejected: bool = false
var blocked_rejected: bool = false
var traffic_stolen: bool = false
var disconnected_driver: bool = false
var client_transitions: Array[Dictionary] = []
var foot_history: S03PredictionHistory = S03PredictionHistory.new()
var car_history: S03PredictionHistory = S03PredictionHistory.new()
var action_queue: Array[Dictionary] = []
var latest_snapshot: Dictionary = {}
var _capture_labels: Dictionary = {}

@onready var foot: S03RActor = $Foot
@onready var parked_car: S04Kinematic = $ParkedCar
@onready var traffic_car: S04Kinematic = $TrafficCar
@onready var camera_rig: Node3D = $CameraRig
@onready var _status_label: Label = $Ui/Status


## Creates the requested ENet role from bounded command-line arguments.
func _ready() -> void:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--role="):
			role = argument.trim_prefix("--role=")
		elif argument.begins_with("--port="):
			port = int(argument.trim_prefix("--port="))

	if role not in ["host", "client"] or port < 1 or port > 65_535:
		_fail("invalid role or port")
		return

	_configure_initial_bodies()
	multiplayer.peer_disconnected.connect(_peer_disconnected)
	if role == "host":
		_start_host()
	else:
		multiplayer.connected_to_server.connect(_connected)
		multiplayer.connection_failed.connect(_connection_failed)
		_start_client()


## Advances authority, prediction, and the scripted transition sequence at fixed physics cadence.
func _physics_process(delta: float) -> void:
	if role == "host":
		_host_step(delta)
	elif active:
		_client_step(delta)


## Keeps the saved north-up camera and HUD bound to the currently controlled local body.
func _process(_delta: float) -> void:
	if role != "client" or not active:
		return

	var focus: Vector3 = _local_focus_position()
	camera_rig.position.x = focus.x
	camera_rig.position.z = focus.z


## Configures authored bodies without allowing passive replicas to simulate.
func _configure_initial_bodies() -> void:
	foot.visible = true
	parked_car.configure(role == "host")
	traffic_car.configure(role == "host")
	if role == "client":
		foot.predicted_local = true
		foot.collision_layer = S04DriveRules.CAR_COLLISION_MASK & 2
		foot.collision_mask = 1


## Opens the single authoritative endpoint and advertises readiness to the runner.
func _start_host() -> void:
	var peer := ENetMultiplayerPeer.new()
	var error: Error = peer.create_server(port, 1)
	if error != OK:
		_fail("host open failed: %s" % error_string(error))
		return

	multiplayer.multiplayer_peer = peer
	active = true
	_print_event({ "event": "ready", "port": port })


## Opens one client endpoint through the runner's bounded UDP proxy.
func _start_client() -> void:
	var peer := ENetMultiplayerPeer.new()
	var error: Error = peer.create_client("127.0.0.1", port)
	if error != OK:
		_fail("client open failed: %s" % error_string(error))
		return

	multiplayer.multiplayer_peer = peer


## Begins sender-bound hydration after the native connection succeeds.
func _connected() -> void:
	_hello.rpc_id(1)


## Fails the client rather than silently waiting after native connection failure.
func _connection_failed() -> void:
	_fail("connection failed")


## Hydrates only the actual remote sender with the complete initial transition cut.
@rpc("any_peer", "call_remote", "reliable", 0)
func _hello() -> void:
	if role != "host":
		return

	peer_id = multiplayer.get_remote_sender_id()
	_baseline.rpc_id(peer_id, _snapshot_state())


## Installs the initial authoritative cut before opening local prediction.
@rpc("authority", "call_remote", "reliable", 0)
func _baseline(snapshot: Dictionary) -> void:
	if role != "client" or active:
		return

	latest_snapshot = snapshot.duplicate(true)
	_install_all_passive(snapshot)
	_switch_to_foot(snapshot, false, "baseline")
	active = true
	stage = "warmup"
	stage_tick = input_tick
	_print_event(
		{
			"event": "start",
			"time_ms": Time.get_ticks_msec(),
			"window_can_draw": not DisplayServer.get_name().contains("headless"),
		}
	)


## Advances the traffic owner, admitted controller, ordered actions, and replication.
func _host_step(delta: float) -> void:
	if not active:
		return

	host_tick += 1
	if traffic_ai_active:
		traffic_car.step(_drive_command(0.35, 0.08, 0.0), delta)
	elif coasting:
		traffic_car.step(S04DriveRules.neutral(), delta)
		if traffic_car.velocity.length() < PARKED_SPEED_MPS:
			traffic_car.neutralize()
			coasting = false
			_finish_host()

	if host_mode == "foot":
		foot.step(_host_foot_command(), delta)
	elif host_mode == "car":
		_controlled_car().step(_host_drive_command(), delta)
	processed_input_tick = int(latest_input.get("tick", processed_input_tick))

	_process_actions()
	if peer_id > 0 and host_tick % SNAPSHOT_INTERVAL_TICKS == 0:
		_snapshot.rpc_id(peer_id, _snapshot_state())


## Simulates one immediate local frame, records it, and drives the bounded scenario.
func _client_step(delta: float) -> void:
	input_tick += 1
	if local_mode == "foot":
		var command: Dictionary = _foot_command()
		foot.step(command, delta)
		foot.latest_predicted_tick = input_tick
		foot_history.push(input_tick, command, delta)
		_submit_input.rpc_id(1, "foot", control_revision, input_tick, command)
	elif local_mode == "car":
		var command: Dictionary = _client_drive_command()
		_controlled_car().step(command, delta)
		_controlled_car().latest_input_tick = input_tick
		car_history.push(input_tick, command, delta)
		_submit_input.rpc_id(1, local_vehicle, control_revision, input_tick, command)
		if first_control_ms == 0:
			first_control_ms = Time.get_ticks_msec()

	_advance_client_scenario()


## Accepts held input only from the connected sender and current host-owned binding.
@rpc("any_peer", "call_remote", "unreliable_ordered", 1)
func _submit_input(mode: String, revision: int, tick: int, command: Dictionary) -> void:
	if role != "host" or multiplayer.get_remote_sender_id() != peer_id:
		return
	if revision != control_revision or tick <= int(latest_input.get("tick", 0)):
		return
	if mode != (host_vehicle if host_mode == "car" else host_mode):
		return

	latest_input = {
		"mode": mode, "revision": revision, "tick": tick, "command": command.duplicate(true),
	}


## Queues a reliable action with identity derived from the RPC sender.
@rpc("any_peer", "call_remote", "reliable", 0)
func _request_action(sequence: int, kind: String, vehicle: String) -> void:
	if role != "host" or multiplayer.get_remote_sender_id() != peer_id:
		return
	if sequence <= 0 or kind not in ["enter", "exit"]:
		return

	action_queue.append(
		{
			"participant": peer_id,
			"sequence": sequence,
			"kind": kind,
			"vehicle": vehicle,
			"accepted_tick": host_tick,
		}
	)


## Identifies the first parked-car request that triggers the scripted competing claimant.
func _is_parked_enter(action: Dictionary) -> bool:
	return action.kind == "enter" and action.vehicle == "parked"


## Applies same-tick claims in deterministic participant/sequence order on authority.
func _process_actions() -> void:
	if action_queue.is_empty():
		return

	var actions: Array[Dictionary] = action_queue.duplicate(true)
	action_queue.clear()
	if not race_complete and actions.any(_is_parked_enter):
		var competing_tick: int = int(actions[0].accepted_tick)
		actions.append(
			{
				"participant": RACE_CLAIMANT_ID,
				"sequence": 1,
				"kind": "enter",
				"vehicle": "parked",
				"accepted_tick": competing_tick,
			}
		)
		race_complete = true

	actions.sort_custom(
		func(left: Dictionary, right: Dictionary) -> bool:
			if left.accepted_tick != right.accepted_tick:
				return left.accepted_tick < right.accepted_tick
			if left.participant != right.participant:
				return left.participant < right.participant
			return left.sequence < right.sequence
	)
	for action: Dictionary in actions:
		_apply_action(action)

	if seat_claimant == RACE_CLAIMANT_ID:
		seat_claimant = 0
		host_vehicle = ""
		_print_event(
			{
				"event": "seat_race",
				"winner": RACE_CLAIMANT_ID,
				"loser": peer_id,
				"accepted_tick": host_tick,
			}
		)


## Owns enter/exit checks so rejection never partially changes seat state.
func _apply_action(action: Dictionary) -> void:
	if action.kind == "enter":
		_apply_enter(action)
	else:
		_apply_exit(action)


## Grants one available seat and stops traffic control before player control begins.
func _apply_enter(action: Dictionary) -> void:
	var participant: int = action.participant
	var vehicle: String = action.vehicle
	var failure: String = ""
	if host_mode != "foot" or seat_claimant != 0:
		failure = "SEAT_OCCUPIED"
	elif vehicle not in ["parked", "traffic"]:
		failure = "INVALID_VEHICLE"

	if failure.is_empty():
		seat_claimant = participant
		host_vehicle = vehicle
		if participant == peer_id:
			if vehicle == "traffic":
				traffic_ai_active = false
				traffic_stolen = true
			host_mode = "car"
			control_revision += 1
			latest_input.clear()
			foot.neutralize()
		else:
			failure = "SCRIPTED_CLAIM"

	if participant == peer_id:
		_send_action_result(action.sequence, failure, vehicle)


## Rejects moving or blocked exits atomically, then places a successful exit on authority.
func _apply_exit(action: Dictionary) -> void:
	var failure: String = ""
	if host_mode != "car" or seat_claimant != peer_id:
		failure = "NOT_SEATED"
	elif _controlled_car().velocity.length() >= EXIT_STOP_SPEED_MPS:
		failure = "EXIT_MOVING"
		moving_rejected = true
	elif stopped_exit_count == 0:
		failure = "EXIT_BLOCKED"
		blocked_rejected = true
		stopped_exit_count += 1

	if failure.is_empty():
		var exited_car: S04Kinematic = _controlled_car()
		foot.global_position = exited_car.global_position + Vector3(-1.5, 0.0, 0.0)
		foot.rotation.y = exited_car.rotation.y
		exited_car.neutralize()
		host_mode = "foot"
		host_vehicle = ""
		seat_claimant = 0
		control_revision += 1
		latest_input.clear()

	_send_action_result(action.sequence, failure, host_vehicle)


## Returns the verdict plus authoritative transition poses; it never trusts client state.
func _send_action_result(sequence: int, failure: String, vehicle: String) -> void:
	_action_result.rpc_id(peer_id, sequence, failure, vehicle, control_revision, _snapshot_state())


## Applies a host verdict, clears both replay domains, and records transition discontinuity.
@rpc("authority", "call_remote", "reliable", 0)
func _action_result(
	sequence: int, failure: String, vehicle: String, revision: int, snapshot: Dictionary
) -> void:
	if role != "client" or not pending_action or sequence != action_sequence:
		return

	pending_action = false
	latest_snapshot = snapshot.duplicate(true)
	var previous_focus: Vector3 = _local_focus_position()
	var previous_position: Vector3 = previous_focus
	var requested_stage: String = stage
	var accepted: bool = failure.is_empty()
	if requested_stage in ["race_entry", "parked_entry", "traffic_entry"]:
		if accepted:
			_switch_to_car(vehicle, snapshot, "accepted_entry")
		else:
			_switch_to_foot(snapshot, true, "rejected_entry")
	elif requested_stage in ["moving_exit", "blocked_exit"]:
		ownership_clean = ownership_clean and local_mode == "car"
	elif requested_stage == "successful_exit" and accepted:
		_switch_to_foot(snapshot, true, "accepted_exit")

	control_revision = revision
	var new_focus: Vector3 = _local_focus_position()
	var record: Dictionary = {
		"event": "transition",
		"stage": requested_stage,
		"accepted": accepted,
		"failure": failure,
		"time_ms": Time.get_ticks_msec(),
		"round_trip_ms": Time.get_ticks_msec() - transition_request_ms,
		"time_to_control_ms":
		first_control_ms - transition_request_ms if first_control_ms > 0 else 0,
		"correction_m": previous_position.distance_to(new_focus),
		"visual_jump_m": previous_focus.distance_to(new_focus),
		"foot_history": foot_history.size(),
		"car_history": car_history.size(),
		"camera_owner": str(camera_rig.get_meta("owner_kind", "")),
		"hud_owner": str(_status_label.get_meta("owner_kind", "")),
	}
	client_transitions.append(record)
	_print_event(record)
	_capture_transition(requested_stage)
	_advance_after_result(requested_stage, accepted, failure)


## Buffers authority, reconciles only the active prediction domain, and updates passive cars.
@rpc("authority", "call_remote", "unreliable_ordered", 1)
func _snapshot(snapshot: Dictionary) -> void:
	if role != "client" or not active:
		return

	latest_snapshot = snapshot.duplicate(true)
	if not (local_mode == "car" and local_vehicle == "parked"):
		_install_passive_car(parked_car, snapshot.parked)
	if not (local_mode == "car" and local_vehicle == "traffic"):
		_install_passive_car(traffic_car, snapshot.traffic)
	if pending_action and snapshot.mode != local_mode:
		return

	if local_mode == "foot" and snapshot.mode == "foot":
		_reconcile_foot(snapshot)
	elif local_mode == "car" and snapshot.mode == "car" and snapshot.vehicle == local_vehicle:
		_reconcile_car(snapshot)


## Restores the host foot pose and replays only unacknowledged foot frames.
func _reconcile_foot(snapshot: Dictionary) -> void:
	var result: Dictionary = foot_history.acknowledge(int(snapshot.ack))
	_install_foot_pose(snapshot.foot)
	if result.history_exhausted:
		return
	for frame: Dictionary in result.frames:
		foot.step(frame.command, frame.delta)


## Restores the host car pose and replays only unacknowledged drive frames.
func _reconcile_car(snapshot: Dictionary) -> void:
	var result: Dictionary = car_history.acknowledge(int(snapshot.ack))
	var actor: S04Kinematic = _controlled_car()
	actor.restore_authoritative(snapshot[local_vehicle])
	if result.history_exhausted:
		return
	for frame: Dictionary in result.frames:
		actor.step(frame.command, frame.delta)


## Produces the complete bounded authoritative state used by transitions and snapshots.
func _snapshot_state() -> Dictionary:
	return {
		"tick": host_tick,
		"mode": host_mode,
		"vehicle": host_vehicle,
		"seat_claimant": seat_claimant,
		"control": control_revision,
		"ack": processed_input_tick,
		"foot": _foot_pose(),
		"parked": _car_pose(parked_car),
		"traffic": _car_pose(traffic_car),
		"traffic_ai": traffic_ai_active,
	}


## Encodes the host foot body without serializing engine-owned objects.
func _foot_pose() -> Dictionary:
	return {
		"position": _vector(foot.global_position),
		"yaw": foot.rotation.y,
		"velocity": _vector(foot.velocity),
		"sequence": 0,
	}


## Encodes one car using the existing S04 pose field names required by restore.
func _car_pose(actor: S04Kinematic) -> Dictionary:
	return {
		"position": _vector(actor.global_position),
		"yaw": actor.rotation.y,
		"velocity": _vector(actor.velocity),
		"sequence": 0,
		"input_tick": processed_input_tick,
	}


## Installs every passive baseline body before prediction admission.
func _install_all_passive(snapshot: Dictionary) -> void:
	_install_foot_pose(snapshot.foot)
	_install_passive_car(parked_car, snapshot.parked)
	_install_passive_car(traffic_car, snapshot.traffic)


## Installs one foot pose through the inherited authoritative restore boundary.
func _install_foot_pose(pose: Dictionary) -> void:
	foot.restore_authority(pose)


## Installs a car only while its replica simulation is disabled.
func _install_passive_car(actor: S04Kinematic, pose: Dictionary) -> void:
	if actor.simulation_enabled:
		return
	actor.install_pose(pose, Time.get_ticks_msec())


## Starts predicted entry immediately while retaining the authoritative rejection path.
func _predict_enter(vehicle: String, next_stage: String) -> void:
	if pending_action:
		return

	action_sequence += 1
	pending_action = true
	stage = next_stage
	transition_request_ms = Time.get_ticks_msec()
	first_control_ms = 0
	_switch_to_car(vehicle, latest_snapshot, "predicted_entry")
	_request_action.rpc_id(1, action_sequence, "enter", vehicle)


## Requests exit without pre-empting moving/clearance authority.
func _request_exit(next_stage: String) -> void:
	if pending_action:
		return

	action_sequence += 1
	pending_action = true
	stage = next_stage
	transition_request_ms = Time.get_ticks_msec()
	first_control_ms = 0
	_request_action.rpc_id(1, action_sequence, "exit", "")


## Switches collision, replay, camera, and HUD ownership to one predicted car.
func _switch_to_car(vehicle: String, snapshot: Dictionary, reason: String) -> void:
	foot_history.clear()
	car_history.clear()
	history_clean = history_clean and foot_history.size() == 0 and car_history.size() == 0
	foot.neutralize()
	foot.collision_layer = 0
	foot.collision_mask = 0
	foot.visible = false
	for name: String in ["parked", "traffic"]:
		var actor: S04Kinematic = parked_car if name == "parked" else traffic_car
		if name == vehicle:
			actor.configure_prediction()
			actor.restore_authoritative(snapshot[name])
		else:
			actor.configure(false)
	local_mode = "car"
	local_vehicle = vehicle
	camera_rig.set_meta("owner_kind", "car")
	_status_label.set_meta("owner_kind", "car")
	_status_label.text = "S04-T car / %s" % vehicle
	ownership_clean = ownership_clean and reason != "" and _ownership_matches()


## Switches collision, replay, camera, and HUD ownership back to predicted foot.
func _switch_to_foot(snapshot: Dictionary, install: bool, reason: String) -> void:
	foot_history.clear()
	car_history.clear()
	history_clean = history_clean and foot_history.size() == 0 and car_history.size() == 0
	for actor: S04Kinematic in [parked_car, traffic_car]:
		actor.configure(false)
	foot.visible = true
	foot.collision_layer = 2
	foot.collision_mask = 1
	if install:
		_install_foot_pose(snapshot.foot)
	local_mode = "foot"
	local_vehicle = ""
	camera_rig.set_meta("owner_kind", "foot")
	_status_label.set_meta("owner_kind", "foot")
	_status_label.text = "S04-T foot"
	ownership_clean = ownership_clean and reason != "" and _ownership_matches()


## Drives the deterministic client sequence from replicated outcomes, never local authority.
func _advance_client_scenario() -> void:
	if stage == "warmup" and input_tick - stage_tick >= 20:
		_predict_enter("parked", "race_entry")
	elif stage == "wait_parked_entry" and input_tick - stage_tick >= 8:
		_predict_enter("parked", "parked_entry")
	elif (
		stage == "drive_parked"
		and not pending_action
		and (_controlled_car().latest_authoritative_speed_mps >= EXIT_STOP_SPEED_MPS + 0.2)
	):
		_request_exit("moving_exit")
	elif (
		stage == "brake_parked"
		and not pending_action
		and (_controlled_car().latest_authoritative_speed_mps < 0.4)
	):
		_request_exit("blocked_exit")
	elif stage == "wait_successful_exit" and input_tick - stage_tick >= 8:
		_request_exit("successful_exit")
	elif stage == "wait_traffic_entry" and input_tick - stage_tick >= 8:
		_predict_enter("traffic", "traffic_entry")
	elif stage == "drive_traffic" and input_tick - stage_tick >= DRIVE_BEFORE_DISCONNECT_TICKS:
		_finish_client_and_disconnect()


## Advances the scenario only from matching authoritative action results.
func _advance_after_result(previous_stage: String, accepted: bool, failure: String) -> void:
	stage_tick = input_tick
	if previous_stage == "race_entry" and not accepted and failure == "SEAT_OCCUPIED":
		stage = "wait_parked_entry"
	elif previous_stage == "parked_entry" and accepted:
		stage = "drive_parked"
	elif previous_stage == "moving_exit" and failure == "EXIT_MOVING":
		stage = "brake_parked"
	elif previous_stage == "blocked_exit" and failure == "EXIT_BLOCKED":
		stage = "wait_successful_exit"
	elif previous_stage == "successful_exit" and accepted:
		stage = "wait_traffic_entry"
	elif previous_stage == "traffic_entry" and accepted:
		stage = "drive_traffic"
	else:
		_fail("unexpected action result at %s: %s" % [previous_stage, failure])


## Chooses held foot input for the current scenario without any seated firing path.
func _foot_command() -> Dictionary:
	return { "move": Vector2(0.15, -0.05), "aim_yaw": 0.0, "fire": false }


## Returns the newest admitted foot command or neutral host intent.
func _host_foot_command() -> Dictionary:
	if latest_input.get("mode", "") == "foot":
		return latest_input.command
	return { "move": Vector2.ZERO, "aim_yaw": 0.0, "fire": false }


## Selects acceleration, braking, or coasting for the scripted local car stage.
func _client_drive_command() -> Dictionary:
	if stage in ["brake_parked", "blocked_exit", "wait_successful_exit"]:
		return _drive_command(0.0, 0.0, 1.0)
	return _drive_command(0.8, 0.08, 0.0)


## Returns the newest admitted drive command or neutral host intent.
func _host_drive_command() -> Dictionary:
	if latest_input.get("mode", "") == host_vehicle:
		return latest_input.command
	return S04DriveRules.neutral()


## Supplies one complete drive command with no weapon action.
func _drive_command(throttle: float, steer: float, brake: float) -> Dictionary:
	return { "throttle": throttle, "steer": steer, "brake": brake, "handbrake": false }


## Resolves the currently selected saved car without accepting a wire node identity.
func _controlled_car() -> S04Kinematic:
	return (
		parked_car
		if (local_vehicle if role == "client" else host_vehicle) == "parked"
		else traffic_car
	)


## Returns the camera/HUD source pose for discontinuity measurement.
func _local_focus_position() -> Vector3:
	return foot.global_position if local_mode == "foot" else _controlled_car().global_position


## Checks that camera and HUD flip together with the simulation owner.
func _ownership_matches() -> bool:
	return (
		camera_rig.get_meta("owner_kind") == local_mode
		and _status_label.get_meta("owner_kind") == local_mode
	)


## Captures one post-draw transition receipt when the runner supplied a safe output path.
func _capture_transition(label: String) -> void:
	var directory: String = OS.get_environment("S04_T_CAPTURE_DIR")
	if directory.is_empty() or _capture_labels.has(label):
		return

	_capture_labels[label] = true
	_capture_after_draw.call_deferred(label, directory)


## Saves a bounded technical frame only after RenderingServer completes the draw.
func _capture_after_draw(label: String, directory: String) -> void:
	await RenderingServer.frame_post_draw
	var image: Image = get_viewport().get_texture().get_image()
	var error: Error = image.save_png(directory.path_join(label + ".png"))
	if error != OK:
		_fail("capture failed: %s" % error_string(error))


## Emits the client result before closing its endpoint so authority observes disconnect.
func _finish_client_and_disconnect() -> void:
	if stage == "disconnecting":
		return

	stage = "disconnecting"
	active = false
	var required_stages: Array[String] = [
		"race_entry",
		"parked_entry",
		"moving_exit",
		"blocked_exit",
		"successful_exit",
		"traffic_entry",
	]
	var observed: Dictionary = {}
	for transition: Dictionary in client_transitions:
		observed[transition.stage] = true
	var ok: bool = (
		required_stages.all(func(name: String) -> bool: return observed.has(name))
		and history_clean
		and ownership_clean
		and local_mode == "car"
		and local_vehicle == "traffic"
	)
	_print_event(
		{
			"event": "result",
			"ok": ok,
			"role": "client",
			"history_clean": history_clean,
			"ownership_clean": ownership_clean,
			"transition_count": client_transitions.size(),
		}
	)
	multiplayer.multiplayer_peer.close()
	await get_tree().create_timer(0.15).timeout
	get_tree().quit(0 if ok else 1)


## Releases the driver immediately and coasts the surviving car after disconnect.
func _peer_disconnected(disconnected_peer: int) -> void:
	if role != "host" or disconnected_peer != peer_id or host_mode != "car":
		return

	disconnected_driver = true
	peer_id = 0
	coast_start = _controlled_car().global_position
	coasting = true
	host_mode = "none"
	seat_claimant = 0
	latest_input.clear()
	_print_event({ "event": "disconnect_coast", "speed_mps": traffic_car.velocity.length() })


## Verifies all authority-owned outcomes after neutral coast reaches rest.
func _finish_host() -> void:
	var coast_distance: float = coast_start.distance_to(traffic_car.global_position)
	var ok: bool = (
		race_complete
		and moving_rejected
		and blocked_rejected
		and traffic_stolen
		and not traffic_ai_active
		and disconnected_driver
		and coast_distance > 0.05
		and traffic_car.velocity.length() < PARKED_SPEED_MPS
	)
	_print_event(
		{
			"event": "result",
			"ok": ok,
			"role": "host",
			"race_complete": race_complete,
			"moving_rejected": moving_rejected,
			"blocked_rejected": blocked_rejected,
			"traffic_stolen": traffic_stolen,
			"traffic_ai_active": traffic_ai_active,
			"disconnect_coast_m": coast_distance,
			"final_speed_mps": traffic_car.velocity.length(),
		}
	)
	get_tree().quit(0 if ok else 1)


## Encodes a vector as JSON-safe primitive coordinates.
func _vector(value: Vector3) -> Array[float]:
	return [value.x, value.y, value.z]


## Emits one machine-readable telemetry line with process-local time context.
func _print_event(values: Dictionary) -> void:
	values["wall_ms"] = Time.get_unix_time_from_system() * 1000.0
	print("S04T " + JSON.stringify(values))


## Emits a failing result and exits without concealing the first fixture error.
func _fail(message: String) -> void:
	_print_event({ "event": "result", "ok": false, "role": role, "failure": message })
	get_tree().quit(1)
