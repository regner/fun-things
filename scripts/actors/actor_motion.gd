class_name ActorMotion
extends CharacterBody3D
## Owns foot pose, planar velocity, facing, and static-world collision for one actor.

enum StepMode {
	AUTHORITY,
	REPLAY,
}

const SPEED_MPS: float = 5.0
const GRAVITY_MPS_SQUARED: float = 9.8
const FLOOR_SNAP_LENGTH_M: float = 0.25
const FLOOR_MAX_ANGLE_DEGREES: float = 45.0

@onready var _presentation: PlayerMotionPresentation = get_node_or_null(
	"PresentationAnchor"
) as PlayerMotionPresentation


## Configures the shared grounded-body slope and downward-following contract.
func _ready() -> void:
	motion_mode = CharacterBody3D.MOTION_MODE_GROUNDED
	floor_snap_length = FLOOR_SNAP_LENGTH_M
	floor_max_angle = deg_to_rad(FLOOR_MAX_ANGLE_DEGREES)


## Applies one command only when its delta matches the active fixed physics step.
func step(command: FootCommand, delta_seconds: float, mode: StepMode) -> bool:
	if command == null or not command.is_valid():
		neutralize()
		return false
	var active_fixed_delta := 1.0 / float(Engine.physics_ticks_per_second)
	if not is_finite(delta_seconds) or not is_equal_approx(delta_seconds, active_fixed_delta):
		neutralize()
		return false
	if mode != StepMode.AUTHORITY and mode != StepMode.REPLAY:
		neutralize()
		return false

	velocity.x = command.move.x * SPEED_MPS
	velocity.z = command.move.y * SPEED_MPS
	velocity.y = 0.0 if is_on_floor() else velocity.y - GRAVITY_MPS_SQUARED * delta_seconds
	rotation.y = command.aim_yaw
	move_and_slide()
	_update_presentation()
	return true


## Clears held movement immediately without changing the actor's retained facing.
func neutralize() -> void:
	velocity = Vector3.ZERO
	_update_presentation()


## Exposes complete motion-owned state for snapshots, replay, and presentation consumers.
func motion_state() -> Dictionary:
	return {
		"position": global_position,
		"velocity": velocity,
		"aim_yaw": rotation.y,
	}


## Calls the optional authored presentation child without moving gameplay collision.
func _update_presentation() -> void:
	if _presentation != null:
		_presentation.apply_motion(velocity, rotation.y)
