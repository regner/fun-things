class_name S04Match
extends S03Match
## Reuses S03 lifecycle/markers while saved S04 bodies own planar vehicle motion.

signal stepped(tick: int)

const BODY_LAYER: int = 4
const BODY_MASK: int = 5
const MAX_POSE_COORDINATE_M: float = 100.0

var server_tick: int = 0
var pending_poses: Dictionary = {}
var baseline_ticks: Dictionary = {}
var body_for_entity: Dictionary = {}
var spawns: Array[Transform3D] = []
var seats: Dictionary = {}

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
		server_tick += 1
		for participant: int in bindings:
			var binding: Dictionary = bindings[participant]
			var actor: S04Kinematic = body_for_entity[binding.entity]
			if not binding.admitted:
				actor.neutralize()
				continue

			if Time.get_ticks_msec() - int(binding.receipt_ms) > HELD_EXPIRY_MS:
				binding.held = S04DriveRules.neutral()

			var held: Dictionary = binding.held
			actor.step(held, delta)
			if binding.pending > binding.sequence:
				binding.sequence = binding.pending
				binding.sample = held.throttle
				accepted_count += 1

	else:
		for entity: int in pending_poses:
			var pose: Dictionary = pending_poses[entity]
			var actor: S04Kinematic = body_for_entity[entity]
			actor.install_pose(pose, int(pose.receipt_ms))
			print("S04 " + JSON.stringify({"event": "apply", "time_ms": Time.get_ticks_msec(),
				"wall_ms": Time.get_unix_time_from_system() * 1000.0,
				"entity": entity, "pose": pose, "position": vector(actor.global_position),
				"yaw": actor.rotation.y}))
		pending_poses.clear()

	stepped.emit(server_tick)


## Adds a saved actual body to S03's provisional entity binding.
func prepare_initial(participant: int) -> int:
	var entity: int = super.prepare_initial(participant)
	if not body_for_entity.has(entity):
		_activate_body(entity, body_for_entity.size())
		bindings[participant].held = S04DriveRules.neutral()
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
	for entity: int in body_for_entity:
		poses.append(pose_for_entity(entity))
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

	for field: String in ["entity", "tick", "control", "durable", "sequence",
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
	if not envelope is Dictionary or envelope.size() != 3:
		return false

	if not envelope.has("context") or not envelope.has("sequence") or not envelope.has("move"):
		return false

	if not envelope.sequence is int or not envelope.move is Dictionary:
		return false

	return _drive_valid(envelope.move)


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
	body_for_entity[bindings[participant].entity].neutralize()


## Publishes only movement state and consumed-or-superseded sequence after simulation.
func pose_for_entity(entity: int) -> Dictionary:
	var actor: S04Kinematic = body_for_entity[entity]
	var participant: int = participant_for_entity(entity)
	var binding: Dictionary = bindings[participant]
	return {"entity": entity, "tick": server_tick, "control": binding.control,
		"durable": durable_revision, "position": vector(actor.global_position),
		"yaw": actor.rotation.y, "velocity": vector(actor.velocity), "sequence": binding.sequence,
		"vehicle": entity + 1000, "generation": binding.generation,
		"life": binding.life, "collision": 1}


## Validates a bounded pose's exact primitive fields before any replica state change.
func pose_valid(pose: Variant) -> bool:  # gdstyle:ignore=quality/max-returns
	if not pose is Dictionary or pose.size() != 12:
		return false

	for field: String in ["entity", "tick", "control", "durable", "sequence",
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


## Returns the current locally controlled body's public actual motion API.
func local_body() -> S04Kinematic:
	return body_for_entity[bindings[participant_id].entity] as S04Kinematic


## Removes participant state and immediately retires its physical/presentation body.
func rollback(participant: int) -> void:
	if bindings.has(participant):
		var entity: int = bindings[participant].entity
		body_for_entity[entity].retire()
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
	super.clear()


## Encodes local vectors into the bounded primitive wire representation.
func vector(value: Vector3) -> Array[float]:
	return [value.x, value.y, value.z]
