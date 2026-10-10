class_name VehicleReplicator
extends RefCounted
## Owns Match vehicle entities, drive admission, snapshots, prediction, and presentation.

const ENTITY_KIND_VEHICLE: int = 2
const PHASE_LIVE: int = 1
const INPUT_EPOCH: int = 1
const MAX_VEHICLES: int = 64
const MAX_IDENTITY_BYTES: int = 128
const REMOTE_EXTRAPOLATION_MSEC: int = 125
const REMOTE_BLEND_MSEC: int = 150
const VEHICLE_SCENES: Dictionary = {
	&"vehicle/latch_a": preload("res://scenes/entities/vehicles/vehicle_latch.tscn"),
	&"vehicle/crate_a": preload("res://scenes/entities/vehicles/vehicle_crate.tscn"),
	&"vehicle/sable_a": preload("res://scenes/entities/vehicles/vehicle_sable.tscn"),
}

var _runtime_entities: Node3D
var _authority: bool = false
var _records_by_id: Dictionary[int, Dictionary] = {}
var _entity_id_by_driver: Dictionary[int, int] = {}
var _queues_by_participant: Dictionary[int, VehicleInputQueue] = {}
var _prediction := VehiclePrediction.new()
var _remote_smoothers: Dictionary[int, RemoteMotionSmoother] = {}


## Configures initial host vehicles from authored parked-car anchors and Match EntityRefs.
func configure_authority(
	runtime_entities: Node3D,
	anchors: Array[Dictionary],
	tracker: EntityGenerationTracker,
) -> bool:
	if (
		_runtime_entities != null
		or runtime_entities == null
		or tracker == null
		or anchors.is_empty()
		or anchors.size() > MAX_VEHICLES
	):
		return false

	_runtime_entities = runtime_entities
	_authority = true
	for anchor: Dictionary in anchors:
		var definition_id: StringName = _definition_for_world_id(anchor.get("world_id", &""))
		var allocated: Dictionary = tracker.allocate()
		if definition_id == &"" or not allocated.get("ok", false):
			clear()
			return false
		var entity_ref: Dictionary = allocated.entity_ref
		var descriptor: Dictionary = {
			"id": int(entity_ref.id),
			"generation": int(entity_ref.generation),
			"definition_id": definition_id,
			"origin_world_id": StringName(anchor.world_id),
			"driver_participant_id": 0,
			"control_revision": 1,
		}
		var vehicle: VehicleMotion = _instantiate_vehicle(descriptor, anchor.transform, true)
		if vehicle == null:
			clear()
			return false
		_records_by_id[int(entity_ref.id)] = {
			"descriptor": descriptor,
			"vehicle": vehicle,
			"spawn_transform": anchor.transform,
		}
	return true


## Configures a client-side vehicle collection before reliable descriptors arrive.
func configure_replica(runtime_entities: Node3D) -> bool:
	if _runtime_entities != null or runtime_entities == null:
		return false
	_runtime_entities = runtime_entities
	_authority = false
	return true


## Installs one complete bounded reliable descriptor snapshot before movement rows.
func install_descriptors(rows: Array, local_participant_id: int) -> bool:
	if _runtime_entities == null or rows.size() > MAX_VEHICLES:
		return false
	var seen: Dictionary[int, bool] = {}
	for value: Variant in rows:
		if not _valid_descriptor(value):
			return false
		var descriptor: Dictionary = value
		if seen.has(int(descriptor.id)):
			return false
		seen[int(descriptor.id)] = true

	var retained_ids: Dictionary[int, bool] = {}
	_entity_id_by_driver.clear()
	for value: Variant in rows:
		var descriptor: Dictionary = value
		var entity_id: int = int(descriptor.id)
		retained_ids[entity_id] = true
		var record: Dictionary = _records_by_id.get(entity_id, {})
		if record.is_empty() or int(record.descriptor.generation) != int(descriptor.generation):
			_retire_record(entity_id)
			var vehicle: VehicleMotion = _instantiate_vehicle(
				descriptor, Transform3D.IDENTITY, false
			)
			if vehicle == null:
				return false
			record = {
				"descriptor": descriptor.duplicate(true),
				"vehicle": vehicle,
				"spawn_transform": Transform3D.IDENTITY,
			}
			_records_by_id[entity_id] = record
		else:
			record.descriptor = descriptor.duplicate(true)
		var driver_id: int = int(descriptor.driver_participant_id)
		if driver_id > 0:
			_entity_id_by_driver[driver_id] = entity_id

	for entity_id: int in _records_by_id.keys():
		if not retained_ids.has(entity_id):
			_retire_record(entity_id)
	_update_local_control(local_participant_id)
	return true


## Returns immutable reliable rows required before vehicle baseline movement.
func descriptor_rows() -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	var entity_ids: Array[int] = _records_by_id.keys()
	entity_ids.sort()
	for entity_id: int in entity_ids:
		rows.append((_records_by_id[entity_id].descriptor as Dictionary).duplicate(true))
	return rows


## Captures every current vehicle in the measured 2 cm movement-row layout.
func capture_rows() -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	var entity_ids: Array[int] = _records_by_id.keys()
	entity_ids.sort()
	for entity_id: int in entity_ids:
		var record: Dictionary = _records_by_id[entity_id]
		var descriptor: Dictionary = record.descriptor
		var vehicle: VehicleMotion = record.vehicle
		if not is_instance_valid(vehicle):
			continue
		var state: Dictionary = vehicle.motion_state()
		var position: Vector3 = state.position
		var velocity: Vector3 = state.velocity
		rows.append(
			{
				"id": descriptor.id,
				"generation": descriptor.generation,
				"kind": ENTITY_KIND_VEHICLE,
				"phase": PHASE_LIVE,
				"flags": 0,
				"x": position.x,
				"y": position.y,
				"z": position.z,
				"vx": velocity.x,
				"vy": velocity.y,
				"vz": velocity.z,
				"yaw": vehicle.rotation.y,
			}
		)
	return rows


## Assigns one host-side test driver until B1.2 replaces this seam with transactions.
func assign_driver_for_testing(participant_id: int, entity_id: int = 0) -> Dictionary:
	if not _authority or participant_id <= 0 or _records_by_id.is_empty():
		return { "ok": false }
	if entity_id == 0:
		var sorted_ids: Array[int] = _records_by_id.keys()
		sorted_ids.sort()
		entity_id = sorted_ids[0]
	if not _records_by_id.has(entity_id):
		return { "ok": false }

	release_driver(participant_id)
	var record: Dictionary = _records_by_id[entity_id]
	var descriptor: Dictionary = record.descriptor
	var previous_driver: int = int(descriptor.driver_participant_id)
	if previous_driver > 0:
		release_driver(previous_driver)
	descriptor.driver_participant_id = participant_id
	descriptor.control_revision = int(descriptor.control_revision) + 1
	_entity_id_by_driver[participant_id] = entity_id
	_queues_by_participant[participant_id] = VehicleInputQueue.new()
	return { "ok": true, "entity_ref": { "id": entity_id, "generation": descriptor.generation } }


## Releases one test binding and clears stale drive commands without transferring seats.
func release_driver(participant_id: int) -> void:
	var entity_id: int = int(_entity_id_by_driver.get(participant_id, 0))
	_entity_id_by_driver.erase(participant_id)
	_queues_by_participant.erase(participant_id)
	if not _records_by_id.has(entity_id):
		return
	var descriptor: Dictionary = _records_by_id[entity_id].descriptor
	descriptor.driver_participant_id = 0
	descriptor.control_revision = int(descriptor.control_revision) + 1


## Returns the current controlled vehicle fence for one sender-derived participant.
func binding_for_participant(participant_id: int) -> Dictionary:
	var entity_id: int = int(_entity_id_by_driver.get(participant_id, 0))
	if not _records_by_id.has(entity_id):
		return {}
	var descriptor: Dictionary = _records_by_id[entity_id].descriptor
	return {
		"id": descriptor.id,
		"generation": descriptor.generation,
		"control_revision": descriptor.control_revision,
	}


## Offers one already-decoded command to the participant's bounded host queue.
func offer_command(participant_id: int, decoded: Dictionary, receipt_msec: int) -> Dictionary:
	var queue: VehicleInputQueue = _queues_by_participant.get(participant_id)
	if queue == null or int(decoded.get("input_epoch", 0)) != INPUT_EPOCH:
		return { "accepted": false, "failure": &"STALE_COMMAND_CONTEXT" }
	var command: DriveCommand = decoded.get("command")
	if queue.sequence_exceeds_freshness_window(command.sequence):
		return { "accepted": false, "failure": &"SEQUENCE_WINDOW" }
	return { "accepted": queue.offer(command, receipt_msec) }


## Steps each assigned host car once using the same VehicleMotion authority path.
func step_authority(delta_seconds: float, now_msec: int, physics_tick: int) -> void:
	if not _authority:
		return
	for participant_id: int in _entity_id_by_driver:
		var entity_id: int = int(_entity_id_by_driver[participant_id])
		var record: Dictionary = _records_by_id.get(entity_id, {})
		var queue: VehicleInputQueue = _queues_by_participant.get(participant_id)
		if record.is_empty() or queue == null:
			continue
		var decision: Dictionary = queue.consume(now_msec)
		var command: DriveCommand = decision.command
		if command == null:
			command = DriveCommand.neutral(maxi(1, queue.acknowledgement()), physics_tick)
		(record.vehicle as VehicleMotion).step(
			command, delta_seconds, VehicleMotion.StepMode.AUTHORITY
		)


## Predicts one local command immediately through the same VehicleMotion step.
func predict_local(command: DriveCommand, delta_seconds: float) -> bool:
	return _prediction.predict(command, delta_seconds)


## Applies one state-store row to local prediction or passive remote smoothing.
func apply_replica_state(
	state: Dictionary,
	local_participant_id: int,
	acknowledged_sequence: int,
	now_msec: int,
) -> bool:
	var entity_id: int = int(state.get("id", 0))
	var record: Dictionary = _records_by_id.get(entity_id, {})
	if record.is_empty() or int(record.descriptor.generation) != int(state.generation):
		return false
	var vehicle: VehicleMotion = record.vehicle
	var position := Vector3(float(state.x), float(state.y), float(state.z))
	var velocity := Vector3(float(state.vx), float(state.vy), float(state.vz))
	var authority_state: Dictionary = {
		"position": position,
		"yaw": float(state.yaw),
		"velocity": velocity,
		"steer": 0.0,
		"handbrake": false,
		"yaw_rate": 0.0,
	}
	var local_entity_id: int = int(_entity_id_by_driver.get(local_participant_id, 0))
	if entity_id == local_entity_id:
		if not _prediction.bind_vehicle(vehicle):
			return false
		_prediction.update_context(
			entity_id,
			int(state.generation),
			1,
			int(record.descriptor.control_revision),
			1,
		)
		return _prediction.reconcile(authority_state, acknowledged_sequence).get("ok", false)

	vehicle.global_position = position
	vehicle.rotation.y = float(state.yaw)
	vehicle.velocity = velocity
	vehicle.configure_simulation(false)
	var smoother: RemoteMotionSmoother = _remote_smoothers.get(entity_id)
	if smoother == null:
		smoother = RemoteMotionSmoother.new(REMOTE_EXTRAPOLATION_MSEC, REMOTE_BLEND_MSEC)
		_remote_smoothers[entity_id] = smoother
	smoother.update_context(entity_id, int(state.generation), 1, 1, 1)
	smoother.push(
		{ "position": position, "velocity": velocity, "aim_yaw": float(state.yaw) },
		now_msec,
	)
	_apply_remote_display(vehicle, smoother.sample(now_msec))
	return true


## Updates local correction decay and remote extrapolate-hold-blend presentation.
func tick_presentation(delta_seconds: float, now_msec: int) -> void:
	_prediction.tick_visual(delta_seconds)
	for entity_id: int in _remote_smoothers:
		var record: Dictionary = _records_by_id.get(entity_id, {})
		if record.is_empty():
			continue
		_apply_remote_display(record.vehicle, _remote_smoothers[entity_id].sample(now_msec))


## Clears replay and interpolation at reset or lifecycle fences without retiring entities.
func invalidate_motion() -> void:
	_prediction.invalidate()
	for smoother: RemoteMotionSmoother in _remote_smoothers.values():
		smoother.clear()
	_remote_smoothers.clear()


## Reports one participant's host consumed-or-superseded drive watermark.
func acknowledgement(participant_id: int) -> int:
	var queue: VehicleInputQueue = _queues_by_participant.get(participant_id)
	return 0 if queue == null else queue.acknowledgement()


## Reports whether this owner has one current descriptor for an EntityRef ID.
func owns_entity(entity_id: int) -> bool:
	return _records_by_id.has(entity_id)


## Returns one current body for integration and moving-contact acceptance tests.
func vehicle_for_entity(entity_id: int) -> VehicleMotion:
	var record: Dictionary = _records_by_id.get(entity_id, {})
	return null if record.is_empty() else record.vehicle as VehicleMotion


## Returns the local prediction diagnostics without exposing mutable history.
func prediction_diagnostics() -> Dictionary:
	return _prediction.diagnostics()


## Restores authored host poses and clears temporary assignments at match reset.
func reset_authority() -> void:
	if not _authority:
		return
	_entity_id_by_driver.clear()
	_queues_by_participant.clear()
	for record: Dictionary in _records_by_id.values():
		var descriptor: Dictionary = record.descriptor
		descriptor.driver_participant_id = 0
		descriptor.control_revision = int(descriptor.control_revision) + 1
		var vehicle: VehicleMotion = record.vehicle
		vehicle.global_transform = record.spawn_transform
		vehicle.neutralize()


## Clears bounded prediction, queues, smoothers, and dynamic vehicle instances.
func clear() -> void:
	_prediction.invalidate()
	for smoother: RemoteMotionSmoother in _remote_smoothers.values():
		smoother.clear()
	_remote_smoothers.clear()
	_entity_id_by_driver.clear()
	_queues_by_participant.clear()
	for record: Dictionary in _records_by_id.values():
		var vehicle: VehicleMotion = record.vehicle
		if is_instance_valid(vehicle):
			vehicle.queue_free()
	_records_by_id.clear()


## Instantiates one approved saved vehicle off-tree with its simulation role preconfigured.
func _instantiate_vehicle(
	descriptor: Dictionary,
	spawn_transform: Transform3D,
	authority: bool,
) -> VehicleMotion:
	var scene: PackedScene = VEHICLE_SCENES.get(StringName(descriptor.definition_id))
	if scene == null:
		return null
	var vehicle: VehicleMotion = scene.instantiate() as VehicleMotion
	if vehicle == null:
		return null
	vehicle.name = "e_%d_g_%d" % [descriptor.id, descriptor.generation]
	vehicle.configure_simulation(authority)
	_runtime_entities.add_child(vehicle)
	vehicle.global_transform = spawn_transform
	return vehicle


## Updates local prediction ownership after a reliable descriptor transaction.
func _update_local_control(local_participant_id: int) -> void:
	var entity_id: int = int(_entity_id_by_driver.get(local_participant_id, 0))
	if entity_id == 0:
		_prediction.invalidate()
		return
	var record: Dictionary = _records_by_id[entity_id]
	var vehicle: VehicleMotion = record.vehicle
	_prediction.bind_vehicle(vehicle)
	_prediction.update_context(
		entity_id,
		int(record.descriptor.generation),
		1,
		int(record.descriptor.control_revision),
		1,
	)


## Applies remote display state only to the authored presentation anchor.
func _apply_remote_display(vehicle: VehicleMotion, display: Dictionary) -> void:
	if vehicle == null or display.is_empty():
		return
	var presentation: VehiclePresentation = vehicle.get_node_or_null(
		"PresentationAnchor"
	) as VehiclePresentation
	if presentation == null:
		return
	presentation.global_position = display.position
	presentation.global_rotation = Vector3(0.0, float(display.aim_yaw), 0.0)
	var forward := Vector3(-sin(float(display.aim_yaw)), 0.0, -cos(float(display.aim_yaw)))
	presentation.apply_motion(
		{
			"steer": 0.0,
			"forward_speed_mps": (display.velocity as Vector3).dot(forward),
		},
		0.0,
	)


## Retires one replica and all presentation state tied to its old generation.
func _retire_record(entity_id: int) -> void:
	var record: Dictionary = _records_by_id.get(entity_id, {})
	if not record.is_empty():
		var vehicle: VehicleMotion = record.vehicle
		if is_instance_valid(vehicle):
			vehicle.queue_free()
	_records_by_id.erase(entity_id)
	var smoother: RemoteMotionSmoother = _remote_smoothers.get(entity_id)
	if smoother != null:
		smoother.clear()
	_remote_smoothers.erase(entity_id)


## Validates a bounded reliable vehicle descriptor before any scene is instantiated.
func _valid_descriptor(value: Variant) -> bool:
	if not value is Dictionary:
		return false
	var descriptor: Dictionary = value
	if descriptor.size() != 6 or not ReplicationIdentity.has_valid_entity_ref_fields(descriptor):
		return false
	if not descriptor.has_all(
		["definition_id", "origin_world_id", "driver_participant_id", "control_revision"]
	):
		return false
	var definition_id: Variant = descriptor.definition_id
	var origin_world_id: Variant = descriptor.origin_world_id
	return (
		(definition_id is String or definition_id is StringName)
		and VEHICLE_SCENES.has(StringName(definition_id))
		and String(definition_id).to_utf8_buffer().size() <= MAX_IDENTITY_BYTES
		and (origin_world_id is String or origin_world_id is StringName)
		and not String(origin_world_id).is_empty()
		and String(origin_world_id).to_utf8_buffer().size() <= MAX_IDENTITY_BYTES
		and descriptor.driver_participant_id is int
		and int(descriptor.driver_participant_id) >= 0
		and descriptor.control_revision is int
		and int(descriptor.control_revision) > 0
	)


## Maps the three authored parking identities to their delivered saved vehicle scenes.
func _definition_for_world_id(world_id: Variant) -> StringName:
	var identity := String(world_id)
	if "latch" in identity:
		return &"vehicle/latch_a"
	if "crate" in identity:
		return &"vehicle/crate_a"
	if "sable" in identity:
		return &"vehicle/sable_a"
	return &""
