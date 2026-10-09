extends "res://scenes/effects/weapon_effects/effect.gd"
## Instant cosmetic span. Endpoints are supplied by presentation, never resolved as hits here.

const MAX_LENGTH_METRES: float = 45.0
const MIN_LENGTH_METRES: float = 0.001
const PARALLEL_UP_THRESHOLD: float = 0.99


## Configure an idle span in its unit-scale parent's space, including before tree entry.
func configure_segment(from_m: Vector3, to_m: Vector3) -> bool:
	if is_active() or not from_m.is_finite() or not to_m.is_finite():
		return false

	var direction: Vector3 = to_m - from_m
	var length_m: float = direction.length()
	if not is_finite(length_m) or length_m < MIN_LENGTH_METRES or length_m > MAX_LENGTH_METRES:
		return false

	direction /= length_m
	var up: Vector3 = Vector3.UP
	if absf(direction.dot(up)) > PARALLEL_UP_THRESHOLD:
		up = Vector3.RIGHT

	transform = Transform3D(
		Basis.looking_at(direction, up) * Basis.from_scale(Vector3(1.0, 1.0, length_m)), from_m
	)
	return true
