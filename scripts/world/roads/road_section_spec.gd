class_name RoadSectionSpec
extends Resource
## Binds stable road and section identities to one preset without storing spline geometry.

enum TravelDirection {
	UNSET,
	TWO_WAY,
	FORWARD,
	REVERSE,
}
enum EndpointPolicy {
	CONNECTED,
	REVIEW,
	DEAD_END,
}

@export var road_id: StringName
@export var section_id: StringName
@export var source_route_name: String
@export var preset: RoadTypePreset
@export var travel_direction: TravelDirection = TravelDirection.TWO_WAY
@export var endpoint_policy: EndpointPolicy = EndpointPolicy.CONNECTED
@export var profile_id: StringName = &"standard"
@export_range(-1.0, 20.0, 0.1) var lane_width_override_m: float = -1.0
@export_range(-1.0, 10.0, 0.1) var shoulder_width_left_override_m: float = -1.0
@export_range(-1.0, 10.0, 0.1) var shoulder_width_right_override_m: float = -1.0
@export var gutter_profile_override_m: Vector2 = Vector2(INF, INF)
@export_range(-1.0, 20.0, 0.1) var sidewalk_width_left_override_m: float = -1.0
@export_range(-1.0, 20.0, 0.1) var sidewalk_width_right_override_m: float = -1.0
@export_range(-1.0, 100.0, 0.1) var speed_limit_override_mps: float = -1.0
@export var spawn_enabled: bool = true


## Returns the exact lane directions this section applies to each RoadPoint.
func expected_lane_directions() -> Array[RoadPoint.LaneDir]:
	if preset == null:
		return []
	if travel_direction == TravelDirection.FORWARD:
		return _filled_directions(RoadPoint.LaneDir.FORWARD)
	if travel_direction == TravelDirection.REVERSE:
		return _filled_directions(RoadPoint.LaneDir.REVERSE)
	if travel_direction == TravelDirection.TWO_WAY:
		return preset.lane_directions.duplicate()
	return []


## Returns the preset lane width or its explicitly authorized section value.
func expected_lane_width_m() -> float:
	if lane_width_override_m >= 0.0:
		return lane_width_override_m
	return preset.lane_width_m if preset != null else -1.0


## Returns the preset left shoulder or its explicitly authorized section value.
func expected_shoulder_left_m() -> float:
	if shoulder_width_left_override_m >= 0.0:
		return shoulder_width_left_override_m
	return preset.shoulder_width_left_m if preset != null else -1.0


## Returns the preset right shoulder or its explicitly authorized section value.
func expected_shoulder_right_m() -> float:
	if shoulder_width_right_override_m >= 0.0:
		return shoulder_width_right_override_m
	return preset.shoulder_width_right_m if preset != null else -1.0


## Returns the preset gutter profile or its explicitly authorized section value.
func expected_gutter_profile_m() -> Vector2:
	if gutter_profile_override_m.is_finite():
		return gutter_profile_override_m
	return preset.gutter_profile_m if preset != null else Vector2(INF, INF)


## Returns whether identifiers, preset, direction, and override declarations are valid.
func is_valid() -> bool:
	if road_id == &"" or section_id == &"" or source_route_name.is_empty():
		return false
	if preset == null or not preset.is_valid() or profile_id == &"":
		return false
	if travel_direction not in TravelDirection.values():
		return false
	if endpoint_policy not in EndpointPolicy.values():
		return false
	if travel_direction == TravelDirection.UNSET and preset.preset_id != &"service":
		return false
	return _override_values_are_finite()


## Builds an array matching the preset lane count for an explicit one-way section.
func _filled_directions(direction: RoadPoint.LaneDir) -> Array[RoadPoint.LaneDir]:
	var directions: Array[RoadPoint.LaneDir] = []
	for _lane: int in preset.lane_directions.size():
		directions.append(direction)
	return directions


## Rejects nonfinite scalar overrides while preserving -1 as the unset sentinel.
func _override_values_are_finite() -> bool:
	var scalar_values: Array[float] = [
		lane_width_override_m,
		shoulder_width_left_override_m,
		shoulder_width_right_override_m,
		sidewalk_width_left_override_m,
		sidewalk_width_right_override_m,
		speed_limit_override_mps,
	]
	for value: float in scalar_values:
		if not is_finite(value) or value < -1.0:
			return false
	return gutter_profile_override_m.is_finite() or gutter_profile_override_m == Vector2(INF, INF)
