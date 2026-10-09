class_name S02MotionRules
extends RefCounted
## Pure foot-motion rule shared by standalone, authority and later prediction replay.

const SPEED_MPS: float = 5.0


## Returns one deterministic state from movement, aim and fire input without side effects.
static func advance(state: Dictionary, command: Dictionary) -> Dictionary:
	var previous_yaw: float = float(state.get("yaw", 0.0))
	var move: Variant = command.get("move")
	var aim_yaw: Variant = command.get("aim_yaw")
	var fire: Variant = command.get("fire")
	if not move is Vector2 or not aim_yaw is float or not fire is bool:
		return { "velocity": Vector3.ZERO, "yaw": previous_yaw, "fire": false,
			"valid": false }
	if not move.is_finite() or not is_finite(aim_yaw):
		return { "velocity": Vector3.ZERO, "yaw": previous_yaw, "fire": false,
			"valid": false }

	var bounded_move: Vector2 = move.limit_length(1.0)
	return {
		"velocity": Vector3(bounded_move.x, 0.0, bounded_move.y) * SPEED_MPS,
		"yaw": wrapf(aim_yaw, -PI, PI),
		"fire": fire,
		"valid": true,
	}
