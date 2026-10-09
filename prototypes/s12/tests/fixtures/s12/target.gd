class_name S12Target
extends Node3D
## Deterministic rail target used for pedestrian- and car-speed hit-registration samples.

@export var target_id: String = ""
@export var speed_mps: float = 1.5
@export var hit_radius_m: float = 0.45
@export var rail_half_length_m: float = 8.0

var direction: float = 1.0


## Advance the authoritative rail motion by one fixed simulation step.
func step(delta: float) -> void:
	var next_x: float = position.x + direction * speed_mps * delta
	if absf(next_x) > rail_half_length_m:
		var overflow: float = absf(next_x) - rail_half_length_m
		direction *= -1.0
		next_x = signf(next_x) * (rail_half_length_m - overflow)

	position.x = next_x


## Return the immutable query values needed by the combat owner.
func state() -> Dictionary:
	return {
		"id": target_id,
		"position": global_position,
		"radius": hit_radius_m,
		"speed": speed_mps,
	}
