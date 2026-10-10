class_name FootPrediction
extends RefCounted
## Owns bounded local foot replay and visual-only authoritative correction smoothing.

const HISTORY_CAPACITY: int = 120
const WIRE_QUANTIZATION_TOLERANCE_METRES: float = 0.015
const MAX_SMOOTH_CORRECTION_METRES: float = 0.5
const LARGE_CORRECTION_SNAP_METRES: float = 2.0
const CORRECTION_SMOOTH_SECONDS: float = 0.1

var _actor: ActorMotion
var _history: Array[Dictionary] = []
var _dropped_through_sequence: int = 0
var _latest_sequence: int = 0
var _acknowledgement: int = 0
var _context: Dictionary = {}
var _max_correction_metres: float = 0.0
var _last_correction_metres: float = 0.0
var _correction_samples: Array[float] = []
var _last_authority_position: Vector3 = Vector3.INF


## Binds one owned collision body while retaining no state from an earlier actor.
func bind_actor(actor: ActorMotion) -> bool:
	if actor == null or not is_instance_valid(actor) or not actor.is_inside_tree():
		return false
	if _actor == actor:
		return true

	invalidate()
	_actor = actor
	return true


## Applies one sampled command immediately through the shared replay motion step.
func predict(command: FootCommand, delta_seconds: float) -> bool:
	if not is_instance_valid(_actor) or command == null:
		return false
	if command.sequence <= _latest_sequence:
		return false
	if not _actor.step(command, delta_seconds, ActorMotion.StepMode.REPLAY):
		return false

	_latest_sequence = command.sequence
	_history.append({ "command": command, "delta": delta_seconds })
	if _history.size() > HISTORY_CAPACITY:
		var dropped: Dictionary = _history.pop_front()
		var dropped_command: FootCommand = dropped.command
		_dropped_through_sequence = dropped_command.sequence
	return true


## Reconciles one complete decoded authoritative movement sample.
func reconcile_motion(
	position: Vector3,
	velocity: Vector3,
	aim_yaw: float,
	grounded: bool,
	acknowledgement: int,
) -> Dictionary:
	return reconcile(
		{
			"position": position,
			"velocity": velocity,
			"aim_yaw": aim_yaw,
			"grounded": grounded,
		},
		acknowledgement,
	)


## Restores host motion, drops acknowledged frames, and replays only permitted motion.
func reconcile(authority_state: Dictionary, acknowledgement: int) -> Dictionary:
	if not is_instance_valid(_actor) or acknowledgement < _acknowledgement:
		return _failure(&"STALE_ACKNOWLEDGEMENT")
	if acknowledgement > _latest_sequence:
		return _failure(&"FUTURE_ACKNOWLEDGEMENT")

	var before_body_position: Vector3 = _actor.global_position
	var presentation: Node3D = _actor.get_node_or_null("PresentationAnchor") as Node3D
	var before_display: Transform3D = (
		presentation.global_transform if presentation != null else _actor.global_transform
	)
	_acknowledgement = acknowledgement
	if _drop_acknowledged(acknowledgement):
		return _install_exhausted(authority_state, before_body_position)
	if not _actor.restore_motion_state(authority_state):
		return _failure(&"MALFORMED_AUTHORITY")
	_last_authority_position = authority_state.position

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


## Drops acknowledged history and reports when an overflow removed a required prefix.
func _drop_acknowledged(acknowledgement: int) -> bool:
	if acknowledgement < _dropped_through_sequence:
		_history.clear()
		_dropped_through_sequence = 0
		_latest_sequence = acknowledgement
		return true

	while not _history.is_empty():
		var first: Dictionary = _history[0]
		var first_command: FootCommand = first.command
		if first_command.sequence > acknowledgement:
			break
		_history.pop_front()
	return false


## Installs authority without replay when bounded history cannot reconstruct the prefix.
func _install_exhausted(authority_state: Dictionary, before_body_position: Vector3) -> Dictionary:
	if not _actor.restore_motion_state(authority_state):
		return _failure(&"MALFORMED_AUTHORITY")
	_last_authority_position = authority_state.position
	_record_correction(before_body_position.distance_to(_actor.global_position))
	_snap_presentation()
	return {
		"ok": true,
		"history_exhausted": true,
		"replayed": 0,
		"correction_metres": _last_correction_metres,
	}


## Replays the retained movement-only frames and returns minus one on rule rejection.
func _replay_history() -> int:
	var replayed: int = 0
	for frame: Dictionary in _history:
		if not _actor.step(frame.command, frame.delta, ActorMotion.StepMode.REPLAY):
			_history.clear()
			_snap_presentation()
			return -1
		replayed += 1
	return replayed


## Applies the bounded visual correction or snaps a large authoritative mismatch.
func _apply_correction(
	authority_state: Dictionary,
	acknowledgement: int,
	before_body_position: Vector3,
	before_display: Transform3D,
	presentation: Node3D,
) -> void:
	_record_correction(before_body_position.distance_to(_actor.global_position))
	if _last_correction_metres > LARGE_CORRECTION_SNAP_METRES:
		_history.clear()
		_latest_sequence = acknowledgement
		_actor.restore_motion_state(authority_state)
		_snap_presentation()
	elif (
		presentation != null
		and _last_correction_metres > WIRE_QUANTIZATION_TOLERANCE_METRES
		and _last_correction_metres <= MAX_SMOOTH_CORRECTION_METRES
	):
		presentation.global_transform = before_display
	else:
		_snap_presentation()


## Retains bounded correction measurements for production diagnostics.
func _record_correction(correction_metres: float) -> void:
	_last_correction_metres = correction_metres
	_max_correction_metres = maxf(_max_correction_metres, correction_metres)
	_correction_samples.append(correction_metres)
	if _correction_samples.size() > HISTORY_CAPACITY:
		_correction_samples.pop_front()


## Decays only the authored presentation anchor toward the predicted collision body.
func tick_visual(delta_seconds: float) -> void:
	if not is_instance_valid(_actor) or delta_seconds <= 0.0:
		return
	var presentation: Node3D = _actor.get_node_or_null("PresentationAnchor") as Node3D
	if presentation == null:
		return

	var weight: float = minf(1.0, delta_seconds / CORRECTION_SMOOTH_SECONDS)
	presentation.global_transform = presentation.global_transform.interpolate_with(
		_actor.global_transform, weight
	)
	if presentation.global_position.distance_to(_actor.global_position) <= 0.001:
		presentation.transform = Transform3D.IDENTITY


## Clears history when any identity, life, control, or collision dependency changes.
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


## Clears all replay and visual correction state at lifecycle or teardown fences.
func invalidate() -> void:
	_history.clear()
	_dropped_through_sequence = 0
	_latest_sequence = 0
	_acknowledgement = 0
	_max_correction_metres = 0.0
	_last_correction_metres = 0.0
	_correction_samples.clear()
	_last_authority_position = Vector3.INF
	_context.clear()
	_snap_presentation()


## Reports bounded replay and correction measurements for integration diagnostics.
func diagnostics() -> Dictionary:
	return {
		"acknowledgement": acknowledgement(),
		"history_size": history_size(),
		"max_correction_metres": max_correction_metres(),
		"p95_correction_metres": correction_p95_metres(),
	}


## Reports the latest complete host position before local replay advances it.
func last_authority_position() -> Vector3:
	return _last_authority_position


## Reports the bounded number of commands eligible for replay.
func history_size() -> int:
	return _history.size()


## Reports the newest host consumed-or-superseded sequence.
func acknowledgement() -> int:
	return _acknowledgement


## Reports the largest collision-body correction observed for diagnostics and tests.
func max_correction_metres() -> float:
	return _max_correction_metres


## Reports the latest collision-body correction before presentation smoothing.
func last_correction_metres() -> float:
	return _last_correction_metres


## Reports nearest-rank p95 across the bounded recent correction window.
func correction_p95_metres() -> float:
	if _correction_samples.is_empty():
		return 0.0
	var ordered: Array[float] = _correction_samples.duplicate()
	ordered.sort()
	var index: int = ceili(float(ordered.size()) * 0.95) - 1
	return ordered[index]


## Removes visual offsets without changing the motion-owned body transform.
func _snap_presentation() -> void:
	if not is_instance_valid(_actor):
		return
	var presentation: Node3D = _actor.get_node_or_null("PresentationAnchor") as Node3D
	if presentation != null:
		presentation.transform = Transform3D.IDENTITY


## Returns a normalized reconciliation failure.
func _failure(code: StringName) -> Dictionary:
	return { "ok": false, "failure": { "code": code } }
