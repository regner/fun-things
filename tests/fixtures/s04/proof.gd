class_name S04Proof  # gdstyle:ignore=quality/max-class-variables
extends Node
## Explicit fixture bookkeeping keeps timing, receipts and cleanup in one experiment owner.
## Drives one bounded vehicle-controller experiment through the existing S03 session APIs.

const INPUT_PHYSICS_PRIORITY: int = -20
const HOST_REVERSE_START_TICK: int = 120
const HOST_REVERSE_END_TICK: int = 180
const STALL_REVERSE_START_TICK: int = 888
const STALL_REVERSE_END_TICK: int = 906
const EXIT_REQUEST_TICK: int = 100
const BOUNDARY_CHECK_TICK: int = 950
const EXPIRY_PULSE_START_TICK: int = 1000
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
const REVERSE_END_TICK: int = 750
const RESYNC_TICK: int = 1080
const CAPTURE_EVENTS: int = 4
const SCENARIO_MEASUREMENT: String = "measurement"
const SCENARIO_EXIT: String = "stopped-exit"
const SCENARIO_DISCONNECT: String = "abrupt-disconnect"

var role: String = "host"
var port: int = 24_900
var profile: String = "baseline"
var scenario: String = SCENARIO_MEASUREMENT
var local_tick: int = 0
var started_ms: int = -1
var sequence: int = 0
var control: int = 1
var resync_sent: bool = false
var last_command: Vector2 = Vector2.ZERO
var event_index: int = 0
var capture_pending: bool = false
var capture_pose: Dictionary = {}
var failures: Array[String] = []
var ending: bool = false
var exit_verdict: String = ""
var exit_requested: bool = false
var lifecycle_stage: int = 0
var scenario_finished: bool = false
var coast_start: Vector3 = Vector3.ZERO
var coast_entity: int = 0
var coasting_snapshots: int = 0

@onready var session: S03Session = $Session
@onready var match_state: S04Match = $View/Match
@onready var replication: S04Replication = $View/Match/Replication
@onready var input_collector: S04DesktopInput = $Input
@onready var camera_rig: S04CameraRig = $CameraRig
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
		elif argument.begins_with("--scenario="):
			scenario = argument.trim_prefix("--scenario=")

	session.match_state = match_state
	session.replication = replication
	replication.match_state = match_state
	replication.resolve_participant = session.participant_for_peer
	replication.handoff_confirmed.connect(session.confirm_handoff)
	replication.admission_received.connect(session.receive_admission)
	match_state.stepped.connect(_on_step)
	match_state.predicted.connect(_on_predicted)
	match_state.reconciled.connect(_on_reconciled)
	replication.exit_result.connect(_on_exit_result)
	input_collector.set_focused(true)
	RenderingServer.frame_post_draw.connect(_on_rendered)
	session.select_provider(S03Transport.new(get_tree()))
	if role == "host":
		session.host(port)
		_record({ "event": "ready", "port": port, "pid": OS.get_process_id() })
	else:
		session.join(session.provider.parse_endpoint("127.0.0.1", port))


## Samples synthetic bound keys and sends replaceable intent at the proposed 30 Hz.
func _physics_process(_delta: float) -> void:  # gdstyle:ignore=quality/max-branches
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
	if scenario != SCENARIO_MEASUREMENT:
		_lifecycle_process()
		return

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

	if session.phase != "ACTIVE" or match_state.rig == null or (
		not match_state.rig.get_meta("input_enabled", false)):
		# A reliable grant may precede fresh movement after resync; do not collect/send yet.
		input_collector.clear()
		return

	_collect_and_send()

	if local_tick >= END_TICK and role == "host":
		ending = true
		session.leave()
		_end_after_cleanup()


## Runs a bounded two-process exit or abrupt-disconnect lifecycle scenario.
func _lifecycle_process() -> void:  # gdstyle:ignore=quality/max-branches
	if role == "host":
		_observe_lifecycle_host()
		return

	if scenario == SCENARIO_DISCONNECT:
		_send_lifecycle_drive(_lifecycle_drive(false))
		if local_tick >= 60 and match_state.local_body().latest_authoritative_speed_mps >= 4.0:
			_record({"event": "scenario_result", "scenario": scenario, "ok": true,
				"speed_mps": match_state.local_body().latest_authoritative_speed_mps})
			get_tree().quit(0)
		return

	if lifecycle_stage < 2:
		_send_lifecycle_drive(_lifecycle_drive(false))
		if lifecycle_stage == 0 and local_tick >= 30 and (
			match_state.local_body().latest_authoritative_speed_mps >= 2.5):
			if replication.request_exit():
				lifecycle_stage = 1
		return

	if lifecycle_stage == 2:
		_send_lifecycle_drive(_lifecycle_drive(true))
		if match_state.local_body().latest_authoritative_speed_mps < 0.4:
			if replication.request_exit():
				lifecycle_stage = 3
		return

	if lifecycle_stage == 4 and not scenario_finished:
		var passive: bool = not match_state.prediction_enabled and (
			not match_state.seats.has(session.local_participant)) and (
			not match_state.bindings[session.local_participant].admitted) and (
			not match_state.rig.get_meta("input_enabled", true)) and (
			not match_state.local_body().simulation_enabled) and (
			match_state.prediction_ticks.is_empty())
		_scenario_result(passive, "successful exit did not install passive lifecycle")


## Sends one lifecycle command through prediction and the sender-bound host validator.
func _send_lifecycle_drive(drive: Dictionary) -> void:
	match_state.queue_local_input(local_tick, drive)
	if local_tick % INPUT_INTERVAL_TICKS != 0:
		return

	sequence += 1
	var envelope: Dictionary = {"context": match_state.context(session.local_participant),
		"sequence": sequence, "input_tick": local_tick, "move": drive}
	replication.send_held(envelope)


## Accelerates for lifecycle setup or brakes to an authoritative stopped state.
func _lifecycle_drive(braking: bool) -> Dictionary:
	var drive: Dictionary = S04DriveRules.neutral()
	if braking:
		drive.brake = 1.0
	else:
		drive.throttle = 1.0
	return drive


## Verifies host survival and rest after the remote process disappears abruptly.
func _observe_lifecycle_host() -> void:
	if session.disconnected_count == 0:
		return
	if scenario == SCENARIO_EXIT:
		_scenario_result(true, "host did not observe stopped-exit client cleanup")
		return
	if coast_entity == 0:
		for entity: int in match_state.body_for_entity:
			if match_state.participant_for_entity(entity) == 0:
				coast_entity = entity
				coast_start = match_state.body_for_entity[entity].global_position
				break
	if coast_entity == 0:
		_scenario_result(false, "disconnect did not retain an unbound car")
		return

	var actor: S04Kinematic = match_state.body_for_entity[coast_entity]
	if not match_state.coasting_bodies.has(coast_entity):
		var coasted: bool = actor.global_position.distance_to(coast_start) > 0.1
		var parked: bool = actor.velocity.length() < S04Match.PARKED_SPEED_MPS
		_scenario_result(coasted and parked and coasting_snapshots > 0,
			"unbound car did not replicate while coasting to rest")


## Emits one lifecycle outcome before terminating the isolated process.
func _scenario_result(ok: bool, failure: String) -> void:
	if scenario_finished:
		return
	scenario_finished = true
	if not ok:
		failures.append(failure)
	_record({"event": "scenario_result", "scenario": scenario,
		"ok": failures.is_empty(), "failures": failures,
		"coasting_snapshots": coasting_snapshots})
	get_tree().quit(0 if failures.is_empty() else 1)


## Applies a fresh binding then sends one sampled held envelope through the common validator.
func _collect_and_send() -> void:
	var binding: Dictionary = match_state.bindings[session.local_participant]
	if binding.control != control:
		control = binding.control
		sequence = 0
		_record({"event": "resync_applied", "control": control, "entity": binding.entity,
			"health": binding.health, "seat": match_state.seats[session.local_participant]})

	if local_tick == BOUNDARY_CHECK_TICK:
		_check_boundaries()

	var command: Vector2 = _command(local_tick)
	_set_keys(command)
	var drive: Dictionary = input_collector.drive_sample()
	# Test recovery compares a settled car, so both host and prediction apply explicit brake.
	if role == "client" and ((local_tick >= REVERSE_END_TICK and
		local_tick < STALL_REVERSE_START_TICK) or (local_tick >= STALL_REVERSE_END_TICK and
		local_tick < EXPIRY_PULSE_START_TICK)):
		drive.brake = 1.0
	if role == "client":
		match_state.queue_local_input(local_tick, drive)
		if not exit_requested and local_tick >= EXIT_REQUEST_TICK and drive.throttle > 0.0 and (
			match_state.local_body().latest_authoritative_speed_mps >= 2.5):
			exit_requested = true
			replication.request_exit()

	if local_tick % INPUT_INTERVAL_TICKS == 0:
		sequence += 1
		# A bounded loss-of-producer segment tests expiry independently of proxy randomness.
		if role == "client" and local_tick >= PRODUCER_SILENCE_START_TICK and (
			local_tick < PRODUCER_SILENCE_END_TICK):
			return
		var envelope: Dictionary = {"context": match_state.context(session.local_participant),
			"sequence": sequence, "input_tick": local_tick, "move": drive}
		if role == "host":
			match_state.submit_held(session.local_participant, envelope)
		else:
			replication.send_held(envelope)


## Checks admission/identity/value fences and local focus cancellation through existing owners.
func _check_boundaries() -> void:
	if role == "client":
		var key: InputEventKey = InputEventKey.new()
		key.physical_keycode = KEY_W
		key.pressed = true
		input_collector._unhandled_input(key)
		input_collector.set_focused(false)
		if input_collector.drive_sample().throttle != 0.0:
			failures.append("focus API did not neutralize held motion")
		input_collector.set_focused(true)
		if input_collector.drive_sample().throttle != 0.0:
			failures.append("focus regain resumed held input")
		_record({ "event": "focus_api",
			"neutral": input_collector.drive_sample().throttle == 0.0 })
		return

	var participant: int = session.local_participant
	var binding: Dictionary = match_state.bindings[participant]
	var before: int = binding.pending
	var envelope: Dictionary = {"context": match_state.context(participant),
		"sequence": sequence + 1, "input_tick": local_tick, "move": {
			"throttle": NAN,
			"steer": 0.0,
			"brake": 0.0,
			"handbrake": false,
		}}
	var reasons: Array[String] = [match_state.submit_held(participant, envelope)]
	envelope.move = S04DriveRules.neutral()
	envelope.context.entity = 2
	reasons.append(match_state.submit_held(participant, envelope))
	envelope.context = match_state.context(participant)
	envelope.sequence = binding.sequence + S03Match.SEQUENCE_WINDOW + 1
	reasons.append(match_state.submit_held(participant, envelope))
	reasons.append(match_state.submit_held(0, envelope))
	envelope.context = match_state.context(participant)
	envelope.sequence = binding.pending + 1
	envelope.input_tick = binding.pending_input_tick
	reasons.append(match_state.submit_held(participant, envelope))
	envelope.input_tick = maxi(1, int(binding.pending_input_tick) - 1)
	reasons.append(match_state.submit_held(participant, envelope))
	envelope.input_tick = S04Match.MAX_INPUT_TICK + 1
	reasons.append(match_state.submit_held(participant, envelope))
	if reasons != ["INVALID", "STALE_CONTEXT", "WINDOW", "NOT_ADMITTED",
		"STALE_INPUT_TICK", "STALE_INPUT_TICK", "INVALID"] or binding.pending != before:
		failures.append("input boundary changed pending state")
	_record({"event": "boundary_checks", "reasons": reasons,
		"unchanged_pending": binding.pending == before})


## Starts measurement only after the admitted dependent state has enabled local control.
func _start() -> void:
	started_ms = Time.get_ticks_msec()
	camera_rig.bind(match_state.local_body())
	_record({"event": "start", "pid": OS.get_process_id(), "profile": profile,
		"window_visible": get_window().visible, "window_mode": get_window().mode,
		"can_draw": DisplayServer.window_can_draw(), "display": DisplayServer.get_name(),
		"user_dir": OS.get_user_data_dir(), "engine": Engine.get_version_info().string,
		"renderer": RenderingServer.get_current_rendering_method()})


## Admits the fixture's measurement handshake only from an admitted mapped sender.
@rpc("any_peer", "call_remote", "reliable", 0)
func _announce(session_id: String) -> void:
	if role != "host" or session_id != session.session_id:
		return

	var participant: int = session.participant_for_peer(multiplayer.get_remote_sender_id())
	if participant > 0 and match_state.bindings[participant].admitted and started_ms < 0:
		_start()


## Provides independently timed motion/turn pulses followed by collision and recovery cases.
func _command(tick: int) -> Vector2:  # gdstyle:ignore=quality/max-returns
	if role == "host":
		return Vector2(-1.0, 0.0) if (
			tick >= HOST_REVERSE_START_TICK and tick < HOST_REVERSE_END_TICK) else Vector2.ZERO

	if tick < WALL_START_TICK:
		var pulse: int = tick / PULSE_TICKS
		if pulse < PULSE_COUNT and tick % PULSE_TICKS < HOLD_TICKS:
			if pulse % 2 == 0:
				return Vector2(1.0, 0.0)
			return Vector2(1.0, 1.0)
		return Vector2.ZERO

	if tick < WALL_END_TICK:
		return Vector2(1.0, 0.0)
	if tick < REVERSE_END_TICK:
		return Vector2(-1.0, 0.0)
	if (tick >= STALL_REVERSE_START_TICK and tick < STALL_REVERSE_END_TICK) or (
		tick >= EXPIRY_PULSE_START_TICK and tick < PRODUCER_SILENCE_START_TICK):
		return Vector2(-1.0, 0.0)

	return Vector2.ZERO


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
			(key == KEY_W and command.x > 0.0) or (key == KEY_S and command.x < 0.0)
			or (key == KEY_D and command.y > 0.0) or (key == KEY_A and command.y < 0.0))
		input_collector._unhandled_input(event)

	last_command = command
	if command != Vector2.ZERO and previous == Vector2.ZERO:
		event_index += 1
		if event_index <= CAPTURE_EVENTS:
			_capture("before")
			capture_pending = true

		var actor: S04Kinematic = match_state.local_body()
		capture_pose = actor.motion_state()
		_record({"event": "input", "index": event_index, "tick": local_tick,
			"move": command.x, "turn": command.y, "sequence_floor": sequence + 1,
			"input_tick_floor": local_tick,
			"position": match_state.vector(actor.global_position),
			"velocity": match_state.vector(actor.velocity), "yaw": actor.rotation.y})

	_record({ "event": "keys", "tick": local_tick, "move": command.x, "turn": command.y })


## Places only a dynamic authoritative test body for the isolated wall-outcome segment.
func _prepare_wall() -> void:
	for participant: int in match_state.bindings:
		if participant == session.local_participant:
			continue

		var actor: S04Kinematic = match_state.body_for_entity[
			match_state.bindings[participant].entity]
		actor.global_position = Vector3(0.0, 0.001, -10.0)
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
			var state: Dictionary = match_state.bindings[participant] if participant > 0 else (
				match_state.coasting_states[entity] as Dictionary)
			var actor: S04Kinematic = match_state.body_for_entity[entity]
			_record({"event": "simulation", "local_tick": local_tick,
				"pose": match_state.pose_for_entity(entity),
				"held": state.held, "receipt_ms": state.receipt_ms,
				"decision_age_ms": state.get("decision_age_ms", 0),
				"phase": "post_move_and_slide", "contacts": actor.get_slide_collision_count()})

		if tick % SNAPSHOT_INTERVAL_TICKS == 0:
			var envelope: Dictionary = replication.movement_envelope(match_state.bindings.keys())
			if not match_state.coasting_states.is_empty():
				coasting_snapshots += 1
				_record({ "event": "coasting_replication", "rows": envelope.rows })
			for peer_id: int in session.roster:
				if session.roster[peer_id].phase == "ADMITTED":
					replication.send_movement(peer_id, match_state.bindings.keys(), tick, 0.0)

	status.text = "S04 %s | %s | tick %d | local prediction" % [role, profile, local_tick]


## Records immediate local simulation separately from authoritative snapshot application.
func _on_predicted(receipt: Dictionary) -> void:
	if role != "client":
		return

	receipt["event"] = "prediction"
	_record(receipt)


## Records bounded rewind/replay work and simulation correction magnitude.
func _on_reconciled(receipt: Dictionary) -> void:
	if role != "client":
		return

	receipt["event"] = "correction"
	_record(receipt)


## Verifies rejection is unchanged and advances successful lifecycle acceptance.
func _on_exit_result(reason: String) -> void:
	exit_verdict = reason
	_record({"event": "exit_result", "reason": reason,
		"still_seated": match_state.seats.has(session.local_participant),
		"prediction_enabled": match_state.prediction_enabled})
	if scenario != SCENARIO_EXIT:
		return

	if lifecycle_stage == 1:
		if reason != "EXIT_MOVING" or not match_state.seats.has(session.local_participant) or (
			not match_state.prediction_enabled):
			_scenario_result(false, "moving rejection changed predicted lifecycle")
			return
		lifecycle_stage = 2
	elif lifecycle_stage == 3:
		if reason != "OK":
			_scenario_result(false, "stopped exit was not accepted")
			return
		lifecycle_stage = 4


## Receipts actual drawn frames independently of simulation and keeps matched camera captures.
func _on_rendered() -> void:
	if started_ms < 0 or ending or match_state.body_for_entity.is_empty():
		return

	var actor: S04Kinematic = match_state.local_body()
	var state: Dictionary = actor.display_state()
	var screen: Vector2 = camera_rig.camera().unproject_position(state.position + Vector3.UP)
	_record({"event": "render", "index": event_index, "tick": local_tick,
		"position": match_state.vector(state.position), "yaw": state.yaw,
		"sequence": actor.latest_sequence, "input_tick": actor.latest_input_tick,
		"screen": [screen.x, screen.y], "viewport": get_viewport().get_visible_rect().size})
	if capture_pending and (
		(state.position as Vector3).distance_to(capture_pose.position) > RESPONSE_DISTANCE_M
		or absf(angle_difference(state.yaw, capture_pose.yaw)) > deg_to_rad(RESPONSE_TURN_DEG)
	):
		_capture("after")
		capture_pending = false


## Retains early matched viewport frames; raw render telemetry covers every response event.
func _capture(suffix: String) -> void:
	var directory: String = OS.get_environment("S04_CAPTURE_DIR")
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
	if role == "client" and exit_verdict != "EXIT_MOVING":
		failures.append("moving exit did not preserve host-owned seat")
	if session.phase != "IDLE" or not match_state.bindings.is_empty() or (
		not match_state.entities.is_empty() or not match_state.pending_poses.is_empty()):
		failures.append("lifecycle cleanup incomplete")

	for actor: S04Kinematic in match_state.bodies:
		if actor.visible or actor.velocity != Vector3.ZERO or actor.collision_mask != 0:
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
	print("S04 " + JSON.stringify(record))
