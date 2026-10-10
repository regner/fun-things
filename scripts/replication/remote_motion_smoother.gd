class_name RemoteMotionSmoother
extends RefCounted
## Extrapolates, holds, then blends remote presentation without moving replica physics.

var _extrapolation_msec: int
var _blend_msec: int
var _context: Dictionary = {}
var _latest: Dictionary = {}
var _received_msec: int = 0
var _blend_started_msec: int = 0
var _blend_from: Dictionary = {}


## Configures the bounded extrapolation and authority blend durations.
func _init(extrapolation_msec: int = 125, blend_msec: int = 100) -> void:
	_extrapolation_msec = maxi(0, extrapolation_msec)
	_blend_msec = maxi(1, blend_msec)


## Installs one newer authority sample and starts a continuous blend from current display.
func push(state: Dictionary, receipt_msec: int) -> bool:
	if not _valid_state(state) or receipt_msec < 0:
		return false
	if _latest.is_empty():
		_latest = state.duplicate(true)
		_received_msec = receipt_msec
		_blend_started_msec = receipt_msec - _blend_msec
		_blend_from = state.duplicate(true)
		return true

	_blend_from = sample(receipt_msec)
	_latest = state.duplicate(true)
	_received_msec = receipt_msec
	_blend_started_msec = receipt_msec
	return true


## Returns the display pose after bounded extrapolation, hold, and authority blending.
func sample(now_msec: int) -> Dictionary:
	if _latest.is_empty():
		return {}
	var target: Dictionary = _extrapolated(now_msec)
	var elapsed_msec: int = maxi(0, now_msec - _blend_started_msec)
	if elapsed_msec >= _blend_msec:
		return target

	var weight: float = float(elapsed_msec) / float(_blend_msec)
	return {
		"position": (_blend_from.position as Vector3).lerp(target.position as Vector3, weight),
		"velocity": target.velocity,
		"aim_yaw": lerp_angle(float(_blend_from.aim_yaw), float(target.aim_yaw), weight),
	}


## Clears held motion when an entity generation or durable dependency changes.
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
	_latest.clear()
	_blend_from.clear()
	_context = next
	return true


## Clears every retained sample at removal, reset, or teardown.
func clear() -> void:
	_context.clear()
	_latest.clear()
	_blend_from.clear()
	_received_msec = 0
	_blend_started_msec = 0


## Projects only through the configured age, then holds the last permitted position.
func _extrapolated(now_msec: int) -> Dictionary:
	var age_msec: int = clampi(now_msec - _received_msec, 0, _extrapolation_msec)
	var position: Vector3 = _latest.position
	position += (_latest.velocity as Vector3) * float(age_msec) / 1000.0
	return {
		"position": position,
		"velocity": _latest.velocity,
		"aim_yaw": _latest.aim_yaw,
	}


## Accepts only complete finite presentation state owned by authoritative motion.
func _valid_state(state: Dictionary) -> bool:
	return (
		state.size() == 3
		and state.has("position")
		and state.position is Vector3
		and (state.position as Vector3).is_finite()
		and state.has("velocity")
		and state.velocity is Vector3
		and (state.velocity as Vector3).is_finite()
		and state.has("aim_yaw")
		and (state.aim_yaw is float or state.aim_yaw is int)
		and is_finite(float(state.aim_yaw))
	)
