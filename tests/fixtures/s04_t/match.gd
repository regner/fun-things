class_name S04TMatch  # gdstyle:ignore=quality/max-class-variables,quality/max-file-length
extends Node3D
## Exercises authoritative seat transfer between the existing predicted foot and car bodies.

const EXIT_STOP_SPEED_MPS: float = 0.5
const PARKED_SPEED_MPS: float = 0.01
const SNAPSHOT_INTERVAL_TICKS: int = 2
const DRIVE_BEFORE_DISCONNECT_TICKS: int = 30
const RACE_CLAIMANT_ID: int = 1
const HELD_EXPIRY_MS: int = 250
const HELD_MESSAGE_BYTES: int = 1200
const HELD_RATE_PER_SECOND: float = 60.0
const HELD_RATE_BURST: float = 8.0
const ACTION_MESSAGE_BYTES: int = 4096
const ACTION_RATE_PER_SECOND: float = 16.0
const ACTION_RATE_BURST: float = 32.0
const ACTION_QUEUE_LIMIT: int = 16
const ACTIONS_PER_TICK: int = 4
const ACTION_RESULT_CACHE: int = 64
const ACTION_SEQUENCE_WINDOW: int = 64
const SNAPSHOT_MESSAGE_BYTES: int = 4096
const MAX_POSITION_M: float = 1000.0
const MAX_INPUT_TICK: int = 2_147_483_647
const ADVERSE_STALL_TICK: int = 900
const ADVERSE_STALL_MS: int = 250
const ADVERSE_FINISH_TICK: int = 960

var role: String = ""
var profile: String = "normal"
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
var input_queue: S03InputFrameQueue = S03InputFrameQueue.new()
var processed_input_sequence: int = 0
var processed_input_tick: int = 0
var input_receipt_ms: int = 0
var current_held_command: Dictionary = {}
var local_input_sequence: int = 0
var local_recent_frames: Array[Dictionary] = []
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
var action_highest_sequence: int = 0
var action_results: Dictionary = {}
var action_result_order: Array[int] = []
var rate_buckets: Dictionary = {}
var hydrated_peers: Dictionary = {}
var latest_snapshot: Dictionary = {}
var input_rejections: Dictionary = {}
var action_rejections: Dictionary = {}
var input_expiry_count: int = 0
var input_superseded_count: int = 0
var input_queue_peak: int = 0
var action_queue_peak: int = 0
var action_processed_peak: int = 0
var control_reset_count: int = 0
var _input_was_expired: bool = false
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
		elif argument.begins_with("--profile="):
			profile = argument.trim_prefix("--profile=")

	if role not in ["host", "client"] or profile not in ["normal", "adverse"] \
			or port < 1 or port > 65_535:
		_fail("invalid role, profile, or port")
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
	_hello.rpc_id(1, { "protocol": 1 })


## Fails the client rather than silently waiting after native connection failure.
func _connection_failed() -> void:
	_fail("connection failed")


## Hydrates one admitted request from the actual sender without response amplification.
@rpc("any_peer", "call_remote", "reliable", 0)
func _hello(request: Variant) -> void:
	if role != "host":
		return

	var sender: int = multiplayer.get_remote_sender_id()
	if not admit_hydration_request(sender, request):
		return

	peer_id = sender
	_baseline.rpc_id(peer_id, _snapshot_state())


## Admits exactly one bounded, exact hydration request for each native peer.
func admit_hydration_request(sender: int, request: Variant) -> bool:
	if sender <= 0 or hydrated_peers.has(sender):
		return false
	if not request is Dictionary or request.size() != 1 or request.get("protocol") != 1:
		return false
	if not _serialized_within(request, 128):
		return false

	hydrated_peers[sender] = true
	return true


## Installs one validated initial authoritative cut before opening local prediction.
@rpc("authority", "call_remote", "reliable", 0)
func _baseline(snapshot: Variant) -> void:
	if role != "client" or active or not _snapshot_valid(snapshot):
		return

	latest_snapshot = (snapshot as Dictionary).duplicate(true)
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
	if profile == "adverse" and host_tick == ADVERSE_STALL_TICK:
		_print_event({ "event": "stall_begin", "tick": host_tick,
			"time_ms": Time.get_ticks_msec() })
		OS.delay_msec(ADVERSE_STALL_MS)
		_print_event({ "event": "stall_end", "tick": host_tick,
			"time_ms": Time.get_ticks_msec() })

	var authority_command: Dictionary = _consume_authority_input()
	if traffic_ai_active:
		traffic_car.step(_drive_command(0.35, 0.08, 0.0), delta)
	elif coasting:
		traffic_car.step(S04DriveRules.neutral(), delta)
		if traffic_car.velocity.length() < PARKED_SPEED_MPS:
			traffic_car.neutralize()
			coasting = false
			_finish_host()

	if host_mode == "foot":
		foot.step(authority_command, delta)
	elif host_mode == "car":
		_controlled_car().step(authority_command, delta)

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
		_send_local_input("foot", command)
	elif local_mode == "car":
		var command: Dictionary = _client_drive_command()
		_controlled_car().step(command, delta)
		_controlled_car().latest_input_tick = input_tick
		car_history.push(input_tick, command, delta)
		_send_local_input(local_vehicle, command)
		if first_control_ms == 0:
			first_control_ms = Time.get_ticks_msec()

	_advance_client_scenario()


## Sends one bounded redundant input batch for the current control revision.
func _send_local_input(mode: String, command: Dictionary) -> void:
	local_input_sequence += 1
	var frame: Dictionary
	if mode == "foot":
		frame = {
			"sequence": local_input_sequence,
			"input_tick": input_tick,
			"move": command.move,
			"aim_yaw": command.aim_yaw,
		}
	else:
		frame = {
			"sequence": local_input_sequence,
			"input_tick": input_tick,
			"throttle": command.throttle,
			"steer": command.steer,
			"brake": command.brake,
			"handbrake": command.handbrake,
		}
	local_recent_frames.append(frame)
	if local_recent_frames.size() > 3:
		local_recent_frames.pop_front()
	_submit_input.rpc_id(1, {
		"mode": mode, "revision": control_revision,
		"frames": local_recent_frames.duplicate(true),
	})


## Accepts held input only from the connected sender and current host-owned binding.
@rpc("any_peer", "call_remote", "unreliable_ordered", 1)
func _submit_input(envelope: Variant) -> void:
	if role != "host":
		return

	var result: String = admit_input_envelope(
		multiplayer.get_remote_sender_id(), envelope, Time.get_ticks_msec()
	)
	if result != "OK":
		_record_rejection(input_rejections, result)


## Validates and queues one exact bounded input envelope without simulating extra steps.
func admit_input_envelope(  # gdstyle:ignore=quality/max-returns
	sender: int, envelope: Variant, now_ms: int
) -> String:
	if sender != peer_id or not hydrated_peers.has(sender):
		return "NOT_ADMITTED"
	if not _held_envelope_valid(envelope) or not _serialized_within(envelope, HELD_MESSAGE_BYTES):
		return "INVALID"
	var data: Dictionary = envelope
	if data.revision != control_revision:
		return "STALE_CONTEXT"
	var expected_mode: String = host_vehicle if host_mode == "car" else host_mode
	if data.mode != expected_mode:
		return "STALE_CONTEXT"
	if not take_rate_token(
			"held", now_ms, HELD_RATE_PER_SECOND, HELD_RATE_BURST
	):
		return "RATE_LIMIT"
	if not input_queue.offer(data.frames, processed_input_sequence, processed_input_tick):
		return "INPUT_QUEUE"
	input_queue_peak = maxi(input_queue_peak, input_queue.size())
	if input_queue.last_offer_added():
		input_receipt_ms = now_ms
		_input_was_expired = false
	return "OK"


## Requires exact envelope/frame fields and finite bounded controls before queue mutation.
func _held_envelope_valid(envelope: Variant) -> bool:  # gdstyle:ignore=quality/max-returns
	if not envelope is Dictionary or envelope.size() != 3:
		return false
	if not envelope.get("mode") is String or envelope.mode not in ["foot", "parked", "traffic"]:
		return false
	if not envelope.get("revision") is int or envelope.revision <= 0:
		return false
	if not envelope.get("frames") is Array:
		return false
	var frames: Array = envelope.frames
	if frames.is_empty() or frames.size() > 3:
		return false

	var previous_sequence: int = -1
	var previous_tick: int = -1
	for frame: Variant in frames:
		if not _input_frame_valid(envelope.mode, frame):
			return false
		if previous_sequence >= 0 and (
				frame.sequence != previous_sequence + 1
				or frame.input_tick != previous_tick + 1
		):
			return false
		previous_sequence = frame.sequence
		previous_tick = frame.input_tick
	return true


## Validates one mode-specific input frame with no ignored or non-finite fields.
func _input_frame_valid(  # gdstyle:ignore=quality/max-returns
	mode: String, frame: Variant
) -> bool:
	if not frame is Dictionary:
		return false
	if not frame.get("sequence") is int or not frame.get("input_tick") is int:
		return false
	if frame.sequence <= 0 or frame.input_tick <= 0 or frame.input_tick > MAX_INPUT_TICK:
		return false
	if mode == "foot":
		if frame.size() != 4 or not frame.get("move") is Vector2 \
				or not frame.get("aim_yaw") is float:
			return false
		var move: Vector2 = frame.move
		return move.is_finite() and move.length_squared() <= 1.0 \
			and is_finite(frame.aim_yaw) and absf(frame.aim_yaw) <= PI
	if frame.size() != 6 or not frame.get("handbrake") is bool:
		return false
	for field: String in ["throttle", "steer", "brake"]:
		if not frame.get(field) is float or not is_finite(frame[field]):
			return false
	return absf(frame.throttle) <= 1.0 and absf(frame.steer) <= 1.0 \
		and frame.brake >= 0.0 and frame.brake <= 1.0


## Consumes or supersedes at most one queued frame and advances only its watermark.
func _consume_authority_input() -> Dictionary:
	var now_ms: int = Time.get_ticks_msec()
	var receipt_age_ms: int = now_ms - input_receipt_ms if input_receipt_ms > 0 else 2_147_483_647
	var expired: bool = receipt_age_ms > HELD_EXPIRY_MS
	var frame: Dictionary = (
		input_queue.supersede_all(processed_input_sequence, processed_input_tick)
		if expired
		else input_queue.pop_next(processed_input_sequence, processed_input_tick)
	)
	var command: Dictionary = _neutral_for_host_mode()
	if not frame.is_empty():
		processed_input_sequence = int(frame.sequence)
		processed_input_tick = int(frame.input_tick)
		input_superseded_count += int(frame.superseded_count)
		if not expired:
			command = _command_from_frame(frame)
		_print_authority_input(frame, command, receipt_age_ms, expired)
	elif expired and not _input_was_expired:
		input_expiry_count += 1
		_input_was_expired = true
		_print_authority_input({}, command, receipt_age_ms, true)
	current_held_command = command.duplicate(true)
	return command


## Converts one validated queued frame into the shared simulation command shape.
func _command_from_frame(frame: Dictionary) -> Dictionary:
	if host_mode == "foot":
		return { "move": frame.move, "aim_yaw": frame.aim_yaw, "fire": false }
	return {
		"throttle": frame.throttle,
		"steer": frame.steer,
		"brake": frame.brake,
		"handbrake": frame.handbrake,
	}


## Returns neutral input for the currently authoritative predicted-body domain.
func _neutral_for_host_mode() -> Dictionary:
	if host_mode == "foot":
		return { "move": Vector2.ZERO, "aim_yaw": foot.rotation.y, "fire": false }
	return S04DriveRules.neutral()


## Emits consumed/superseded watermarks and varying command values for adverse analysis.
func _print_authority_input(
	frame: Dictionary, command: Dictionary, receipt_age_ms: int, expired: bool
) -> void:
	var sample: Array[float]
	if host_mode == "foot":
		var move: Vector2 = command.move
		sample = [move.x, move.y, command.aim_yaw]
	else:
		sample = [command.throttle, command.steer, command.brake]
	_print_event({
		"event": "authority_input", "mode": host_mode, "revision": control_revision,
		"sequence": processed_input_sequence, "input_tick": processed_input_tick,
		"queue_size": input_queue.size(), "superseded": int(frame.get("superseded_count", 0)),
		"receipt_age_ms": receipt_age_ms, "expired": expired, "sample": sample,
		"time_ms": Time.get_ticks_msec(),
	})


## Resets queue and watermarks exactly at a host-owned control-revision fence.
func _reset_input_binding() -> void:
	input_queue.clear()
	processed_input_sequence = 0
	processed_input_tick = 0
	input_receipt_ms = 0
	current_held_command = _neutral_for_host_mode()
	_input_was_expired = false
	control_reset_count += 1


## Refills and consumes one named monotonic token bucket.
func take_rate_token(
	name: String, now_ms: int, rate_per_second: float, burst: float
) -> bool:
	var bucket: Dictionary = rate_buckets.get(name, { "tokens": burst, "time_ms": now_ms })
	var elapsed_ms: int = maxi(0, now_ms - int(bucket.time_ms))
	bucket.tokens = minf(burst, float(bucket.tokens) + elapsed_ms * rate_per_second / 1000.0)
	bucket.time_ms = now_ms
	if float(bucket.tokens) < 1.0:
		rate_buckets[name] = bucket
		return false
	bucket.tokens = float(bucket.tokens) - 1.0
	rate_buckets[name] = bucket
	return true


## Checks the actual Variant serialization extent before any boundary mutation.
func _serialized_within(value: Variant, limit: int) -> bool:
	return limit > 0 and var_to_bytes(value).size() <= limit


## Counts one named rejection without retaining unbounded attacker-controlled values.
func _record_rejection(target: Dictionary, reason: String) -> void:
	target[reason] = int(target.get(reason, 0)) + 1


## Queues one exact bounded reliable action using identity from the RPC sender.
@rpc("any_peer", "call_remote", "reliable", 0)
func _request_action(envelope: Variant) -> void:
	if role != "host":
		return

	var sender: int = multiplayer.get_remote_sender_id()
	var result: String = admit_action_envelope(sender, envelope, Time.get_ticks_msec())
	if result == "CACHED":
		_action_result.rpc_id(sender, action_results[int(envelope.action_sequence)])
	elif result not in ["QUEUED", "DUPLICATE_QUEUED"]:
		_record_rejection(action_rejections, result)


## Validates rate, sequence, deduplication, and queue bounds before action admission.
func admit_action_envelope(  # gdstyle:ignore=quality/max-returns,quality/max-branches
	sender: int, envelope: Variant, now_ms: int
) -> String:
	if sender != peer_id or not hydrated_peers.has(sender):
		return "NOT_ADMITTED"
	if not _action_envelope_valid(envelope) \
			or not _serialized_within(envelope, ACTION_MESSAGE_BYTES):
		return "INVALID"
	var data: Dictionary = envelope
	var sequence: int = data.action_sequence
	if action_results.has(sequence):
		return "CACHED"
	if _action_queued(sequence):
		return "DUPLICATE_QUEUED"
	if data.context.control != control_revision:
		return "STALE_CONTEXT"
	if not take_rate_token(
			"action", now_ms, ACTION_RATE_PER_SECOND, ACTION_RATE_BURST
	):
		return "RATE_LIMIT"
	if sequence <= action_highest_sequence:
		return "STALE_SEQUENCE"
	if sequence > action_highest_sequence + ACTION_SEQUENCE_WINDOW:
		return "WINDOW"
	if action_queue.size() >= ACTION_QUEUE_LIMIT:
		return "QUEUE_FULL"

	action_highest_sequence = sequence
	action_queue.append({
		"participant": sender, "sequence": sequence, "kind": data.kind,
		"vehicle": str(data.payload.get("vehicle", "")), "accepted_tick": host_tick,
	})
	action_queue_peak = maxi(action_queue_peak, action_queue.size())
	return "QUEUED"


## Requires exact context, payload, sequence, and kind fields for reliable actions.
func _action_envelope_valid(  # gdstyle:ignore=quality/max-returns
	envelope: Variant
) -> bool:
	if not envelope is Dictionary or envelope.size() != 4:
		return false
	if not envelope.get("context") is Dictionary or envelope.context.size() != 1 \
			or not envelope.context.get("control") is int or envelope.context.control <= 0:
		return false
	if not envelope.get("action_sequence") is int or envelope.action_sequence <= 0:
		return false
	if not envelope.get("kind") is String or envelope.kind not in ["enter", "exit"]:
		return false
	if not envelope.get("payload") is Dictionary:
		return false
	if envelope.kind == "exit":
		return envelope.payload.is_empty()
	return envelope.payload.size() == 1 and envelope.payload.get("vehicle") is String \
		and envelope.payload.vehicle in ["parked", "traffic"]


## Reports whether one admitted sequence already waits in the bounded queue.
func _action_queued(sequence: int) -> bool:
	for action: Dictionary in action_queue:
		if action.sequence == sequence:
			return true
	return false


## Removes at most the reviewed per-participant action work for one host tick.
func take_action_batch() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	while not action_queue.is_empty() and result.size() < ACTIONS_PER_TICK:
		result.append(action_queue.pop_front())
	action_processed_peak = maxi(action_processed_peak, result.size())
	return result


## Identifies the first parked-car request that triggers the scripted competing claimant.
func _is_parked_enter(action: Dictionary) -> bool:
	return action.kind == "enter" and action.vehicle == "parked"


## Applies same-tick claims in deterministic participant/sequence order on authority.
func _process_actions() -> void:
	if action_queue.is_empty():
		return

	var actions: Array[Dictionary] = take_action_batch()
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
			_reset_input_binding()
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
		_reset_input_binding()

	_send_action_result(action.sequence, failure, host_vehicle)


## Caches and returns one bounded reliable transition after authoritative processing.
func _send_action_result(sequence: int, failure: String, vehicle: String) -> void:
	var message: Dictionary = {
		"sequence": sequence, "failure": failure, "vehicle": vehicle,
		"revision": control_revision, "snapshot": _snapshot_state(),
	}
	cache_action_result(sequence, message)
	_action_result.rpc_id(peer_id, message)


## Retains only the newest reviewed number of idempotent action results.
func cache_action_result(sequence: int, message: Dictionary) -> void:
	if action_results.has(sequence):
		return
	action_results[sequence] = message.duplicate(true)
	action_result_order.append(sequence)
	if action_result_order.size() > ACTION_RESULT_CACHE:
		action_results.erase(action_result_order.pop_front())


## Applies one validated host transition and records its visual discontinuity.
@rpc("authority", "call_remote", "reliable", 0)
func _action_result(  # gdstyle:ignore=quality/max-function-length,quality/max-local-variables
	message: Variant
) -> void:
	if role != "client" or not pending_action or not _transition_message_valid(message):
		return

	var transition: Dictionary = message
	var sequence: int = transition.sequence
	if sequence != action_sequence:
		return
	var failure: String = transition.failure
	var vehicle: String = transition.vehicle
	var revision: int = transition.revision
	var snapshot: Dictionary = transition.snapshot
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
	elif requested_stage in ["moving_exit", "forced_blocked_exit"]:
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


## Validates the exact reliable transition shape before client state installation.
func _transition_message_valid(message: Variant) -> bool:
	if not message is Dictionary or message.size() != 5 \
			or not _serialized_within(message, ACTION_MESSAGE_BYTES):
		return false
	if not message.get("sequence") is int or message.sequence <= 0:
		return false
	if not message.get("failure") is String or message.failure not in [
		"", "SEAT_OCCUPIED", "INVALID_VEHICLE", "EXIT_MOVING", "EXIT_BLOCKED",
		"NOT_SEATED",
	]:
		return false
	if not message.get("vehicle") is String \
			or message.vehicle not in ["", "parked", "traffic"]:
		return false
	if not message.get("revision") is int or message.revision <= 0:
		return false
	return _snapshot_valid(message.get("snapshot")) \
		and message.revision == message.snapshot.control


## Buffers one validated authority snapshot and updates only permitted simulation domains.
@rpc("authority", "call_remote", "unreliable_ordered", 1)
func _snapshot(snapshot: Variant) -> void:
	if role != "client" or not active or not _snapshot_valid(snapshot):
		return

	var state: Dictionary = snapshot
	latest_snapshot = state.duplicate(true)
	if not (local_mode == "car" and local_vehicle == "parked"):
		_install_passive_car(parked_car, state.parked)
	if not (local_mode == "car" and local_vehicle == "traffic"):
		_install_passive_car(traffic_car, state.traffic)
	if pending_action and state.mode != local_mode:
		return

	if local_mode == "foot" and state.mode == "foot":
		_reconcile_foot(state)
	elif local_mode == "car" and state.mode == "car" and state.vehicle == local_vehicle:
		_reconcile_car(state)


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


## Validates an exact bounded snapshot and all finite primitive pose values.
func _snapshot_valid(snapshot: Variant) -> bool:  # gdstyle:ignore=quality/max-returns
	if not snapshot is Dictionary or snapshot.size() != 10 \
			or not _serialized_within(snapshot, SNAPSHOT_MESSAGE_BYTES):
		return false
	for field: String in ["tick", "seat_claimant", "control", "ack"]:
		if not snapshot.get(field) is int or snapshot[field] < 0:
			return false
	if snapshot.control <= 0 or not snapshot.get("traffic_ai") is bool:
		return false
	if not snapshot.get("mode") is String or snapshot.mode not in ["none", "foot", "car"]:
		return false
	if not snapshot.get("vehicle") is String \
			or snapshot.vehicle not in ["", "parked", "traffic"]:
		return false
	if snapshot.mode == "car" and snapshot.vehicle.is_empty():
		return false
	if snapshot.mode != "car" and not snapshot.vehicle.is_empty():
		return false
	return _wire_pose_valid(snapshot.get("foot"), false) \
		and _wire_pose_valid(snapshot.get("parked"), true) \
		and _wire_pose_valid(snapshot.get("traffic"), true)


## Validates one exact finite foot or car pose without accepting engine objects.
func _wire_pose_valid(  # gdstyle:ignore=quality/max-returns
	pose: Variant, car: bool
) -> bool:
	var expected_size: int = 5 if car else 4
	if not pose is Dictionary or pose.size() != expected_size:
		return false
	if not pose.get("sequence") is int or pose.sequence < 0:
		return false
	if car and (not pose.get("input_tick") is int or pose.input_tick < 0):
		return false
	if not pose.get("yaw") is float or not is_finite(pose.yaw) or absf(pose.yaw) > PI:
		return false
	return _wire_vector_valid(pose.get("position")) \
		and _wire_vector_valid(pose.get("velocity"))


## Validates one primitive finite wire vector within the fixture coordinate bound.
func _wire_vector_valid(values: Variant) -> bool:
	if not values is Array or values.size() != 3:
		return false
	for value: Variant in values:
		if not (value is int or value is float) or not is_finite(float(value)) \
				or absf(float(value)) > MAX_POSITION_M:
			return false
	return true


## Produces the complete bounded authoritative state used by transitions and snapshots.
func _snapshot_state() -> Dictionary:
	return {
		"tick": host_tick,
		"mode": host_mode,
		"vehicle": host_vehicle if host_mode == "car" else "",
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
	_request_action.rpc_id(1, {
		"context": { "control": control_revision }, "action_sequence": action_sequence,
		"kind": "enter", "payload": { "vehicle": vehicle },
	})


## Requests exit without pre-empting moving/clearance authority.
func _request_exit(next_stage: String) -> void:
	if pending_action:
		return

	action_sequence += 1
	pending_action = true
	stage = next_stage
	transition_request_ms = Time.get_ticks_msec()
	first_control_ms = 0
	_request_action.rpc_id(1, {
		"context": { "control": control_revision }, "action_sequence": action_sequence,
		"kind": "exit", "payload": {},
	})


## Switches collision, replay, camera, and HUD ownership to one predicted car.
func _switch_to_car(vehicle: String, snapshot: Dictionary, reason: String) -> void:
	foot_history.clear()
	car_history.clear()
	_reset_local_input_binding()
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
	_reset_local_input_binding()
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


## Clears local packet numbering when host authority creates a control revision.
func _reset_local_input_binding() -> void:
	local_input_sequence = 0
	local_recent_frames.clear()


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
		_request_exit("forced_blocked_exit")
	elif stage == "wait_successful_exit" and input_tick - stage_tick >= 8:
		_request_exit("successful_exit")
	elif stage == "wait_traffic_entry" and input_tick - stage_tick >= 20:
		_predict_enter("traffic", "traffic_entry")
	elif stage == "drive_traffic" and (
			input_tick - stage_tick >= DRIVE_BEFORE_DISCONNECT_TICKS
			and int(latest_snapshot.get("tick", 0)) >= ADVERSE_FINISH_TICK
	):
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
	elif previous_stage == "forced_blocked_exit" and failure == "EXIT_BLOCKED":
		stage = "wait_successful_exit"
	elif previous_stage == "successful_exit" and accepted:
		stage = "wait_traffic_entry"
	elif previous_stage == "traffic_entry" and accepted:
		stage = "drive_traffic"
	else:
		_fail("unexpected action result at %s: %s" % [previous_stage, failure])


## Chooses varying bounded foot input without any seated firing path.
func _foot_command() -> Dictionary:
	var phase: float = float(input_tick % 12) / 12.0
	return {
		"move": Vector2(0.1 + phase * 0.12, -0.05 - phase * 0.06),
		"aim_yaw": -0.2 + phase * 0.4,
		"fire": false,
	}


## Selects varying acceleration/steering or explicit braking for the local car stage.
func _client_drive_command() -> Dictionary:
	if stage in ["brake_parked", "forced_blocked_exit", "wait_successful_exit"]:
		return _drive_command(0.0, 0.0, 1.0)
	var phase: float = float(input_tick % 30) / 29.0
	return _drive_command(0.65 + phase * 0.25, -0.15 + phase * 0.3, 0.0)


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
		"forced_blocked_exit",
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
	input_queue.clear()
	current_held_command = S04DriveRules.neutral()
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
		and input_queue_peak <= S03InputFrameQueue.DEFAULT_CAPACITY
		and action_queue_peak <= ACTION_QUEUE_LIMIT
		and action_processed_peak <= ACTIONS_PER_TICK
		and action_results.size() <= ACTION_RESULT_CACHE
		and control_reset_count >= 3
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
			"input_queue_peak": input_queue_peak,
			"input_superseded_count": input_superseded_count,
			"input_expiry_count": input_expiry_count,
			"input_rejections": input_rejections,
			"action_queue_peak": action_queue_peak,
			"action_processed_peak": action_processed_peak,
			"action_cache_size": action_results.size(),
			"action_rejections": action_rejections,
			"control_reset_count": control_reset_count,
			"hydration_count": hydrated_peers.size(),
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
