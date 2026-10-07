class_name S02ActorMotion
extends CharacterBody3D
## Standalone foot-motion owner; consumes intent without reading devices or applying damage.

const MAX_STEP_SECONDS: float = 0.05

@export var forward_speed_mps: float = 5.0
@export var reverse_speed_mps: float = 3.0
@export var turn_speed_degrees: float = 180.0


## Advances one physics tick using bounded, finite facing-relative intent.
func step(move_axis: float, turn_axis: float, delta_seconds: float) -> void:
	if not is_finite(move_axis) or not is_finite(turn_axis):
		neutralize()
		return
	if not is_finite(delta_seconds) or delta_seconds <= 0.0:
		neutralize()
		return

	var step_seconds: float = minf(delta_seconds, MAX_STEP_SECONDS)
	var turn: float = clampf(turn_axis, -1.0, 1.0)
	var move: float = clampf(move_axis, -1.0, 1.0)
	rotation.y = wrapf(rotation.y - deg_to_rad(turn_speed_degrees) * turn * step_seconds,
		-PI, PI)
	var speed: float = forward_speed_mps if move >= 0.0 else reverse_speed_mps
	velocity = -global_basis.z * move * speed
	move_and_slide()


## Clears motion immediately on focus, local-menu or harness suspension.
func neutralize() -> void:
	velocity = Vector3.ZERO


## Returns the source-derived muzzle in the unsmoothed physics pose.
func muzzle_position() -> Vector3:
	return ($Sockets/Muzzle as Marker3D).global_position


## Exposes simulation pose for camera, query and independent outcome checks.
func motion_state() -> Dictionary:
	return { "position": global_position, "yaw": rotation.y, "velocity": velocity }
