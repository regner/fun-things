class_name AssetScaleClearanceProbe
extends CharacterBody3D
## Test-only actor envelope used by delivered-asset scale and clearance checks.

const SPEED_MPS: float = 5.0


## Advances one bounded movement step without device, combat, or network behavior.
func step(command: Dictionary, delta_seconds: float) -> void:
	if not is_finite(delta_seconds) or delta_seconds <= 0.0:
		neutralize()
		return

	var move_value: Variant = command.get("move")
	var aim_value: Variant = command.get("aim_yaw")
	if not move_value is Vector2 or not aim_value is float:
		neutralize()
		return

	var move: Vector2 = move_value
	var aim_yaw: float = aim_value
	if not move.is_finite() or not is_finite(aim_yaw):
		neutralize()
		return

	var bounded_move: Vector2 = move.limit_length(1.0)
	velocity = Vector3(bounded_move.x, 0.0, bounded_move.y) * SPEED_MPS
	rotation.y = wrapf(aim_yaw, -PI, PI)
	move_and_slide()


## Clears movement between independent fixture cases.
func neutralize() -> void:
	velocity = Vector3.ZERO


## Returns the authored query origin in the probe body's unsmoothed pose.
func muzzle_position() -> Vector3:
	return ($Sockets/Muzzle as Marker3D).global_position
