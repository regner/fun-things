class_name S02MotionRules
extends RefCounted
## Pure foot-motion rule shared by standalone, authority and later prediction replay.

const SPEED_MPS: float = 5.0


## Returns one deterministic velocity/facing state from a bounded world-relative command.
static func advance(state: Dictionary, move: Vector2, aim_yaw: float) -> Dictionary:
	var previous_yaw: float = float(state.get("yaw", 0.0))
	if not move.is_finite() or not is_finite(aim_yaw):
		return { "velocity": Vector3.ZERO, "yaw": previous_yaw, "valid": false }

	var bounded_move: Vector2 = move.limit_length(1.0)
	return {
		"velocity": Vector3(bounded_move.x, 0.0, bounded_move.y) * SPEED_MPS,
		"yaw": wrapf(aim_yaw, -PI, PI),
		"valid": true,
	}
