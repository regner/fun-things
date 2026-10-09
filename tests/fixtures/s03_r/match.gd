class_name S03RMatch
extends S03Match
## Reuses S03 lifecycle/markers while saved S02-derived bodies own actual foot motion.

signal stepped(tick: int)

const BODY_LAYER: int = 2
const BODY_MASK: int = 3
const MAX_POSE_COORDINATE_M: float = 100.0

var server_tick: int = 0
var pending_poses: Dictionary = {}
var baseline_ticks: Dictionary = {}
var body_for_entity: Dictionary = {}
var spawns: Array[Transform3D] = []

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
		server_tick += 1
		for participant: int in bindings:
			var binding: Dictionary = bindings[participant]
			var actor: S03RActor = body_for_entity[binding.entity]
			if not binding.admitted:
				actor.neutralize()
				continue

			if Time.get_ticks_msec() - int(binding.receipt_ms) > HELD_EXPIRY_MS:
				binding.held = { "move": Vector2.ZERO, "aim_yaw": actor.rotation.y }

			var held: Dictionary = binding.held
			actor.step(held.move, held.aim_yaw, delta)
			if binding.pending > binding.sequence:
				binding.sequence = binding.pending
				binding.sample = (held.move as Vector2).length()
				accepted_count += 1

	else:
		for entity: int in pending_poses:
			var pose: Dictionary = pending_poses[entity]
			var actor: S03RActor = body_for_entity[entity]
			actor.install_pose(pose, int(pose.receipt_ms))
			print("S03R " + JSON.stringify({"event": "apply", "time_ms": Time.get_ticks_msec(),
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
		bindings[participant].held = { "move": Vector2.ZERO, "aim_yaw": 0.0 }
	return entity


## Configures fixed two-player fixture bodies through their role before use.
func _activate_body(entity: int, slot: int) -> void:
	assert(slot < bodies.size(), "S03-R fixture supports exactly two participants")
	var actor: S03RActor = bodies[slot]
	actor.transform = spawns[slot]
	actor.visible = true
	actor.remote_view = not authoritative and slot + 1 != participant_id
	actor.collision_layer = BODY_LAYER if authoritative else 0
	actor.collision_mask = BODY_MASK if authoritative else 0
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
		for field: String in ["entity", "tick", "control", "durable", "sequence"]:
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
		bindings[participant].held = { "move": Vector2.ZERO, "aim_yaw": 0.0 }
	return true


## Retains sender/context/window checks while queueing the complete foot command.
func submit_held(participant: int, envelope: Variant) -> String:
	if not authoritative or not bindings.has(participant) or not bindings[participant].admitted:
		return _reject("NOT_ADMITTED")
	if not _held_shape_valid(envelope):
		return _reject("INVALID")
	if not envelope.context is Dictionary or envelope.context != context(participant):
		return _reject("STALE_CONTEXT")

	var binding: Dictionary = bindings[participant]
	var floor_sequence: int = maxi(int(binding.sequence), int(binding.pending))
	if envelope.sequence <= floor_sequence:
		return _reject("STALE_SEQUENCE")
	if envelope.sequence > int(binding.sequence) + SEQUENCE_WINDOW:
		return _reject("WINDOW")

	binding.pending = envelope.sequence
	binding.held = { "move": envelope.move, "aim_yaw": envelope.aim_yaw }
	binding.receipt_ms = Time.get_ticks_msec()
	return "OK"


## Accepts normalized world movement and a finite canonical aim yaw.
func _held_shape_valid(envelope: Variant) -> bool:
	if not envelope is Dictionary or envelope.size() != 4:
		return false
	if not envelope.has("context") or not envelope.has("sequence") or not (
		envelope.has("move") and envelope.has("aim_yaw")):
		return false
	if not envelope.sequence is int or not envelope.move is Vector2 or not (
		envelope.aim_yaw is float):
		return false

	var move: Vector2 = envelope.move
	return move.is_finite() and move.length_squared() <= 1.0 and (
		is_finite(envelope.aim_yaw) and absf(envelope.aim_yaw) <= PI)


## Begins a fresh control binding neutral without resetting actual pose or durable health.
func prepare_resync(participant: int) -> void:
	super.prepare_resync(participant)
	bindings[participant].held = { "move": Vector2.ZERO, "aim_yaw": 0.0 }
	body_for_entity[bindings[participant].entity].neutralize()


## Publishes only movement state and consumed-or-superseded sequence after simulation.
func pose_for_entity(entity: int) -> Dictionary:
	var actor: S03RActor = body_for_entity[entity]
	var participant: int = participant_for_entity(entity)
	var binding: Dictionary = bindings[participant]
	return {"entity": entity, "tick": server_tick, "control": binding.control,
		"durable": durable_revision, "position": vector(actor.global_position),
		"yaw": actor.rotation.y, "velocity": vector(actor.velocity), "sequence": binding.sequence}


## Validates a bounded pose's exact primitive fields before any replica state change.
func pose_valid(pose: Variant) -> bool:  # gdstyle:ignore=quality/max-returns
	if not pose is Dictionary or pose.size() != 8:
		return false

	for field: String in ["entity", "tick", "control", "durable", "sequence"]:
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
	super.rollback(participant)


## Completes body neutralization and clears buffers before S03 publishes closing state.
func clear() -> void:
	for actor: S03RActor in body_for_entity.values():
		actor.retire()
	body_for_entity.clear()
	pending_poses.clear()
	baseline_ticks.clear()
	super.clear()


## Encodes local vectors into the bounded primitive wire representation.
func vector(value: Vector3) -> Array[float]:
	return [value.x, value.y, value.z]
