class_name RoadSourceCatalog
extends Resource
## Stores world-integrator-owned source identity and semantic specs, never spline samples.

const MAX_ID_BYTES: int = 128

@export var district_id: StringName
@export_range(1, 2_147_483_647, 1) var source_revision: int = 1
@export_range(1, 2_147_483_647, 1) var derivation_schema_revision: int = 1
@export var addon_version: String = "0.9.4"
@export var bootstrap_source_sha256: String
@export var presets: Array[RoadTypePreset] = []
@export var sections: Array[RoadSectionSpec] = []
@export var junctions: Array[RoadJunctionSpec] = []


## Returns the section with an exact stable identity, or null when absent.
func section(section_id: StringName) -> RoadSectionSpec:
	for candidate: RoadSectionSpec in sections:
		if candidate != null and candidate.section_id == section_id:
			return candidate
	return null


## Returns the section seeded from one exact source route name, or null when absent.
func section_for_source_route(route_name: String) -> RoadSectionSpec:
	for candidate: RoadSectionSpec in sections:
		if candidate != null and candidate.source_route_name == route_name:
			return candidate
	return null


## Returns the junction with an exact stable identity, or null when absent.
func junction(junction_id: StringName) -> RoadJunctionSpec:
	for candidate: RoadJunctionSpec in junctions:
		if candidate != null and candidate.junction_id == junction_id:
			return candidate
	return null


## Validates revision ownership, bounded identities, and unique semantic records.
func validate_source() -> Dictionary:
	var errors: Array[String] = []
	if not _valid_id(district_id):
		errors.append("district_id is missing or exceeds 128 UTF-8 bytes")
	if source_revision <= 0 or derivation_schema_revision <= 0:
		errors.append("source and derivation revisions must be positive")
	if addon_version != "0.9.4":
		errors.append("catalog addon version does not match the vendored 0.9.4 pin")
	if not _valid_sha256(bootstrap_source_sha256):
		errors.append("bootstrap source SHA-256 must contain 64 lowercase hex characters")
	_validate_presets(errors)
	_validate_sections(errors)
	_validate_junctions(errors)
	return { "ok": errors.is_empty(), "errors": errors }


## Validates preset records and rejects duplicate or unbounded preset identities.
func _validate_presets(errors: Array[String]) -> void:
	var seen: Dictionary[StringName, bool] = {}
	for preset: RoadTypePreset in presets:
		if preset == null or not preset.is_valid() or not _valid_id(preset.preset_id):
			errors.append("catalog contains an invalid road preset")
			continue
		if seen.has(preset.preset_id):
			errors.append("duplicate preset_id: %s" % preset.preset_id)
		seen[preset.preset_id] = true


## Validates stable road/section records and their catalog-owned preset references.
func _validate_sections(errors: Array[String]) -> void:
	var seen: Dictionary[StringName, bool] = {}
	var seen_source_routes: Dictionary[String, bool] = {}
	for spec: RoadSectionSpec in sections:
		if spec == null or not spec.is_valid():
			errors.append("catalog contains an invalid road section")
			continue
		if not _valid_id(spec.road_id) or not _valid_id(spec.section_id):
			errors.append("road or section identity exceeds its bound")
		if seen.has(spec.section_id):
			errors.append("duplicate section_id: %s" % spec.section_id)
		seen[spec.section_id] = true
		if seen_source_routes.has(spec.source_route_name):
			errors.append("duplicate source route: %s" % spec.source_route_name)
		seen_source_routes[spec.source_route_name] = true
		if spec.preset not in presets:
			errors.append("section %s references a preset outside the catalog" % spec.section_id)


## Validates stable junction records and rejects duplicate identities.
func _validate_junctions(errors: Array[String]) -> void:
	var seen: Dictionary[StringName, bool] = {}
	for spec: RoadJunctionSpec in junctions:
		if spec == null or not spec.is_valid() or not _valid_id(spec.junction_id):
			errors.append("catalog contains an invalid road junction")
			continue
		if seen.has(spec.junction_id):
			errors.append("duplicate junction_id: %s" % spec.junction_id)
		seen[spec.junction_id] = true


## Checks the frozen source digest shape without accepting uppercase or punctuation.
func _valid_sha256(value: String) -> bool:
	if value.length() != 64:
		return false
	for character: String in value:
		if character not in "0123456789abcdef":
			return false
	return true


## Checks the shared authored identity byte bound.
func _valid_id(value: StringName) -> bool:
	var byte_count: int = String(value).to_utf8_buffer().size()
	return byte_count > 0 and byte_count <= MAX_ID_BYTES
