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
const REVERSE_YAW_FLIP_MPS: float = 0.05


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
	var planar_velocity: Vector3 = forward * speed + right * lateral
	var braking: bool = command.brake > 0.0 or (speed * command.throttle < 0.0)
	if command.handbrake:
		planar_velocity = _apply_handbrake(
			planar_velocity, braking, delta, tuning
		)
		speed = planar_velocity.dot(forward)
		lateral = planar_velocity.dot(right)
	elif braking:
		speed = move_toward(
			speed, 0.0, _value(tuning, &"brake_mps2", BRAKE_MPS2) * delta
		)
	elif command.throttle != 0.0:
		speed = clampf(
			speed + command.throttle
			* _value(tuning, &"acceleration_mps2", ACCELERATION_MPS2)
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
	var handbrake_target_speed: float = planar_velocity.length()
	lateral *= maxf(0.0, 1.0 - grip * delta)
	planar_velocity = forward * speed + right * lateral
	if command.handbrake and not planar_velocity.is_zero_approx():
		# Side grip changes travel direction; selected brake deceleration owns speed scrub.
		planar_velocity = planar_velocity.normalized() * handbrake_target_speed
		speed = planar_velocity.dot(forward)

	var yaw_rate: float = _yaw_rate(planar_velocity, speed, command.steer, tuning)
	return { "velocity": planar_velocity, "yaw_rate": yaw_rate }


## Scales steering by travel speed while requiring meaningful reverse motion to flip direction.
static func _yaw_rate(planar_velocity: Vector3, forward_speed: float,
		steer: float, tuning: Resource) -> float:
	var yaw_rate: float = -steer * _value(
		tuning, &"turn_rad_per_second", TURN_RAD_PER_SECOND
	) * clampf(
		planar_velocity.length()
		/ _value(tuning, &"full_steer_speed_mps", FULL_STEER_SPEED_MPS),
		0.0,
		1.0
	)
	# A meaningful reverse component avoids yaw-direction jitter while rotating through sideways.
	return -yaw_rate if forward_speed < -REVERSE_YAW_FLIP_MPS else yaw_rate


## Brakes the complete planar vector without changing its travel direction or crossing zero.
static func _apply_handbrake(planar_velocity: Vector3, service_braking: bool,
		delta: float, tuning: Resource) -> Vector3:
	var deceleration_mps2: float = _value(
		tuning, &"handbrake_mps2", HANDBRAKE_MPS2
	)
	if service_braking:
		deceleration_mps2 = maxf(
			deceleration_mps2,
			_value(tuning, &"brake_mps2", BRAKE_MPS2)
		)

	var target_speed: float = move_toward(
		planar_velocity.length(), 0.0, deceleration_mps2 * delta
	)
	return (
		planar_velocity.normalized() * target_speed
		if target_speed > 0.0
		else Vector3.ZERO
	)


## Resolves optional standalone tuning without changing fixture defaults.
static func _value(tuning: Resource, property: StringName, fallback: float) -> float:
	return fallback if tuning == null else float(tuning.get(property))
