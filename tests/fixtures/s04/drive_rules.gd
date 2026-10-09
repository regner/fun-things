class_name S04DriveRules
extends RefCounted
## One planar arcade handling rule for both bounded body candidates; no device/network reads.

const CAR_COLLISION_LAYER: int = 4
const CAR_COLLISION_MASK: int = 5
const ACCELERATION_MPS2: float = 12.0
const BRAKE_MPS2: float = 18.0
const HANDBRAKE_MPS2: float = 10.0
const COAST_MPS2: float = 4.0
const MAX_FORWARD_MPS: float = 20.0
const MAX_REVERSE_MPS: float = 6.0
const GRIP_PER_SECOND: float = 6.0
const SLIDE_GRIP_PER_SECOND: float = 1.0
const TURN_RAD_PER_SECOND: float = 1.5
const FULL_STEER_SPEED_MPS: float = 4.0


## Supplies fresh neutral intent so callers never share a mutable command.
static func neutral() -> Dictionary:
	return { "throttle": 0.0, "steer": 0.0, "brake": 0.0, "handbrake": false }


## Applies bounded acceleration, service/handbrake deceleration, lateral grip and speed-aware yaw.
static func advance(velocity: Vector3, yaw: float, command: Dictionary,
		delta: float, tuning: Resource = null) -> Dictionary:
	var forward: Vector3 = Vector3(-sin(yaw), 0.0, -cos(yaw))
	var right: Vector3 = Vector3(cos(yaw), 0.0, -sin(yaw))
	var speed: float = velocity.dot(forward)
	var lateral: float = velocity.dot(right)
	var throttle: float = command.throttle
	var braking: bool = command.brake > 0.0 or (speed * throttle < 0.0)
	if braking or command.handbrake:
		var deceleration_mps2: float = 0.0
		if command.handbrake:
			deceleration_mps2 = _value(
				tuning, &"handbrake_mps2", HANDBRAKE_MPS2
			)
		if braking:
			deceleration_mps2 = maxf(
				deceleration_mps2,
				_value(tuning, &"brake_mps2", BRAKE_MPS2)
			)

		speed = move_toward(speed, 0.0, deceleration_mps2 * delta)
	elif throttle != 0.0:
		speed = clampf(
			speed + throttle * _value(tuning, &"acceleration_mps2", ACCELERATION_MPS2)
			* delta,
			-_value(tuning, &"max_reverse_mps", MAX_REVERSE_MPS),
			_value(tuning, &"max_forward_mps", MAX_FORWARD_MPS)
		)
	else:
		speed = move_toward(
			speed, 0.0, _value(tuning, &"coast_mps2", COAST_MPS2) * delta
		)

	var grip: float = _value(
		tuning,
		&"slide_grip_per_second" if command.handbrake else &"grip_per_second",
		SLIDE_GRIP_PER_SECOND if command.handbrake else GRIP_PER_SECOND
	)
	lateral *= maxf(0.0, 1.0 - grip * delta)
	var yaw_rate: float = -command.steer * _value(
		tuning, &"turn_rad_per_second", TURN_RAD_PER_SECOND
	) * clampf(
		absf(speed) / _value(tuning, &"full_steer_speed_mps", FULL_STEER_SPEED_MPS),
		0.0,
		1.0
	)
	if speed < 0.0:
		yaw_rate = -yaw_rate

	return { "velocity": forward * speed + right * lateral, "yaw_rate": yaw_rate }


## Resolves optional standalone tuning without changing fixture defaults.
static func _value(tuning: Resource, property: StringName, fallback: float) -> float:
	return fallback if tuning == null else float(tuning.get(property))
