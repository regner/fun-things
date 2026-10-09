class_name S02ActorMotion
extends CharacterBody3D
## Standalone foot-motion owner; consumes commands without reading devices or applying damage.


## Advances one physics tick using shared world-relative movement and snap-facing rules.
func step(move: Vector2, aim_yaw: float, delta_seconds: float) -> void:
	if not is_finite(delta_seconds) or delta_seconds <= 0.0:
		neutralize()
		return

	var next: Dictionary = S02MotionRules.advance(motion_state(), move, aim_yaw)
	velocity = next.velocity
	if next.valid:
		rotation.y = next.yaw
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
