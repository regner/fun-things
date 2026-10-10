class_name VehiclePrediction
extends RefCounted
## Owns bounded local vehicle replay and visual-only authoritative correction smoothing.

const HISTORY_CAPACITY: int = 120
const WIRE_QUANTIZATION_TOLERANCE_METRES: float = 0.015
const MAX_SMOOTH_CORRECTION_METRES: float = 0.5
const LARGE_CORRECTION_SNAP_METRES: float = 2.0
const CORRECTION_SMOOTH_SECONDS: float = 0.1

var _vehicle: VehicleMotion
var _history: Array[Dictionary] = []
var _dropped_through_sequence: int = 0
var _latest_sequence: int = 0
var _acknowledgement: int = 0
var _context: Dictionary = {}
var _last_correction_metres: float = 0.0
var _correction_samples: Array[float] = []
var _reconciliation_count: int = 0


## Binds one locally controlled car and clears state from any earlier binding.
func bind_vehicle(vehicle: VehicleMotion) -> bool:
	if vehicle == null or not is_instance_valid(vehicle) or not vehicle.is_inside_tree():
		return false
	if _vehicle == vehicle:
		_vehicle.configure_simulation(true)
		return true

	unbind_vehicle()
	_vehicle = vehicle
	_vehicle.configure_simulation(true)
	return true


## Drops local control, clears replay, and makes the former body passive.
func unbind_vehicle() -> void:
	var previous: VehicleMotion = _vehicle
	invalidate()
	if is_instance_valid(previous):
		previous.configure_simulation(false)
	_vehicle = null


## Applies one numbered input immediately through the shared replay step.
func predict(command: DriveCommand, delta_seconds: float) -> bool:
	if not is_instance_valid(_vehicle) or command == null:
		return false
	if command.sequence <= _latest_sequence:
		return false
	if not _vehicle.step(command, delta_seconds, VehicleMotion.StepMode.REPLAY):
		return false

	_latest_sequence = command.sequence
	_history.append({ "command": command, "delta": delta_seconds })
	if _history.size() > HISTORY_CAPACITY:
		var dropped: Dictionary = _history.pop_front()
		var dropped_command: DriveCommand = dropped.command
		_dropped_through_sequence = dropped_command.sequence
	return true


## Restores host motion and replays only retained unacknowledged movement frames.
func reconcile(authority_state: Dictionary, acknowledgement: int) -> Dictionary:
	if not is_instance_valid(_vehicle) or acknowledgement < _acknowledgement:
		return _failure(&"STALE_ACKNOWLEDGEMENT")
	if acknowledgement > _latest_sequence:
		return _failure(&"FUTURE_ACKNOWLEDGEMENT")

	var before_body_position: Vector3 = _vehicle.global_position
	var presentation: Node3D = _vehicle.get_node_or_null("PresentationAnchor") as Node3D
	var before_display: Transform3D = (
		presentation.global_transform if presentation != null else _vehicle.global_transform
	)
	_acknowledgement = acknowledgement
	if _drop_acknowledged(acknowledgement):
		return _install_exhausted(authority_state, before_body_position)
	if not _vehicle.restore_motion_state(authority_state):
		return _failure(&"MALFORMED_AUTHORITY")

	var replayed: int = _replay_history()
	if replayed < 0:
		return _failure(&"REPLAY_REJECTED")
	_apply_correction(
		authority_state,
		acknowledgement,
		before_body_position,
		before_display,
		presentation,
	)
	return {
		"ok": true,
		"history_exhausted": false,
		"replayed": replayed,
		"correction_metres": _last_correction_metres,
	}


## Clears history whenever entity, generation, life, control, or collision changes.
func update_context(
	entity_id: int,
	generation: int,
	life_revision: int,
	control_revision: int,
	collision_revision: int,
) -> bool:
	var next: Dictionary = {
		"entity_id": entity_id,
		"generation": generation,
		"life_revision": life_revision,
		"control_revision": control_revision,
		"collision_revision": collision_revision,
	}
	if next == _context:
		return false
	if not _context.is_empty():
		invalidate()
	_context = next
	return true


## Decays only the authored presentation anchor toward the collision body.
func tick_visual(delta_seconds: float) -> void:
	if not is_instance_valid(_vehicle) or delta_seconds <= 0.0:
		return
	var presentation: Node3D = _vehicle.get_node_or_null("PresentationAnchor") as Node3D
	if presentation == null:
		return

	var weight: float = minf(1.0, delta_seconds / CORRECTION_SMOOTH_SECONDS)
	presentation.global_transform = presentation.global_transform.interpolate_with(
		_vehicle.global_transform, weight
	)
	if presentation.global_position.distance_to(_vehicle.global_position) <= 0.001:
		presentation.transform = Transform3D.IDENTITY


## Clears replay, correction, and visual offsets at a nonincremental fence.
func invalidate() -> void:
	_history.clear()
	_dropped_through_sequence = 0
	_latest_sequence = 0
	_acknowledgement = 0
	_last_correction_metres = 0.0
	_correction_samples.clear()
	_reconciliation_count = 0
	_context.clear()
	_snap_presentation()


## Reports bounded history and raw correction measurements for acceptance receipts.
func diagnostics() -> Dictionary:
	return {
		"acknowledgement": _acknowledgement,
		"history_size": _history.size(),
		"last_correction_metres": _last_correction_metres,
		"p95_correction_metres": correction_p95_metres(),
		"reconciliation_count": _reconciliation_count,
	}


## Reports nearest-rank p95 across the bounded correction window.
func correction_p95_metres() -> float:
	if _correction_samples.is_empty():
		return 0.0
	var ordered: Array[float] = _correction_samples.duplicate()
	ordered.sort()
	return ordered[ceili(float(ordered.size()) * 0.95) - 1]


## Drops acknowledged history and detects an overflowed reconstruction prefix.
func _drop_acknowledged(acknowledgement: int) -> bool:
	if acknowledgement < _dropped_through_sequence:
		_history.clear()
		_dropped_through_sequence = 0
		_latest_sequence = acknowledgement
		return true

	while not _history.is_empty():
		var first: Dictionary = _history[0]
		var command: DriveCommand = first.command
		if command.sequence > acknowledgement:
			break
		_history.pop_front()
	return false


## Installs authority without replay when bounded history lost a required prefix.
func _install_exhausted(authority_state: Dictionary, before_position: Vector3) -> Dictionary:
	if not _vehicle.restore_motion_state(authority_state):
		return _failure(&"MALFORMED_AUTHORITY")
	_record_correction(before_position.distance_to(_vehicle.global_position))
	_snap_presentation()
	return {
		"ok": true,
		"history_exhausted": true,
		"replayed": 0,
		"correction_metres": _last_correction_metres,
	}


## Replays retained movement-only frames and rejects any changed shared-step contract.
func _replay_history() -> int:
	var replayed: int = 0
	for frame: Dictionary in _history:
		if not _vehicle.step(frame.command, frame.delta, VehicleMotion.StepMode.REPLAY):
			_history.clear()
			_snap_presentation()
			return -1
		replayed += 1
	return replayed


## Applies bounded visual correction while authoritative collision wins immediately.
func _apply_correction(
	authority_state: Dictionary,
	acknowledgement: int,
	before_position: Vector3,
	before_display: Transform3D,
	presentation: Node3D,
) -> void:
	_record_correction(before_position.distance_to(_vehicle.global_position))
	if _last_correction_metres > LARGE_CORRECTION_SNAP_METRES:
		_history.clear()
		_latest_sequence = acknowledgement
		_vehicle.restore_motion_state(authority_state)
		_snap_presentation()
	elif (
		presentation != null
		and _last_correction_metres > WIRE_QUANTIZATION_TOLERANCE_METRES
		and _last_correction_metres <= MAX_SMOOTH_CORRECTION_METRES
	):
		presentation.global_transform = before_display
	else:
		_snap_presentation()


## Retains only the bounded recent correction sample window.
func _record_correction(correction_metres: float) -> void:
	_reconciliation_count += 1
	_last_correction_metres = correction_metres
	_correction_samples.append(correction_metres)
	if _correction_samples.size() > HISTORY_CAPACITY:
		_correction_samples.pop_front()


## Removes visual offsets without changing the motion-owned body transform.
func _snap_presentation() -> void:
	if not is_instance_valid(_vehicle):
		return
	var presentation: Node3D = _vehicle.get_node_or_null("PresentationAnchor") as Node3D
	if presentation != null:
		presentation.transform = Transform3D.IDENTITY


## Returns one normalized reconciliation refusal.
func _failure(code: StringName) -> Dictionary:
	return { "ok": false, "failure": { "code": code } }
