class_name ActorMotion
extends CharacterBody3D
## Owns foot pose, planar velocity, facing, and static-world collision for one actor.

enum StepMode {
	AUTHORITY,
	REPLAY,
}

const SPEED_MPS: float = 5.0

@onready var _presentation: PlayerMotionPresentation = get_node_or_null(
	"PresentationAnchor"
) as PlayerMotionPresentation


## Applies one fixed command through the identical authority or permitted replay rule.
func step(command: FootCommand, delta_seconds: float, mode: StepMode) -> bool:
	if command == null or not command.is_valid():
		neutralize()
		return false
	if not is_finite(delta_seconds) or delta_seconds <= 0.0:
		neutralize()
		return false
	if mode != StepMode.AUTHORITY and mode != StepMode.REPLAY:
		neutralize()
		return false

	velocity = Vector3(command.move.x, 0.0, command.move.y) * SPEED_MPS
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
