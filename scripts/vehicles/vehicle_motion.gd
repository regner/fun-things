class_name VehicleMotion
extends CharacterBody3D
## Owns planar car pose, velocity, handling telemetry, and static-world collision.

# Ported deliberately from the accepted S04 drive rule and decision-29 handbrake fixes.
enum StepMode {
	AUTHORITY,
	REPLAY,
}

const VEHICLE_COLLISION_LAYER: int = 4
const VEHICLE_COLLISION_MASK: int = 5
const REVERSE_YAW_FLIP_MPS: float = 0.05

@export var tuning: VehicleTuning

var simulation_enabled: bool = true
var _last_steer: float = 0.0
var _last_handbrake: bool = false
var _yaw_rate: float = 0.0

@onready var _presentation: VehiclePresentation = get_node_or_null(
	"PresentationAnchor"
) as VehiclePresentation


## Applies one validated command through the shared authority/replay handling step.
func step(command: DriveCommand, delta_seconds: float, mode: StepMode) -> bool:
	if not simulation_enabled or not _can_step(command, delta_seconds, mode):
		neutralize()
		return false

	var next: Dictionary = _advance(velocity, rotation.y, command, delta_seconds, tuning)
	_yaw_rate = next.yaw_rate
	rotation.y = wrapf(rotation.y + _yaw_rate * delta_seconds, -PI, PI)
	velocity = next.velocity
	move_and_slide()
	velocity = get_real_velocity()
	velocity.y = 0.0
	_last_steer = command.steer
	_last_handbrake = command.handbrake
	_update_presentation(delta_seconds)
	return true


## Clears held motion immediately for invalidation, reset, or control transfer.
func neutralize() -> void:
	velocity = Vector3.ZERO
	_last_steer = 0.0
	_last_handbrake = false
	_yaw_rate = 0.0
	_update_presentation(0.0)


## Enables authoritative movement or makes a replica/inactive dev car physically passive.
func configure_simulation(enabled: bool) -> void:
	simulation_enabled = enabled
	collision_layer = VEHICLE_COLLISION_LAYER if enabled else 0
	collision_mask = VEHICLE_COLLISION_MASK if enabled else 0
	if not enabled:
		neutralize()


## Exposes complete motion-owned state for snapshots, replay, AI, and presentation.
func motion_state() -> Dictionary:
	var forward := Vector3(-sin(rotation.y), 0.0, -cos(rotation.y))
	return {
		"position": global_position,
		"yaw": rotation.y,
		"velocity": velocity,
		"forward_speed_mps": velocity.dot(forward),
		"steer": _last_steer,
		"handbrake": _last_handbrake,
		"yaw_rate": _yaw_rate,
	}


## Validates fixed-step and tuning boundaries before any simulation state can change.
func _can_step(command: DriveCommand, delta_seconds: float, mode: StepMode) -> bool:
	if command == null or not command.is_valid() or tuning == null or not tuning.is_valid():
		return false
	var active_fixed_delta := 1.0 / float(Engine.physics_ticks_per_second)
	if not is_finite(delta_seconds) or not is_equal_approx(delta_seconds, active_fixed_delta):
		return false
	return mode == StepMode.AUTHORITY or mode == StepMode.REPLAY


## Applies acceleration, full-vector handbrake braking, grip, caps, and speed-aware yaw.
static func _advance(  # gdstyle:ignore=quality/max-function-length,quality/max-local-variables
	current_velocity: Vector3,
	yaw: float,
	command: DriveCommand,
	delta_seconds: float,
	active_tuning: VehicleTuning
) -> Dictionary:
	var forward := Vector3(-sin(yaw), 0.0, -cos(yaw))
	var right := Vector3(cos(yaw), 0.0, -sin(yaw))
	var forward_speed: float = current_velocity.dot(forward)
	var lateral_speed: float = current_velocity.dot(right)
	var planar_velocity: Vector3 = forward * forward_speed + right * lateral_speed
	var opposing_throttle: bool = forward_speed * command.throttle < 0.0

	if command.handbrake:
		planar_velocity = _apply_handbrake(
			planar_velocity, command.brake, opposing_throttle, delta_seconds, active_tuning
		)
		forward_speed = planar_velocity.dot(forward)
		lateral_speed = planar_velocity.dot(right)
	elif command.brake > 0.0 or opposing_throttle:
		forward_speed = move_toward(
			forward_speed, 0.0, active_tuning.brake_mps2 * delta_seconds
		)
	elif not is_zero_approx(command.throttle):
		forward_speed = clampf(
			forward_speed + command.throttle * active_tuning.acceleration_mps2 * delta_seconds,
			-active_tuning.max_reverse_mps,
			active_tuning.max_forward_mps
		)
	else:
		forward_speed = move_toward(
			forward_speed, 0.0, active_tuning.coast_mps2 * delta_seconds
		)

	var grip: float = (
		active_tuning.handbrake_side_grip_per_second
		if command.handbrake
		else active_tuning.grip_per_second
	)
	var handbrake_target_speed: float = planar_velocity.length()
	lateral_speed *= maxf(0.0, 1.0 - grip * delta_seconds)
	planar_velocity = forward * forward_speed + right * lateral_speed
	if command.handbrake and not planar_velocity.is_zero_approx():
		# Grip rotates travel; braking alone owns full-vector speed loss.
		planar_velocity = planar_velocity.normalized() * handbrake_target_speed
		forward_speed = planar_velocity.dot(forward)

	var authority_speed: float = (
		planar_velocity.length() if command.handbrake else absf(forward_speed)
	)
	var yaw_rate: float = (
		-command.steer
		* active_tuning.turn_rate_rad_per_second
		* clampf(authority_speed / active_tuning.full_steer_speed_mps, 0.0, 1.0)
	)
	var reverse_threshold: float = REVERSE_YAW_FLIP_MPS if command.handbrake else 0.0
	if forward_speed < -reverse_threshold:
		yaw_rate = -yaw_rate

	return { "velocity": planar_velocity, "yaw_rate": yaw_rate }


## Brakes the complete planar vector without changing direction or crossing zero.
static func _apply_handbrake(
	planar_velocity: Vector3,
	brake: float,
	opposing_throttle: bool,
	delta_seconds: float,
	active_tuning: VehicleTuning
) -> Vector3:
	var deceleration: float = active_tuning.handbrake_brake_mps2
	if brake > 0.0 or opposing_throttle:
		deceleration = maxf(deceleration, active_tuning.brake_mps2)
	var target_speed := move_toward(
		planar_velocity.length(), 0.0, deceleration * delta_seconds
	)
	if target_speed <= 0.0:
		return Vector3.ZERO
	return planar_velocity.normalized() * target_speed


## Supplies motion telemetry to the optional authored visual anchor only.
func _update_presentation(delta_seconds: float) -> void:
	if _presentation != null:
		_presentation.apply_motion(motion_state(), delta_seconds)
