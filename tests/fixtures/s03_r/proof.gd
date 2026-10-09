class_name S03RProof  # gdstyle:ignore=quality/max-class-variables
extends Node
## Explicit fixture bookkeeping keeps timing, receipts and cleanup in one experiment owner.
## Drives one bounded actual-controller experiment through the existing S03 session APIs.

const INPUT_PHYSICS_PRIORITY: int = -20
const HOST_REVERSE_START_TICK: int = 120
const HOST_REVERSE_END_TICK: int = 180
const STALL_REVERSE_START_TICK: int = 888
const STALL_REVERSE_END_TICK: int = 930
const BOUNDARY_CHECK_TICK: int = 950
const EXPIRY_PULSE_START_TICK: int = 990
const PRODUCER_SILENCE_START_TICK: int = 1002
const PRODUCER_SILENCE_END_TICK: int = 1040
const RESPONSE_DISTANCE_M: float = 0.005
const RESPONSE_TURN_DEG: float = 0.2
const INPUT_INTERVAL_TICKS: int = 2
const SNAPSHOT_INTERVAL_TICKS: int = 3
const PULSE_COUNT: int = 20
const PULSE_TICKS: int = 30
const HOLD_TICKS: int = 12
const END_TICK: int = 1320
const STALL_TICK: int = 900
const STALL_MS: int = 250
const WALL_START_TICK: int = 600
const WALL_END_TICK: int = 720
const REVERSE_END_TICK: int = 768
const RESYNC_TICK: int = 1080
const CAPTURE_EVENTS: int = 4

var role: String = "host"
var port: int = 24_900
var profile: String = "baseline"
var requested_max_fps: int = 0
var requested_low_processor_mode: bool = false
var local_tick: int = 0
var started_ms: int = -1
var sequence: int = 0
var control: int = 1
var recent_input_frames: Array[Dictionary] = []
var resync_sent: bool = false
var last_command: Vector2 = Vector2.ZERO
var event_index: int = 0
var capture_pending: bool = false
var capture_pose: Dictionary = {}
var failures: Array[String] = []
var ending: bool = false

@onready var session: S03Session = $Session
@onready var match_state: S03RMatch = $View/Match
@onready var replication: S03RReplication = $View/Match/Replication
@onready var input_collector: S02DesktopInput = $Input
@onready var camera_rig: S02CameraRig = $CameraRig
@onready var status: Label = get_node("UI/Status")


## Injects existing boundaries before starting the ordinary host/join lifecycle.
func _ready() -> void:
	process_physics_priority = INPUT_PHYSICS_PRIORITY
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--role="):
			role = argument.trim_prefix("--role=")
		elif argument.begins_with("--port="):
			port = int(argument.trim_prefix("--port="))
		elif argument.begins_with("--profile="):
			profile = argument.trim_prefix("--profile=")
		elif argument.begins_with("--max-fps="):
			requested_max_fps = int(argument.trim_prefix("--max-fps="))
		elif argument == "--low-processor-mode":
			requested_low_processor_mode = true

	Engine.max_fps = requested_max_fps
	OS.low_processor_usage_mode = requested_low_processor_mode
	session.match_state = match_state
	session.replication = replication
	replication.match_state = match_state
	replication.resolve_participant = session.participant_for_peer
	replication.handoff_confirmed.connect(session.confirm_handoff)
	replication.admission_received.connect(session.receive_admission)
	match_state.stepped.connect(_on_step)
	match_state.reconciled.connect(_on_reconciled)
	match_state.held_received.connect(_on_held_received)
	match_state.movement_buffered.connect(_on_movement_buffered)
	input_collector.set_focused(true)
	RenderingServer.frame_post_draw.connect(_on_rendered)
	session.select_provider(S03Transport.new(get_tree()))
	if role == "host":
		session.host(port)
		_record({ "event": "ready", "port": port, "pid": OS.get_process_id() })
	else:
		session.join(session.provider.parse_endpoint("127.0.0.1", port))


## Samples synthetic bound keys and sends replaceable intent at the proposed 30 Hz.
func _physics_process(delta: float) -> void:  # gdstyle:ignore=quality/max-branches
	if ending:
		return
	if started_ms < 0:
		if role == "client" and session.phase == "ACTIVE" and (
			match_state.rig != null and match_state.rig.get_meta("input_enabled", false)):
			_start()
			_announce.rpc_id(1, session.session_id)
		return

	if session.phase == "IDLE":
		_finish()
		return

	local_tick += 1
	if role == "host" and profile == "adverse" and local_tick == STALL_TICK:
		_record({ "event": "stall_begin", "tick": local_tick })
		OS.delay_msec(STALL_MS)
		_record({ "event": "stall_end", "tick": local_tick })

	if role == "host" and local_tick == WALL_START_TICK:
		_prepare_wall()

	if role == "client" and local_tick == RESYNC_TICK and not resync_sent:
		resync_sent = true
		_record({"event": "resync_request", "entity": match_state.bindings[
			session.local_participant].entity, "health": match_state.bindings[
			session.local_participant].health})
		session.request_resync()

	if session.phase != "ACTIVE" or match_state.rig == null:
		input_collector.clear()
		return

	_collect_and_send(delta)

	if local_tick >= END_TICK and role == "host":
		ending = true
		session.leave()
		_end_after_cleanup()


## Predicts each fixed input and sends replaceable samples through the common validator.
func _collect_and_send(delta: float) -> void:
	var binding: Dictionary = match_state.bindings[session.local_participant]
	if binding.control != control:
		control = binding.control
		sequence = 0
		recent_input_frames.clear()
		_record({"event": "resync_applied", "control": control, "entity": binding.entity,
			"health": binding.health})

	if local_tick == BOUNDARY_CHECK_TICK:
		_check_boundaries()

	var command: Vector2 = _command(local_tick)
	_set_keys(command)
	var sampled: Dictionary = input_collector.sample()
	var motion_command: Dictionary = {
		"move": sampled.move, "aim_yaw": _aim_yaw(command), "fire": false,
	}
	sequence += 1
	var input_frame: Dictionary = {
		"sequence": sequence,
		"input_tick": local_tick,
		"move": sampled.move,
		"aim_yaw": motion_command.aim_yaw,
	}
	recent_input_frames.append(input_frame)
	if recent_input_frames.size() > 4:
		recent_input_frames.pop_front()
	if role == "client":
		match_state.queue_local_prediction(local_tick, motion_command, delta)
	if local_tick % INPUT_INTERVAL_TICKS != 0:
		return

	# A bounded loss-of-producer segment tests expiry independently of proxy randomness.
	if role == "client" and local_tick >= PRODUCER_SILENCE_START_TICK and (
		local_tick < PRODUCER_SILENCE_END_TICK):
		return
	var sample_ticks_ms: int = Time.get_ticks_msec()
	var sample_wall_ms: float = Time.get_unix_time_from_system() * 1000.0
	var envelope: Dictionary = {
		"context": match_state.context(session.local_participant),
		"frames": recent_input_frames.duplicate(true),
	}
	if role == "host":
		match_state.submit_held(session.local_participant, envelope)
	else:
		replication.send_held(envelope)
	if role == "client" and event_index <= PULSE_COUNT and sampled.move != Vector2.ZERO:
		_record({"event": "input_send", "index": event_index, "sequence": sequence,
			"move": [sampled.move.x, sampled.move.y], "aim_yaw": motion_command.aim_yaw,
			"sample_ticks_ms": sample_ticks_ms, "sample_wall_ms": sample_wall_ms,
			"send_ticks_ms": Time.get_ticks_msec(),
			"send_wall_ms": Time.get_unix_time_from_system() * 1000.0})


## Checks admission/identity/value fences and local focus cancellation through existing owners.
func _check_boundaries() -> void:
	if role == "client":
		var key: InputEventKey = InputEventKey.new()
		key.physical_keycode = KEY_W
		key.pressed = true
		input_collector._unhandled_input(key)
		input_collector.set_focused(false)
		if input_collector.sample().move != Vector2.ZERO:
			failures.append("focus API did not neutralize held motion")
		input_collector.set_focused(true)
		if input_collector.sample().move != Vector2.ZERO:
			failures.append("focus regain resumed held input")
		_record({ "event": "focus_api",
			"neutral": input_collector.sample().move == Vector2.ZERO })
		return

	var participant: int = session.local_participant
	var binding: Dictionary = match_state.bindings[participant]
	var before: int = binding.pending
	var frame: Dictionary = {"sequence": sequence + 1, "input_tick": local_tick,
		"move": Vector2(NAN, 0.0), "aim_yaw": 0.0}
	var envelope: Dictionary = {
		"context": match_state.context(participant), "frames": [frame],
	}
	var reasons: Array[String] = [match_state.submit_held(participant, envelope)]
	frame.move = Vector2.ZERO
	envelope.frames = [frame]
	envelope.context.entity = 2
	reasons.append(match_state.submit_held(participant, envelope))
	envelope.context = match_state.context(participant)
	frame.sequence = binding.sequence + S03Match.SEQUENCE_WINDOW + 1
	envelope.frames = [frame]
	reasons.append(match_state.submit_held(participant, envelope))
	reasons.append(match_state.submit_held(0, envelope))
	if reasons != ["INVALID", "STALE_CONTEXT", "WINDOW", "NOT_ADMITTED"] or (
		binding.pending != before):
		failures.append("input boundary changed pending state")
	_record({"event": "boundary_checks", "reasons": reasons,
		"unchanged_pending": binding.pending == before})


## Starts measurement only after the admitted dependent state has enabled local control.
func _start() -> void:
	started_ms = Time.get_ticks_msec()
	camera_rig.bind(match_state.local_body())
	input_collector.bind_aim(camera_rig.camera(), match_state.local_body())
	_record({"event": "start", "pid": OS.get_process_id(), "profile": profile,
		"window_visible": get_window().visible, "window_mode": get_window().mode,
		"can_draw": DisplayServer.window_can_draw(), "display": DisplayServer.get_name(),
		"user_dir": OS.get_user_data_dir(), "engine": Engine.get_version_info().string,
		"renderer": RenderingServer.get_current_rendering_method(),
		"max_fps": Engine.max_fps, "low_processor_mode": OS.low_processor_usage_mode,
		"vsync_mode": DisplayServer.window_get_vsync_mode()})


## Admits the fixture's measurement handshake only from an admitted mapped sender.
@rpc("any_peer", "call_remote", "reliable", 0)
func _announce(session_id: String) -> void:
	if role != "host" or session_id != session.session_id:
		return

	var participant: int = session.participant_for_peer(multiplayer.get_remote_sender_id())
	if participant > 0 and match_state.bindings[participant].admitted and started_ms < 0:
		_start()


## Records accepted client input immediately inside the authoritative RPC call chain.
func _on_held_received(participant: int, received_sequence: int, receipt_ms: int) -> void:
	if role != "host" or participant == session.local_participant or local_tick >= WALL_START_TICK:
		return

	_record({"event": "host_receive", "participant": participant,
		"sequence": received_sequence, "receipt_ms": receipt_ms})


## Records movement arrival before the replica's next physics installation.
func _on_movement_buffered(rows: Array) -> void:
	if role != "client" or local_tick >= WALL_START_TICK:
		return

	_record({ "event": "state_receive", "rows": rows })


## Provides independently timed motion/turn pulses followed by collision and recovery cases.
func _command(tick: int) -> Vector2:  # gdstyle:ignore=quality/max-returns
	if role == "host":
		return Vector2(0.0, 1.0) if (
			tick >= HOST_REVERSE_START_TICK and tick < HOST_REVERSE_END_TICK) else Vector2.ZERO

	if tick < WALL_START_TICK:
		var pulse: int = tick / PULSE_TICKS
		if pulse < PULSE_COUNT and tick % PULSE_TICKS < HOLD_TICKS:
			if pulse % 2 == 0:
				return Vector2(0.0, -1.0)
			return Vector2(1.0 if pulse % 4 == 1 else -1.0, 0.0)
		return Vector2.ZERO

	if tick < WALL_END_TICK:
		return Vector2(0.0, -1.0)
	if tick < REVERSE_END_TICK:
		return Vector2(0.0, 1.0)
	if (tick >= STALL_REVERSE_START_TICK and tick < STALL_REVERSE_END_TICK) or (
		tick >= EXPIRY_PULSE_START_TICK and tick < PRODUCER_SILENCE_START_TICK):
		return Vector2(0.0, 1.0)

	return Vector2.ZERO


## Faces synthetic route movement so the envelope exercises independent aim yaw.
func _aim_yaw(move: Vector2) -> float:
	return 0.0 if move == Vector2.ZERO else atan2(-move.x, -move.y)


## Routes synthetic physical binding transitions through the accepted S02 input owner.
func _set_keys(command: Vector2) -> void:
	if command == last_command:
		return

	var previous: Vector2 = last_command
	# Synthetic events are bounded to four bindings per command edge, outside simulation.
	for key: Key in [KEY_W, KEY_S, KEY_A, KEY_D]:
		var event: InputEventKey = InputEventKey.new()  # gdstyle:ignore=quality/allocation-in-loop
		event.physical_keycode = key
		event.pressed = (
			(key == KEY_W and command.y < 0.0) or (key == KEY_S and command.y > 0.0)
			or (key == KEY_D and command.x > 0.0) or (key == KEY_A and command.x < 0.0))
		input_collector._unhandled_input(event)

	last_command = command
	if command != Vector2.ZERO and previous == Vector2.ZERO:
		event_index += 1
		if event_index <= CAPTURE_EVENTS:
			_capture("before")
			capture_pending = true

		var actor: S03RActor = match_state.local_body()
		capture_pose = actor.motion_state()
		_record({"event": "input", "index": event_index, "tick": local_tick,
			"move": [command.x, command.y], "aim_yaw": _aim_yaw(command),
			"sequence_floor": sequence + 1, "position": match_state.vector(
				actor.global_position), "yaw": actor.rotation.y})

	_record({ "event": "keys", "tick": local_tick,
		"move": [command.x, command.y], "aim_yaw": _aim_yaw(command) })


## Places only a dynamic authoritative test body for the isolated wall-outcome segment.
func _prepare_wall() -> void:
	for participant: int in match_state.bindings:
		if participant == session.local_participant:
			continue

		var actor: S03RActor = match_state.body_for_entity[
			match_state.bindings[participant].entity]
		actor.global_position = Vector3(6.0, 0.001, 6.0)
		actor.rotation.y = 0.0
		actor.neutralize()
		_record({ "event": "wall_setup", "entity": match_state.bindings[participant].entity })


## Records post-simulation state/acknowledgement and refreshes both entities at 20 Hz.
func _on_step(tick: int) -> void:
	if started_ms < 0 or match_state.bindings.is_empty():
		return

	if role == "host":
		for entity: int in match_state.body_for_entity:
			var participant: int = match_state.participant_for_entity(entity)
			var binding: Dictionary = match_state.bindings[participant]
			var actor: S03RActor = match_state.body_for_entity[entity]
			_record({"event": "simulation", "local_tick": local_tick,
				"pose": match_state.pose_for_entity(entity),
				"held": [binding.held.move.x, binding.held.move.y],
				"aim_yaw": binding.held.aim_yaw, "receipt_ms": binding.receipt_ms,
				"held_age_ms": binding.held_age_ms,
				"decision_age_ms": match_state.expiry_decision_ages.get(entity, -1),
				"pending_input_frames": match_state.input_queues[participant].size(),
				"superseded_input_frames": binding.superseded_count,
				"muzzle": match_state.vector(actor.muzzle_position()),
				"aim": match_state.vector(-actor.global_basis.z)})

		if tick % SNAPSHOT_INTERVAL_TICKS == 0:
			_send_snapshot(tick)
	else:
		var actor: S03RActor = match_state.local_body()
		_record({
			"event": "prediction",
			"tick": local_tick,
			"predicted_tick": actor.latest_predicted_tick,
			"position": match_state.vector(actor.global_position),
			"yaw": actor.rotation.y,
			"history_size": match_state.prediction_history.size(),
		})

	status.text = "S03-R %s | %s | tick %d | local prediction" % [
		role, profile, local_tick]


## Sends one instrumented movement snapshot to every admitted peer.
func _send_snapshot(tick: int) -> void:
	var rows: Array = []
	for entity: int in match_state.body_for_entity:
		var pose: Dictionary = match_state.pose_for_entity(entity)
		rows.append({ "entity": entity, "sequence": pose.sequence, "tick": pose.tick })

	for peer_id: int in session.roster:
		if session.roster[peer_id].phase != "ADMITTED":
			continue

		var send_wall_ms: float = Time.get_unix_time_from_system() * 1000.0
		replication.send_movement(peer_id, match_state.bindings.keys(), tick, 0.0)
		if local_tick < WALL_START_TICK:
			_record({ "event": "state_send", "peer": peer_id, "rows": rows,
				"send_wall_ms": send_wall_ms })


## Retains correction, bounded replay cost and observable mismatch cause telemetry.
func _on_reconciled(details: Dictionary) -> void:
	details["event"] = "correction"
	details["tick"] = local_tick
	_record(details)


## Receipts actual drawn frames independently of simulation and keeps matched camera captures.
func _on_rendered() -> void:
	if started_ms < 0 or ending or match_state.body_for_entity.is_empty():
		return

	var actor: S03RActor = match_state.local_body()
	var state: Dictionary = actor.display_state()
	var screen: Vector2 = camera_rig.camera().unproject_position(state.position + Vector3.UP)
	_record({"event": "render", "index": event_index, "tick": local_tick,
		"position": match_state.vector(state.position), "yaw": state.yaw,
		"sequence": actor.latest_sequence, "predicted_tick": actor.latest_predicted_tick,
		"screen": [screen.x, screen.y], "viewport": get_viewport().get_visible_rect().size})
	if capture_pending and (
		(state.position as Vector3).distance_to(capture_pose.position) > RESPONSE_DISTANCE_M
		or absf(angle_difference(state.yaw, capture_pose.yaw)) > deg_to_rad(RESPONSE_TURN_DEG)
	):
		_capture("after")
		capture_pending = false


## Retains early matched viewport frames; raw render telemetry covers every response event.
func _capture(suffix: String) -> void:
	var directory: String = OS.get_environment("S03R_CAPTURE_DIR")
	if directory.is_empty() or DisplayServer.get_name() == "headless":
		return

	var image: Image = get_viewport().get_texture().get_image()
	image.save_png(directory.path_join("%s-%02d-%s.png" % [role, event_index, suffix]))


## Waits for ordinary asynchronous host cleanup before emitting the bounded result.
func _end_after_cleanup() -> void:
	await get_tree().create_timer(S03Transport.CLOSE_DELAY_S * 2.0).timeout
	_finish()


## Requires actual lifecycle cleanup and publishes structured process disposition.
func _finish() -> void:
	ending = true
	if session.phase != "IDLE" or not match_state.bindings.is_empty() or (
		not match_state.entities.is_empty() or not match_state.pending_poses.is_empty()):
		failures.append("lifecycle cleanup incomplete")

	for actor: S03RActor in match_state.bodies:
		if actor.visible or actor.velocity != Vector3.ZERO or not actor.samples.is_empty():
			failures.append("body not retired")

	_record({"event": "result", "ok": failures.is_empty(), "failures": failures,
		"reason": session.close_outcome, "max_held_bytes": replication.max_held_bytes,
		"max_movement_bytes": replication.max_movement_bytes,
		"accepted": match_state.accepted_count, "rejected": match_state.rejected})
	get_tree().quit(0 if failures.is_empty() else 1)


## Emits bounded structured telemetry; wall-clock timestamps do not control gameplay steps.
func _record(record: Dictionary) -> void:
	record["time_ms"] = Time.get_ticks_msec()
	record["wall_ms"] = Time.get_unix_time_from_system() * 1000.0
	record["role"] = role
	print("S03R " + JSON.stringify(record))
