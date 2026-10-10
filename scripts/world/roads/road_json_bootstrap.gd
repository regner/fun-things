class_name RoadJsonBootstrap
extends RefCounted
## Converts the frozen greybox JSON into a transient editor import plan for addon splines.

const MAX_ROUTES: int = 256
const MAX_POINTS_PER_ROUTE: int = 4096
const BRIDGE_ROUTE_NAME: String = "Harbour bridge"
const MAP_ORIGIN_X: float = 630.0
const MAP_ORIGIN_Y: float = 355.0


## Reads bounded route records while requiring unresolved one-way and bridge decisions.
static func load_plan(
	path: String,
	catalog: RoadSourceCatalog,
	service_directions: Dictionary,
	bridge_profile_id: StringName,
) -> Dictionary:
	var source_result: Dictionary = _load_source_routes(path, catalog)
	if not source_result.ok:
		return source_result
	var errors: Array[String] = []
	var records: Array[Dictionary] = []
	for route_value: Variant in source_result.routes:
		var record: Dictionary = _route_record(
			route_value, catalog, service_directions, bridge_profile_id, errors
		)
		if not record.is_empty():
			records.append(record)
	if records.size() != catalog.sections.size():
		errors.append("bootstrap routes do not map one-to-one to catalog sections")
	if not errors.is_empty():
		return { "ok": false, "errors": errors }
	return {
		"ok": true,
		"source_revision": catalog.source_revision,
		"source_sha256": catalog.bootstrap_source_sha256,
		"routes": records,
	}


## Converts one checked route into stable identities and Godot-space point positions.
static func _route_record(
	value: Variant,
	catalog: RoadSourceCatalog,
	service_directions: Dictionary,
	bridge_profile_id: StringName,
	errors: Array[String],
) -> Dictionary:
	if not value is Dictionary:
		errors.append("bootstrap route must be a dictionary")
		return {}
	var route: Dictionary = value
	var name_value: Variant = route.get("name")
	var kind_value: Variant = route.get("kind")
	var points_value: Variant = route.get("points")
	if not name_value is String or not kind_value is String or not points_value is Array:
		errors.append("bootstrap route has invalid name, kind, or points fields")
		return {}
	var spec: RoadSectionSpec = catalog.section_for_source_route(name_value)
	if spec == null or String(spec.preset.preset_id) != kind_value:
		errors.append("bootstrap route %s does not match a catalog section" % name_value)
		return {}
	if points_value.size() < 2 or points_value.size() > MAX_POINTS_PER_ROUTE:
		errors.append("bootstrap route %s has an invalid point count" % name_value)
		return {}
	var direction: int = _resolved_direction(spec, service_directions)
	if direction == RoadSectionSpec.TravelDirection.UNSET:
		errors.append("service route %s requires an explicit one-way direction" % name_value)
	if name_value == BRIDGE_ROUTE_NAME and bridge_profile_id != spec.profile_id:
		errors.append("Harbour bridge requires its catalog structural profile")

	var points_world := PackedVector3Array()
	var point_ids: Array[StringName] = []
	for index: int in points_value.size():
		var source_point: Variant = points_value[index]
		if not _valid_source_point(source_point):
			errors.append("bootstrap route %s has a nonfinite point" % name_value)
			return {}
		var position := Vector3(
			float(source_point[0]) - MAP_ORIGIN_X,
			0.0,
			float(source_point[1]) - MAP_ORIGIN_Y,
		)
		points_world.append(position)
		point_ids.append(StringName("%s/point_%04d" % [spec.road_id, index + 1]))
	return {
		"road_id": spec.road_id,
		"section_id": spec.section_id,
		"preset_id": spec.preset.preset_id,
		"travel_direction": direction,
		"endpoint_policy": spec.endpoint_policy,
		"profile_id": spec.profile_id,
		"points_world": points_world,
		"point_ids": point_ids,
	}


## Loads the bounded source route array after catalog and provenance checks.
static func _load_source_routes(path: String, catalog: RoadSourceCatalog) -> Dictionary:
	if catalog == null or not catalog.validate_source().ok:
		return _failure("road source catalog is invalid")
	if (
		not FileAccess.file_exists(path)
		or FileAccess.get_sha256(path) != catalog.bootstrap_source_sha256
	):
		return _failure("bootstrap JSON is missing or does not match catalog provenance")
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary:
		return _failure("bootstrap JSON root must be a dictionary")
	var routes_value: Variant = parsed.get("routes")
	if not routes_value is Array or routes_value.is_empty():
		return _failure("bootstrap JSON routes must be a nonempty array")
	if routes_value.size() > MAX_ROUTES:
		return _failure("bootstrap JSON route count exceeds the authoring bound")
	return { "ok": true, "routes": routes_value }


## Resolves service direction only from the explicit world-integrator input.
static func _resolved_direction(spec: RoadSectionSpec, choices: Dictionary) -> int:
	if spec.travel_direction != RoadSectionSpec.TravelDirection.UNSET:
		return spec.travel_direction
	var value: Variant = choices.get(spec.road_id)
	if value in [
		RoadSectionSpec.TravelDirection.FORWARD,
		RoadSectionSpec.TravelDirection.REVERSE,
	]:
		return value
	return RoadSectionSpec.TravelDirection.UNSET


## Checks one map-space pair before creating a Vector3.
static func _valid_source_point(value: Variant) -> bool:
	if not value is Array or value.size() != 2:
		return false
	if not (value[0] is float or value[0] is int):
		return false
	if not (value[1] is float or value[1] is int):
		return false
	return is_finite(float(value[0])) and is_finite(float(value[1]))


## Creates a normalized one-error bootstrap failure.
static func _failure(message: String) -> Dictionary:
	return { "ok": false, "errors": [message] }
