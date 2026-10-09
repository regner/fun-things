class_name S04Match  # gdstyle:ignore=quality/max-class-variables
extends S03Match
## Reuses S03 lifecycle/markers while saved S04 bodies own planar vehicle motion.

signal stepped(tick: int)
signal predicted(receipt: Dictionary)
signal reconciled(receipt: Dictionary)

const MAX_POSE_COORDINATE_M: float = 100.0
const PREDICTION_HISTORY_LIMIT: int = 120
const EXIT_STOP_SPEED_MPS: float = 0.5
const PARKED_SPEED_MPS: float = 0.01

var server_tick: int = 0
var pending_poses: Dictionary = {}
var baseline_ticks: Dictionary = {}
var body_for_entity: Dictionary = {}
var spawns: Array[Transform3D] = []
var seats: Dictionary = {}
var coasting_bodies: Dictionary = {}
var prediction_history: Dictionary = {}
var prediction_ticks: Array[int] = []
var prediction_enabled: bool = false
var prediction_overflowed: bool = false
var queued_input_tick: int = 0
var queued_command: Dictionary = {}
var last_predicted_tick: int = 0
var last_correction: Dictionary = {}

@onready var bodies: Array[S04Kinematic] = [$Bodies/Host, $Bodies/Client]


## Disables every saved body's collision before descendants can enter replica callbacks.
func _enter_tree() -> void:
	for actor: S04Kinematic in [$Bodies/Host, $Bodies/Client]:
		actor.configure(false)
		actor.visible = false


## Retains authored dynamic spawn poses without changing saved world placement.
func _ready() -> void:
	for actor: S04Kinematic in bodies:
		spawns.append(actor.transform)


## Uses one shared vehicle step per authoritative tick, then acknowledges intent.
func _physics_process(delta: float) -> void:
	if authoritative:
		_server_step(delta)
	else:
		_client_step(delta)

	stepped.emit(server_tick)


## Advances admitted and disconnected coasting cars without inventing catch-up steps.
func _server_step(delta: float) -> void:
	server_tick += 1
	for participant: int in bindings:
		var binding: Dictionary = bindings[participant]
		var actor: S04Kinematic = body_for_entity[binding.entity]
		if not binding.admitted:
			actor.neutralize()
			continue

		binding.decision_age_ms = Time.get_ticks_msec() - int(binding.receipt_ms)
		if binding.decision_age_ms > HELD_EXPIRY_MS:
			binding.held = S04DriveRules.neutral()

		var held: Dictionary = binding.held
		actor.step(held, delta)
		binding.processed_input_tick = binding.pending_input_tick
		if binding.pending > binding.sequence:
			binding.sequence = binding.pending
			binding.sample = held.throttle
			accepted_count += 1

	for entity: int in coasting_bodies.keys():
		var actor: S04Kinematic = coasting_bodies[entity]
		actor.step(S04DriveRules.neutral(), delta)
		if actor.velocity.length() < PARKED_SPEED_MPS:
			actor.neutralize()
			coasting_bodies.erase(entity)


## Reconciles local prediction, installs remote poses, then predicts the current input tick.
func _client_step(delta: float) -> void:
	for entity: int in pending_poses:
		var pose: Dictionary = pending_poses[entity]
		var actor: S04Kinematic = body_for_entity[entity]
		if prediction_enabled and entity == bindings[participant_id].entity:
			_reconcile(actor, pose)
		else:
			actor.install_pose(pose, int(pose.receipt_ms))

		print("S04 " + JSON.stringify({"event": "apply", "time_ms": Time.get_ticks_msec(),
			"wall_ms": Time.get_unix_time_from_system() * 1000.0,
			"entity": entity, "pose": pose, "position": pose.position,
			"yaw": pose.yaw}))
	pending_poses.clear()

	if prediction_enabled and queued_input_tick > last_predicted_tick:
		_predict(queued_input_tick, queued_command, delta)


## Runs one local permitted step and retains only the bounded replay inputs.
func _predict(input_tick: int, command: Dictionary, delta: float) -> void:
	var actor: S04Kinematic = local_body()
	actor.step(command, delta)
	actor.latest_input_tick = input_tick
	prediction_history[input_tick] = { "command": command.duplicate(true), "delta": delta }
	prediction_ticks.append(input_tick)
	last_predicted_tick = input_tick
	if prediction_ticks.size() > PREDICTION_HISTORY_LIMIT:
		prediction_history.erase(prediction_ticks.pop_front())
		prediction_overflowed = true

	predicted.emit({"input_tick": input_tick, "position": vector(actor.global_position),
		"yaw": actor.rotation.y, "velocity": vector(actor.velocity),
		"history_size": prediction_ticks.size()})


## Restores the host pose and replays only unacknowledged local drive-rule frames.
func _reconcile(actor: S04Kinematic, pose: Dictionary) -> void:
	var previous_display: Dictionary = actor.display_state()
	var previous_position: Vector3 = actor.global_position
	var acknowledged_tick: int = pose.input_tick
	while not prediction_ticks.is_empty() and prediction_ticks[0] <= acknowledged_tick:
		prediction_history.erase(prediction_ticks.pop_front())

	actor.restore_authoritative(pose)
	var replayed: int = 0
	var started_usec: int = Time.get_ticks_usec()
	if prediction_overflowed:
		prediction_history.clear()
		prediction_ticks.clear()
		prediction_overflowed = false
	else:
		for tick: int in prediction_ticks:
			var frame: Dictionary = prediction_history[tick]
			actor.step(frame.command, frame.delta)
			actor.latest_input_tick = tick
			replayed += 1

	var elapsed_usec: int = Time.get_ticks_usec() - started_usec
	var correction_m: float = previous_position.distance_to(actor.global_position)
	actor.preserve_visual_pose(previous_display.position, previous_display.yaw)
	last_correction = {
		"authoritative_tick": pose.tick, "acknowledged_input_tick": acknowledged_tick,
		"magnitude_m": correction_m, "replayed": replayed, "cpu_usec": elapsed_usec,
		"cpu_per_tick_usec": float(elapsed_usec) / maxf(1.0, replayed)}
	reconciled.emit(last_correction)


## Adds a saved actual body to S03's provisional entity binding.
func prepare_initial(participant: int) -> int:
	var entity: int = super.prepare_initial(participant)
	if not body_for_entity.has(entity):
		_activate_body(entity, body_for_entity.size())
		bindings[participant].held = S04DriveRules.neutral()
		bindings[participant].pending_input_tick = 0
		bindings[participant].processed_input_tick = 0
		seats[participant] = {"player": entity, "vehicle": entity + 1000,
			"equipment": { "selected": "pistol", "magazine": 7 }, "seat": "driver"}
	return entity


## Configures fixed two-driver fixture bodies through their role before use.
func _activate_body(entity: int, slot: int) -> void:
	assert(slot < bodies.size(), "S04 fixture supports exactly two participants")
	var actor: S04Kinematic = bodies[slot]
	actor.transform = spawns[slot]
	actor.visible = true
	actor.configure(authoritative)
	body_for_entity[entity] = actor


## Captures actual controller state alongside the unchanged S03 durable cut.
func baseline(participant: int, baseline_id: int) -> Dictionary:
	var data: Dictionary = super.baseline(participant, baseline_id)
	var poses: Array = []
	for binding: Dictionary in bindings.values():
		poses.append(pose_for_entity(binding.entity))
	data["poses"] = poses
	data["seats"] = seats.duplicate(true)
	return data


## Validates the entire car/seat cut before inherited lifecycle mutation.
func apply_baseline(data: Dictionary) -> bool:
	var cut: Dictionary = data.duplicate(true)
	var rows: Dictionary = _baseline_rows(cut)
	if rows.is_empty() or not _baseline_poses(cut, rows) or not _baseline_seats(cut, rows):
		return false

	if not super.apply_baseline(cut):
		return false

	for key: Variant in cut.seats:
		seats[int(key)] = cut.seats[key].duplicate(true)

	for pose: Dictionary in cut.poses:
		var entity: int = pose.entity
		_activate_body(entity, body_for_entity.size())
		body_for_entity[entity].install_pose(pose, Time.get_ticks_msec())
		# Installed state fences old delivery but cannot satisfy fresh-movement admission.
		baseline_ticks[entity] = pose.tick

	for participant: int in bindings:
		bindings[participant].held = S04DriveRules.neutral()
		bindings[participant].pending_input_tick = 0
		bindings[participant].processed_input_tick = 0
	return true


## Checks the fixed two-player durable dependency map without touching replica state.
func _baseline_rows(cut: Dictionary) -> Dictionary:
	for field: String in ["participant", "durable", "baseline", "revision"]:
		if not _positive_integer(cut.get(field)):
			return {}

	var rows: Variant = cut.get("rows")
	if not rows is Array or rows.size() != 2:
		return {}

	var result: Dictionary = {}
	var participants: Dictionary = {}
	for row: Variant in rows:
		if not _baseline_row_valid(row):
			return {}
		if result.has(int(row.entity)) or participants.has(int(row.participant)):
			return {}
		result[int(row.entity)] = row
		participants[int(row.participant)] = true

	return result if participants.has(int(cut.participant)) else {}


## Requires bounded integral durable dependencies, including injured health.
func _baseline_row_valid(row: Variant) -> bool:
	if not row is Dictionary or row.size() != 6:
		return false

	for field: String in ["participant", "entity", "generation", "life", "control"]:
		if not _positive_integer(row.get(field)):
			return false

	var health: Variant = row.get("health")
	return (health is float or health is int) and is_finite(float(health)) \
		and float(health) == int(health) and health >= 0 and health <= 100


## Normalizes JSON integers and binds each unique pose to the durable cut.
func _baseline_poses(cut: Dictionary, rows: Dictionary) -> bool:
	var poses: Variant = cut.get("poses")
	if not poses is Array or poses.size() != 2:
		return false

	var seen: Dictionary = {}
	for pose: Variant in poses:
		if not _normalize_pose(pose) or not rows.has(pose.entity) or seen.has(pose.entity):
			return false
		var row: Dictionary = rows[pose.entity]
		for field: String in ["generation", "life", "control"]:
			if pose[field] != row[field]:
				return false
		if pose.vehicle != pose.entity + 1000 or pose.collision != 1 or pose.durable != cut.durable:
			return false
		seen[pose.entity] = true

	return true


## Accepts only finite bounded integral wire fields before normal pose validation.
func _normalize_pose(pose: Variant) -> bool:
	if not pose is Dictionary:
		return false

	for field: String in ["entity", "tick", "control", "durable", "sequence", "input_tick",
		"vehicle", "generation", "life", "collision"]:
		var value: Variant = pose.get(field)
		if not (value is float or value is int) or not is_finite(float(value)):
			return false
		if value < 0 or value > 2_147_483_647 or float(value) != int(value):
			return false
		pose[field] = int(value)

	return pose_valid(pose)


## Requires exactly one matching fixed driver seat per durable participant.
func _baseline_seats(cut: Dictionary, rows: Dictionary) -> bool:
	var installed: Variant = cut.get("seats")
	if not installed is Dictionary or installed.size() != 2:
		return false

	for row: Dictionary in rows.values():
		var key: Variant = row.participant
		var seat: Variant = installed.get(int(key), installed.get(str(int(key))))
		if not _seat_valid(seat, int(row.entity)):
			return false

	return true


## Validates the fixture sentinel without inventing production equipment or seat policy.
func _seat_valid(seat: Variant, entity: int) -> bool:
	if not seat is Dictionary or seat.size() != 4 or seat.get("seat") != "driver":
		return false

	if seat.get("player") != entity or seat.get("vehicle") != entity + 1000:
		return false

	var equipment: Variant = seat.get("equipment")
	if not equipment is Dictionary or equipment.size() != 2:
		return false

	return equipment.get("selected") == "pistol" and equipment.get("magazine") == 7


## Bounds small fixture IDs before integer conversion or inherited indexing.
func _positive_integer(value: Variant) -> bool:
	return (value is int or value is float) and is_finite(float(value)) \
		and value > 0 and value <= 2_147_483_647 and float(value) == int(value)


## Retains S03's sender/context/window checks while accepting bounded drive intent.
func _held_shape_valid(envelope: Variant) -> bool:
	if not envelope is Dictionary or envelope.size() != 4:
		return false

	for field: String in ["context", "sequence", "input_tick", "move"]:
		if not envelope.has(field):
			return false

	if not envelope.sequence is int or not envelope.input_tick is int:
		return false
	if envelope.input_tick <= 0 or not envelope.move is Dictionary:
		return false

	return _drive_valid(envelope.move)


## Retains the newest validated client tick for post-simulation acknowledgement.
func submit_held(participant: int, envelope: Variant) -> String:
	var result: String = super.submit_held(participant, envelope)
	if result == "OK":
		bindings[participant].pending_input_tick = envelope.input_tick
	return result


## Validates only the four primitive bounded car controls.
func _drive_valid(held: Dictionary) -> bool:
	if held.size() != 4 or not held.get("handbrake") is bool:
		return false

	for field: String in ["throttle", "steer", "brake"]:
		if not held.get(field) is float or not is_finite(held[field]):
			return false
		if absf(held[field]) > 1.0:
			return false

	return held.brake >= 0.0


## Begins a fresh control binding neutral without resetting actual pose or durable health.
func prepare_resync(participant: int) -> void:
	super.prepare_resync(participant)
	bindings[participant].held = S04DriveRules.neutral()
	bindings[participant].pending_input_tick = 0
	bindings[participant].processed_input_tick = 0
	body_for_entity[bindings[participant].entity].neutralize()


## Publishes only movement state and consumed-or-superseded sequence after simulation.
func pose_for_entity(entity: int) -> Dictionary:
	var actor: S04Kinematic = body_for_entity[entity]
	var participant: int = participant_for_entity(entity)
	var binding: Dictionary = bindings[participant]
	return {"entity": entity, "tick": server_tick, "control": binding.control,
		"durable": durable_revision, "position": vector(actor.global_position),
		"yaw": actor.rotation.y, "velocity": vector(actor.velocity), "sequence": binding.sequence,
		"input_tick": binding.processed_input_tick,
		"vehicle": entity + 1000, "generation": binding.generation,
		"life": binding.life, "collision": 1}


## Validates a bounded pose's exact primitive fields before any replica state change.
func pose_valid(pose: Variant) -> bool:  # gdstyle:ignore=quality/max-returns
	if not pose is Dictionary or pose.size() != 13:
		return false

	for field: String in ["entity", "tick", "control", "durable", "sequence", "input_tick",
		"vehicle", "generation", "life", "collision"]:
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

	for pose: Dictionary in rows:
		var entity: int = pose.entity
		if not body_for_entity.has(entity) or pose.durable > durable_revision:
			continue

		var participant: int = participant_for_entity(entity)
		if pose.vehicle != entity + 1000 or pose.generation != bindings[participant].generation:
			continue
		if pose.life != bindings[participant].life or pose.collision != 1:
			continue
		if pose.control != bindings[participant].control:
			continue
		if pose.tick <= maxi(int(motion_ticks.get(entity, -1)),
			int(baseline_ticks.get(entity, -1))):
			continue

		motion_ticks[entity] = pose.tick
		var pending_pose: Dictionary = pose.duplicate(true)
		pending_pose["receipt_ms"] = Time.get_ticks_msec()
		pending_poses[entity] = pending_pose

	return true


## Resolves a body through the binding owner rather than accepting client identity claims.
func participant_for_entity(entity: int) -> int:
	for participant: int in bindings:
		if bindings[participant].entity == entity:
			return participant
	return 0


## Enables local prediction only after admission and fresh dependent movement.
func enable_local() -> void:
	super.enable_local()
	if not authoritative and bindings.has(participant_id):
		prediction_enabled = true
		local_body().configure_prediction()


## Queues one numbered local input; simulation consumes it on the next client physics step.
func queue_local_input(input_tick: int, command: Dictionary) -> void:
	if authoritative or not prediction_enabled or input_tick <= queued_input_tick:
		return

	queued_input_tick = input_tick
	queued_command = command.duplicate(true)


## Host-validates exit without allowing the predicted client to pre-empt the verdict.
func request_exit(participant: int) -> String:
	if not authoritative or not bindings.has(participant) or not bindings[participant].admitted:
		return "NOT_ADMITTED"

	var actor: S04Kinematic = body_for_entity[bindings[participant].entity]
	if actor.velocity.length() >= EXIT_STOP_SPEED_MPS:
		return "EXIT_MOVING"

	bindings[participant].admitted = false
	bindings[participant].held = S04DriveRules.neutral()
	actor.neutralize()
	seats.erase(participant)
	return "OK"


## Returns the current locally controlled body's public actual motion API.
func local_body() -> S04Kinematic:
	return body_for_entity[bindings[participant_id].entity] as S04Kinematic


## Releases a disconnected driver while the authoritative car coasts under shared rules.
func rollback(participant: int) -> void:
	if bindings.has(participant):
		var entity: int = bindings[participant].entity
		var actor: S04Kinematic = body_for_entity[entity]
		if authoritative and bindings[participant].admitted:
			coasting_bodies[entity] = actor
		else:
			actor.retire()
			body_for_entity.erase(entity)
		pending_poses.erase(entity)
		baseline_ticks.erase(entity)
	seats.erase(participant)
	super.rollback(participant)


## Completes body neutralization and clears buffers before S03 publishes closing state.
func clear() -> void:
	for actor: S04Kinematic in body_for_entity.values():
		actor.retire()
	body_for_entity.clear()
	pending_poses.clear()
	baseline_ticks.clear()
	seats.clear()
	coasting_bodies.clear()
	prediction_history.clear()
	prediction_ticks.clear()
	prediction_enabled = false
	prediction_overflowed = false
	queued_input_tick = 0
	queued_command.clear()
	last_predicted_tick = 0
	last_correction.clear()
	super.clear()


## Encodes local vectors into the bounded primitive wire representation.
func vector(value: Vector3) -> Array[float]:
	return [value.x, value.y, value.z]
