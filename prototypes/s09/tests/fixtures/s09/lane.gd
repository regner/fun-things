class_name S09Lane
extends Node3D
## Saved lane controls for one closed directed route; runtime sampling never changes placement.

const SAMPLE_SPACING_M: float = 0.5

@export var world_id: StringName
@export var replacement_for: StringName
@export var controls: PackedVector3Array


## Validates the bounded authored controls before traffic admission.
func is_valid() -> bool:
	if world_id == &"" or controls.size() < 4 or controls.size() > 32:
		return false
	for point: Vector3 in controls:
		if not point.is_finite():
			return false

	return true


## Samples the closed control polygon at a fixed interval for deterministic route queries.
func sampled_points() -> PackedVector3Array:
	var result: PackedVector3Array = []
	if not is_valid():
		return result

	for index: int in controls.size():
		var start: Vector3 = global_transform * controls[index]
		var finish: Vector3 = global_transform * controls[(index + 1) % controls.size()]
		var length: float = start.distance_to(finish)
		var steps: int = maxi(1, ceili(length / SAMPLE_SPACING_M))
		for step: int in steps:
			result.append(start.lerp(finish, float(step) / float(steps)))

	return result
