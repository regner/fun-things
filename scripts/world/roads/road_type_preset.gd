class_name RoadTypePreset
extends Resource
## Owns immutable road-class defaults applied to Road Generator points and road semantics.

@export var preset_id: StringName
@export var lane_directions: Array[RoadPoint.LaneDir] = []
@export_range(0.1, 20.0, 0.1) var lane_width_m: float = 4.0
@export_range(0.0, 10.0, 0.1) var shoulder_width_left_m: float = 0.0
@export_range(0.0, 10.0, 0.1) var shoulder_width_right_m: float = 0.0
@export var gutter_profile_m: Vector2 = Vector2.ZERO
@export_range(0.0, 20.0, 0.1) var sidewalk_width_left_m: float = 0.0
@export_range(0.0, 20.0, 0.1) var sidewalk_width_right_m: float = 0.0
@export var curb_profile_id: StringName = &"standard"
@export_range(0.1, 100.0, 0.1) var speed_limit_mps: float = 10.0
@export var surface_material_id: StringName = &"road_default"
@export var sidewalk_material_id: StringName = &"sidewalk_default"
@export var street_light_asset_id: StringName
@export_range(0.0, 200.0, 0.1) var street_light_spacing_m: float = 0.0
@export var spawn_policy_id: StringName = &"standard"


## Returns whether all class defaults are finite, bounded, and usable by the adapter.
func is_valid() -> bool:
	if preset_id == &"" or lane_directions.is_empty():
		return false
	if not is_finite(lane_width_m) or lane_width_m <= 0.0:
		return false
	if not _valid_nonnegative_values():
		return false
	for direction: RoadPoint.LaneDir in lane_directions:
		if direction not in [RoadPoint.LaneDir.FORWARD, RoadPoint.LaneDir.REVERSE]:
			return false

	return true


## Checks finite nonnegative dimensions and semantic tuning.
func _valid_nonnegative_values() -> bool:
	var values: Array[float] = [
		shoulder_width_left_m,
		shoulder_width_right_m,
		sidewalk_width_left_m,
		sidewalk_width_right_m,
		street_light_spacing_m,
	]
	for value: float in values:
		if not is_finite(value) or value < 0.0:
			return false
	return (
		is_finite(gutter_profile_m.x)
		and is_finite(gutter_profile_m.y)
		and is_finite(speed_limit_mps)
		and speed_limit_mps > 0.0
	)
