class_name S03RMatch
extends S03Match
## Reuses S03 lifecycle/markers while saved S02-derived bodies own actual foot motion.

signal stepped(tick: int)
signal reconciled(details: Dictionary)
signal held_received(participant: int, sequence: int, receipt_ms: int)
signal movement_buffered(rows: Array)

const BODY_LAYER: int = 2
const BODY_MASK: int = 3
const MAX_POSE_COORDINATE_M: float = 100.0
const MAX_INPUT_TICK: int = 2_147_483_647

var server_tick: int = 0
var pending_poses: Dictionary = {}
var baseline_ticks: Dictionary = {}
var expiry_decision_ages: Dictionary = {}
var body_for_entity: Dictionary = {}
var spawns: Array[Transform3D] = []
var input_queues: Dictionary = {}
var prediction_history: S03PredictionHistory = S03PredictionHistory.new()
var queued_prediction: Dictionary = {}
var last_replay_frames: int = 0
var last_replay_usec: int = 0
var last_authority_install_error_m: float = 0.0

@onready var bodies: Array[S03RActor] = [$Bodies/Host, $Bodies/Client]


## Disables every saved body's collision before descendants can enter replica callbacks.
func _enter_tree() -> void:
	for actor: S03RActor in [$Bodies/Host, $Bodies/Client]:
		actor.collision_layer = 0
		actor.collision_mask = 0
		actor.visible = false


## Retains authored dynamic spawn poses without changing saved world placement.
func _ready() -> void:
	for actor: S03RActor in bodies:
		spawns.append(actor.transform)


## Uses one shared actual-controller step per authoritative tick, then acknowledges intent.
func _physics_process(delta: float) -> void:
	if authoritative:
		_step_authority(delta)
	else:
		for entity: int in pending_poses:
			var pose: Dictionary = pending_poses[entity]
			var actor: S03RActor = body_for_entity[entity]
			if actor.predicted_local:
				_reconcile_local(actor, pose)
			else:
				actor.install_pose(pose, int(pose.receipt_ms))
				last_authority_install_error_m = actor.global_position.distance_to(
					_vector_from_wire(pose.position)
				)
			print("S03R " + JSON.stringify({"event": "apply", "time_ms": Time.get_ticks_msec(),
				"wall_ms": Time.get_unix_time_from_system() * 1000.0,
				"entity": entity, "pose": pose, "position": vector(actor.global_position),
				"yaw": actor.rotation.y,
				"authority_install_error_m": last_authority_install_error_m}))
		pending_poses.clear()
		_apply_queued_prediction()

	stepped.emit(server_tick)


## Consumes at most one numbered frame for each admitted participant this host tick.
func _step_authority(delta: float) -> void:
	server_tick += 1
	for participant: int in bindings:
		var binding: Dictionary = bindings[participant]
		var actor: S03RActor = body_for_entity[binding.entity]
		if not binding.admitted:
			actor.neutralize()
			continue

		binding.held_age_ms = Time.get_ticks_msec() - int(binding.receipt_ms)
		expiry_decision_ages[binding.entity] = binding.held_age_ms
		binding.held = consume_authority_input(
			participant, actor.rotation.y, binding.held_age_ms
		)
		var held: Dictionary = binding.held
		actor.step({ "move": held.move, "aim_yaw": held.aim_yaw, "fire": false }, delta)


## Consumes, supersedes or expires one participant's pending input for this host step.
func consume_authority_input(
	participant: int, fallback_yaw: float, receipt_age_ms: int
) -> Dictionary:
	var binding: Dictionary = bindings[participant]
	var queue: S03InputFrameQueue = input_queues[participant]
	var frame: Dictionary
	if receipt_age_ms > HELD_EXPIRY_MS:
		frame = queue.supersede_all(binding.sequence, binding.last_input_tick)
	else:
		frame = queue.pop_next(binding.sequence, binding.last_input_tick)
	if frame.is_empty():
		return { "move": Vector2.ZERO, "aim_yaw": fallback_yaw,
			"input_tick": binding.last_input_tick }

	binding.sequence = frame.sequence
	binding.last_input_tick = frame.input_tick
	binding.superseded_count += frame.superseded_count
	if receipt_age_ms > HELD_EXPIRY_MS:
		binding.sample = 0.0
		return { "move": Vector2.ZERO, "aim_yaw": fallback_yaw,
			"input_tick": binding.last_input_tick }

	binding.sample = (frame.move as Vector2).length()
	accepted_count += 1
	return { "move": frame.move, "aim_yaw": frame.aim_yaw,
		"input_tick": frame.input_tick }


## Replaces one participant's authority queue at a lifecycle fence.
func _reset_input_queue(participant: int) -> void:
	input_queues[participant] = S03InputFrameQueue.new(SEQUENCE_WINDOW)


## Queues one local numbered input for the client physics owner to simulate once.
func queue_local_prediction(input_tick: int, command: Dictionary, delta_seconds: float) -> void:
	if authoritative or input_tick <= 0 or not queued_prediction.is_empty():
		return
	queued_prediction = {
		"tick": input_tick, "command": command.duplicate(true), "delta": delta_seconds,
	}


## Applies the queued local frame through the same actor and motion rule as authority.
func _apply_queued_prediction() -> void:
	if queued_prediction.is_empty() or not bindings.has(participant_id):
		queued_prediction.clear()
		return

	var actor: S03RActor = local_body()
	prediction_history.push(
		queued_prediction.tick, queued_prediction.command, queued_prediction.delta
	)
	actor.step(queued_prediction.command, queued_prediction.delta)
	actor.latest_predicted_tick = int(queued_prediction.tick)
	queued_prediction.clear()


## Restores authority, replays unacknowledged frames, and emits correction measurements.
func _reconcile_local(actor: S03RActor, pose: Dictionary) -> void:
	var before_position: Vector3 = actor.global_position
	var before_yaw: float = actor.rotation.y
	var before_display: Transform3D = actor.display_transform()
	var replay: Dictionary = prediction_history.acknowledge(int(pose.last_input_tick))
	var started_usec: int = Time.get_ticks_usec()
	actor.restore_authority(pose)
	last_authority_install_error_m = actor.global_position.distance_to(
		_vector_from_wire(pose.position)
	)
	for frame: Dictionary in replay.frames:
		actor.step(frame.command, frame.delta)
		actor.latest_predicted_tick = int(frame.tick)
	last_replay_usec = Time.get_ticks_usec() - started_usec
	last_replay_frames = replay.frames.size()
	actor.smooth_correction_from(before_display)

	var correction_m: float = before_position.distance_to(actor.global_position)
	var correction_yaw_deg: float = rad_to_deg(absf(angle_difference(
		before_yaw, actor.rotation.y
	)))
	reconciled.emit({
		"ack_input_tick": pose.last_input_tick,
		"correction_m": correction_m,
		"correction_yaw_deg": correction_yaw_deg,
		"replay_frames": last_replay_frames,
		"replay_usec": last_replay_usec,
		"history_exhausted": replay.history_exhausted,
		"cause": _misprediction_cause(actor, correction_m),
	})


## Labels only causes observable in this fixture rather than inferring hidden contacts.
func _misprediction_cause(actor: S03RActor, correction_m: float) -> String:
	if correction_m <= 0.001:
		return "none"
	if actor.get_slide_collision_count() > 0:
		return "static_collision"
	for other: S03RActor in body_for_entity.values():
		if other != actor and other.global_position.distance_to(actor.global_position) < 1.0:
			return "remote_actor_contact"
	return "held_timing_or_delivery"


## Adds a saved actual body to S03's provisional entity binding.
func prepare_initial(participant: int) -> int:
	var entity: int = super.prepare_initial(participant)
	if not body_for_entity.has(entity):
		_activate_body(entity, body_for_entity.size())
		bindings[participant].held = {
			"move": Vector2.ZERO, "aim_yaw": 0.0, "input_tick": 0,
		}
		bindings[participant].last_input_tick = 0
		bindings[participant].held_age_ms = 0
		bindings[participant].superseded_count = 0
		_reset_input_queue(participant)
	return entity


## Configures fixed two-player fixture bodies through their role before use.
func _activate_body(entity: int, slot: int) -> void:
	assert(slot < bodies.size(), "S03-R fixture supports exactly two participants")
	var actor: S03RActor = bodies[slot]
	actor.transform = spawns[slot]
	actor.visible = true
	var local_entity: int = 0
	if not authoritative and bindings.has(participant_id):
		local_entity = int(bindings[participant_id].entity)
	actor.predicted_local = not authoritative and entity == local_entity
	actor.remote_view = not authoritative and not actor.predicted_local
	actor.collision_layer = BODY_LAYER if authoritative or actor.predicted_local else 0
	actor.collision_mask = BODY_MASK if authoritative or actor.predicted_local else 0
	body_for_entity[entity] = actor


## Captures actual controller state alongside the unchanged S03 durable cut.
func baseline(participant: int, baseline_id: int) -> Dictionary:
	var data: Dictionary = super.baseline(participant, baseline_id)
	var poses: Array = []
	for entity: int in body_for_entity:
		poses.append(pose_for_entity(entity))
	data["poses"] = poses
	return data


## Preflights actual poses before S03 atomically installs its baseline and local rig.
func apply_baseline(data: Dictionary) -> bool:  # gdstyle:ignore=quality/max-returns
	var poses: Variant = data.get("poses")
	if not poses is Array or poses.size() != 2:
		return false

	for pose: Variant in poses:
		if not pose is Dictionary:
			return false
		# JSON encodes these tiny fixture integers as numeric values, never native objects.
		for field: String in [
			"entity", "tick", "control", "durable", "sequence", "last_input_tick",
		]:
			var value: Variant = pose.get(field)
			if not (value is float or value is int) or not is_finite(float(value)):
				return false
			if float(value) != int(value):
				return false
			pose[field] = int(value)
		if not pose_valid(pose):
			return false

	if not super.apply_baseline(data):
		return false

	for pose: Dictionary in poses:
		var entity: int = int(pose.entity)
		if not entities.has(entity):
			return false
		_activate_body(entity, body_for_entity.size())
		body_for_entity[entity].install_pose(pose, Time.get_ticks_msec())
		# Baseline state fences old delivery but cannot satisfy fresh-movement admission.
		baseline_ticks[entity] = int(pose.tick)

	for participant: int in bindings:
		bindings[participant].held = {
			"move": Vector2.ZERO, "aim_yaw": 0.0, "input_tick": 0,
		}
		bindings[participant].last_input_tick = 0
		bindings[participant].held_age_ms = 0
		bindings[participant].superseded_count = 0
		_reset_input_queue(participant)
	prediction_history.clear()
	queued_prediction.clear()
	return true


## Retains sender/context/window checks while queueing numbered physics input frames.
func submit_held(  # gdstyle:ignore=quality/max-returns
	participant: int, envelope: Variant
) -> String:
	if not authoritative or not bindings.has(participant) or not bindings[participant].admitted:
		return _reject("NOT_ADMITTED")
	if not _held_shape_valid(envelope):
		return _reject("INVALID")
	if envelope.context != context(participant):
		return _reject("STALE_CONTEXT")

	var binding: Dictionary = bindings[participant]
	var frames: Array = envelope.frames
	var newest_sequence: int = int(frames[-1].sequence)
	if newest_sequence > int(binding.sequence) + SEQUENCE_WINDOW:
		return _reject("WINDOW")
	var queue: S03InputFrameQueue = input_queues[participant]
	if not queue.offer(frames, binding.sequence, binding.last_input_tick):
		return _reject("INPUT_QUEUE")
	if not queue.last_offer_added():
		return "OK"

	binding.pending = maxi(binding.pending, newest_sequence)
	binding.receipt_ms = Time.get_ticks_msec()
	held_received.emit(participant, newest_sequence, int(binding.receipt_ms))
	return "OK"


## Accepts an ordered bounded burst of normalized numbered foot frames.
func _held_shape_valid(envelope: Variant) -> bool:
	if not envelope is Dictionary or envelope.size() != 2:
		return false
	if not envelope.get("context") is Dictionary or not envelope.get("frames") is Array:
		return false
	var frames: Array = envelope.frames
	if frames.is_empty() or frames.size() > 3:
		return false

	var previous_sequence: int = -1
	var previous_tick: int = -1
	for frame: Variant in frames:
		if not _input_frame_valid(frame):
			return false
		if previous_sequence >= 0 and (
			frame.sequence != previous_sequence + 1 or frame.input_tick != previous_tick + 1
		):
			return false
		previous_sequence = frame.sequence
		previous_tick = frame.input_tick
	return true


## Validates one complete physics input frame before queue mutation.
func _input_frame_valid(frame: Variant) -> bool:
	if not frame is Dictionary or frame.size() != 4:
		return false
	if not frame.get("sequence") is int or not frame.get("input_tick") is int:
		return false
	if not frame.get("move") is Vector2 or not frame.get("aim_yaw") is float:
		return false
	var move: Vector2 = frame.move
	return frame.sequence > 0 and frame.input_tick > 0 and (
		frame.input_tick <= MAX_INPUT_TICK and move.is_finite()
		and move.length_squared() <= 1.0 and is_finite(frame.aim_yaw)
		and absf(frame.aim_yaw) <= PI)


## Begins a fresh control binding neutral without resetting actual pose or durable health.
func prepare_resync(participant: int) -> void:
	super.prepare_resync(participant)
	bindings[participant].held = {
		"move": Vector2.ZERO, "aim_yaw": 0.0, "input_tick": 0,
	}
	bindings[participant].last_input_tick = 0
	bindings[participant].held_age_ms = 0
	bindings[participant].superseded_count = 0
	input_queues[participant].clear()
	body_for_entity[bindings[participant].entity].neutralize()
	prediction_history.clear()
	queued_prediction.clear()


## Publishes only movement state and consumed-or-superseded sequence after simulation.
func pose_for_entity(entity: int) -> Dictionary:
	var actor: S03RActor = body_for_entity[entity]
	var participant: int = participant_for_entity(entity)
	var binding: Dictionary = bindings[participant]
	return {"entity": entity, "tick": server_tick, "control": binding.control,
		"durable": durable_revision, "position": vector(actor.global_position),
		"yaw": actor.rotation.y, "velocity": vector(actor.velocity), "sequence": binding.sequence,
		"last_input_tick": binding.last_input_tick}


## Validates a bounded pose's exact primitive fields before any replica state change.
func pose_valid(pose: Variant) -> bool:  # gdstyle:ignore=quality/max-returns
	if not pose is Dictionary or pose.size() != 9:
		return false

	for field: String in [
		"entity", "tick", "control", "durable", "sequence", "last_input_tick",
	]:
		if not pose.get(field) is int or pose[field] < 0:
			return false

	if not pose.get("yaw") is float or not is_finite(pose.yaw) or absf(pose.yaw) > PI:
		return false

	for field: String in ["position", "velocity"]:
		var values: Variant = pose.get(field)
		if not values is Array or values.size() != 3:
			return false

		for value: Variant in values:
			if not (value is float or value is int) or not is_finite(float(value)):
				return false
			if absf(float(value)) > MAX_POSE_COORDINATE_M:
				return false

	return pose.entity > 0 and pose.control > 0 and pose.durable > 0


## Buffers only the latest dependency-valid pose per entity for next physics installation.
func apply_movement(envelope: Dictionary) -> bool:
	if envelope.get("session") != session_id or envelope.get("revision") != 1:
		return false

	var rows: Variant = envelope.get("rows")
	if not rows is Array or rows.size() > 2:
		return false

	for pose: Variant in rows:
		if not pose_valid(pose):
			return false

	var buffered: Array = []
	for pose: Dictionary in rows:
		var entity: int = pose.entity
		if not body_for_entity.has(entity) or pose.durable > durable_revision:
			continue

		var participant: int = participant_for_entity(entity)
		if pose.control != bindings[participant].control:
			continue
		if pose.tick <= maxi(int(motion_ticks.get(entity, -1)),
			int(baseline_ticks.get(entity, -1))):
			continue

		motion_ticks[entity] = pose.tick
		var pending_pose: Dictionary = pose.duplicate(true)
		pending_pose["receipt_ms"] = Time.get_ticks_msec()
		pending_poses[entity] = pending_pose
		buffered.append({ "entity": entity, "sequence": pose.sequence, "tick": pose.tick })

	if not buffered.is_empty():
		movement_buffered.emit(buffered)
	return true


## Resolves a body through the binding owner rather than accepting client identity claims.
func participant_for_entity(entity: int) -> int:
	for participant: int in bindings:
		if bindings[participant].entity == entity:
			return participant
	return 0


## Returns the current locally controlled body's public actual motion API.
func local_body() -> S03RActor:
	return body_for_entity[bindings[participant_id].entity] as S03RActor


## Removes participant state and immediately retires its physical/presentation body.
func rollback(participant: int) -> void:
	if bindings.has(participant):
		var entity: int = bindings[participant].entity
		body_for_entity[entity].retire()
		body_for_entity.erase(entity)
		pending_poses.erase(entity)
		baseline_ticks.erase(entity)
		expiry_decision_ages.erase(entity)
		input_queues.erase(participant)
		if participant == participant_id:
			prediction_history.clear()
			queued_prediction.clear()
	super.rollback(participant)


## Completes body neutralization and clears buffers before S03 publishes closing state.
func clear() -> void:
	for actor: S03RActor in body_for_entity.values():
		actor.retire()
	body_for_entity.clear()
	pending_poses.clear()
	baseline_ticks.clear()
	expiry_decision_ages.clear()
	input_queues.clear()
	prediction_history.clear()
	queued_prediction.clear()
	super.clear()


## Decodes one validated wire vector for exact authority-install measurements.
func _vector_from_wire(values: Array) -> Vector3:
	return Vector3(values[0], values[1], values[2])


## Encodes local vectors into the bounded primitive wire representation.
func vector(value: Vector3) -> Array[float]:
	return [value.x, value.y, value.z]
