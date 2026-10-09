class_name CityData
extends Node
## Publishes saved-world compatibility identity and authored spawn-anchor descriptors.

const FAILURE_CONTENT_INVALID: StringName = &"CONTENT_INVALID"
const MAX_IDENTITY_BYTES: int = 128
const MAX_MANIFEST_RESOURCES: int = 512
const CONTENT_MANIFEST_SCHEMA: int = 1
const CONTENT_DIGEST_DOMAIN: String = "brackett-composed-world-v1"

@export var district_id: StringName
@export var content_revision: int = 1
@export var content_signature: String
@export_file("*.json") var content_manifest_path: String
@export var world_path: NodePath
@export var player_spawns_path: NodePath
@export var parked_cars_path: NodePath


## Returns the build-compatible identity derived from the saved city revision.
func identity() -> Dictionary:
	return {
		"district_id": district_id,
		"content_id": _content_id(),
		"content_revision": content_revision,
		"content_signature": content_signature,
	}


## Returns the bounded fields consumed by the session admission handshake.
func admission_identity() -> Dictionary:
	return {
		"district_id": district_id,
		"content_id": _content_id(),
	}


## Fails closed when a peer does not name this exact saved world revision.
func validate_admission(candidate: Dictionary) -> Dictionary:
	if not validate_composition().get("ok", false):
		return _content_failure()
	if not _valid_identity_field(candidate.get("district_id")):
		return _content_failure()
	if not _valid_identity_field(candidate.get("content_id")):
		return _content_failure()
	if StringName(candidate.district_id) != district_id:
		return _content_failure()
	if String(candidate.content_id) != _content_id():
		return _content_failure()

	return { "ok": true, "identity": admission_identity() }


## Returns saved candidate descriptors of one supported kind without applying clearance.
func anchor_descriptors(kind: StringName) -> Array[Dictionary]:
	var container_path: NodePath
	if kind == WorldAnchor.KIND_PLAYER_SPAWN:
		container_path = player_spawns_path
	elif kind == WorldAnchor.KIND_PARKED_CAR:
		container_path = parked_cars_path
	else:
		return []

	var container: Node = get_node_or_null(container_path)
	if container == null:
		return []

	var descriptors: Array[Dictionary] = []
	for child: Node in container.get_children():
		if child is WorldAnchor and child.anchor_kind == kind:
			descriptors.append(child.descriptor())
	return descriptors


## Checks saved world binding and anchor identity uniqueness before gameplay consumes them.
func validate_composition() -> Dictionary:
	var world: Node = get_node_or_null(world_path)
	if not world is Node3D or StringName(world.get("world_id")) != district_id:
		return _content_failure()
	if content_revision <= 0 or content_signature.length() != 64:
		return _content_failure()

	var seen: Dictionary[StringName, bool] = {}
	for kind: StringName in [WorldAnchor.KIND_PLAYER_SPAWN, WorldAnchor.KIND_PARKED_CAR]:
		var descriptors: Array[Dictionary] = anchor_descriptors(kind)
		if descriptors.is_empty():
			return _content_failure()
		for descriptor: Dictionary in descriptors:
			var anchor_world_id: StringName = descriptor.world_id
			if anchor_world_id == &"" or seen.has(anchor_world_id):
				return _content_failure()
			seen[anchor_world_id] = true

	if calculate_content_signature() != content_signature:
		return _content_failure()

	return { "ok": true, "identity": identity(), "anchor_count": seen.size() }


## Digests checked dependency hashes, world placement, and canonical saved anchors.
func calculate_content_signature() -> String:
	var world: Node = get_node_or_null(world_path)
	if not world is Node3D or world.scene_file_path.is_empty():
		return ""
	var manifest: Dictionary = _load_content_manifest(world.scene_file_path)
	if manifest.is_empty():
		return ""
	if OS.has_feature("editor") and not _manifest_matches_sources(manifest):
		return ""

	var context := HashingContext.new()
	if context.start(HashingContext.HASH_SHA256) != OK:
		return ""
	_update_hash_text(context, CONTENT_DIGEST_DOMAIN)
	_update_hash_text(context, "world_transform")
	_update_transform_hash(context, (world as Node3D).transform)
	for row: Dictionary in manifest.resources:
		_update_hash_text(context, row.path)
		_update_hash_text(context, row.sha256)

	var descriptors: Array[Dictionary] = []
	descriptors.append_array(anchor_descriptors(WorldAnchor.KIND_PLAYER_SPAWN))
	descriptors.append_array(anchor_descriptors(WorldAnchor.KIND_PARKED_CAR))
	descriptors.sort_custom(_anchor_descriptor_less)
	for descriptor: Dictionary in descriptors:
		_update_anchor_hash(context, descriptor)

	return context.finish().hex_encode()


## Builds a sorted source manifest for editor tooling and deliberate content updates.
func build_content_manifest() -> Dictionary:
	var world: Node = get_node_or_null(world_path)
	if not world is Node3D or world.scene_file_path.is_empty():
		return {}
	var dependencies: PackedStringArray = _dependency_closure(world.scene_file_path)
	if dependencies.is_empty() or dependencies.size() > MAX_MANIFEST_RESOURCES:
		return {}

	var rows: Array[Dictionary] = []
	for path: String in dependencies:
		var source_hash: String = FileAccess.get_sha256(path)
		if source_hash.is_empty():
			return {}
		rows.append({ "path": path, "sha256": source_hash })
	return {
		"schema": CONTENT_MANIFEST_SCHEMA,
		"world_root": world.scene_file_path,
		"resources": rows,
	}


## Builds the bounded admission fingerprint while keeping the source signature inspectable.
func _content_id() -> String:
	return "%s-r%d-%s" % [district_id, content_revision, content_signature]


## Loads and validates the bounded, sorted source-hash manifest used in exported builds.
func _load_content_manifest(expected_root: String) -> Dictionary:
	if content_manifest_path.is_empty() or not FileAccess.file_exists(content_manifest_path):
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(content_manifest_path))
	if not parsed is Dictionary:
		return {}
	var manifest: Dictionary = parsed
	if not _valid_manifest_header(manifest, expected_root):
		return {}
	if not _valid_manifest_resources(manifest.get("resources")):
		return {}
	return manifest


## Checks manifest schema and binds it to the instantiated saved world root.
func _valid_manifest_header(manifest: Dictionary, expected_root: String) -> bool:
	return (
		manifest.get("schema") == CONTENT_MANIFEST_SCHEMA
		and String(manifest.get("world_root")) == expected_root
	)


## Checks resource count, strict sort order, row types, paths, and hash widths.
func _valid_manifest_resources(resources: Variant) -> bool:
	if not resources is Array or resources.is_empty():
		return false
	if resources.size() > MAX_MANIFEST_RESOURCES:
		return false

	var previous_path: String = ""
	for value: Variant in resources:
		if not _valid_manifest_row(value, previous_path):
			return false
		previous_path = value.path
	return true


## Checks one canonical manifest row without allocating from unbounded values.
func _valid_manifest_row(value: Variant, previous_path: String) -> bool:
	if not value is Dictionary:
		return false
	var row: Dictionary = value
	var path: Variant = row.get("path")
	var source_hash: Variant = row.get("sha256")
	return (
		path is String
		and source_hash is String
		and (String(path).begins_with("res://") or String(path).begins_with("user://"))
		and String(path) > previous_path
		and String(source_hash).length() == 64
	)


## Confirms a development checkout still matches every checked manifest row exactly.
func _manifest_matches_sources(manifest: Dictionary) -> bool:
	var world: Node = get_node_or_null(world_path)
	var dependencies: PackedStringArray = _dependency_closure(world.scene_file_path)
	var resources: Array = manifest.resources
	if dependencies.size() != resources.size():
		return false
	for index: int in dependencies.size():
		var row: Dictionary = resources[index]
		if dependencies[index] != row.path:
			return false
		if FileAccess.get_sha256(dependencies[index]) != row.sha256:
			return false
	return true


## Collects one sorted, cycle-safe resource closure including source import settings.
func _dependency_closure(root_path: String) -> PackedStringArray:
	var pending: Array[String] = [root_path]
	var paths: Dictionary[String, bool] = {}
	while not pending.is_empty():
		var path: String = pending.pop_back()
		if paths.has(path):
			continue
		if not FileAccess.file_exists(path):
			return PackedStringArray()
		paths[path] = true

		var import_path: String = path + ".import"
		if FileAccess.file_exists(import_path):
			paths[import_path] = true
		for record: String in ResourceLoader.get_dependencies(path):
			var dependency_path: String = _dependency_path(record)
			if not dependency_path.is_empty() and not paths.has(dependency_path):
				pending.append(dependency_path)

	var sorted_paths := PackedStringArray(paths.keys())
	sorted_paths.sort()
	return sorted_paths


## Extracts a loadable fallback path from Godot's UID dependency record format.
func _dependency_path(record: String) -> String:
	for prefix: String in ["res://", "user://"]:
		var path_start: int = record.find(prefix)
		if path_start >= 0:
			return record.substr(path_start)
	return ""


## Adds one canonical saved-anchor record to the platform-independent digest.
func _update_anchor_hash(context: HashingContext, descriptor: Dictionary) -> void:
	_update_hash_text(context, String(descriptor.world_id))
	_update_hash_text(context, String(descriptor.kind))
	_update_transform_hash(context, descriptor.transform)


## Adds every transform component with stable text encoding to a content digest.
func _update_transform_hash(context: HashingContext, value: Transform3D) -> void:
	for component: float in [
		value.basis.x.x,
		value.basis.x.y,
		value.basis.x.z,
		value.basis.y.x,
		value.basis.y.y,
		value.basis.y.z,
		value.basis.z.x,
		value.basis.z.y,
		value.basis.z.z,
		value.origin.x,
		value.origin.y,
		value.origin.z,
	]:
		_update_hash_text(context, String.num(component, 17))


## Orders anchors by stable authored identity before hashing their records.
func _anchor_descriptor_less(left: Dictionary, right: Dictionary) -> bool:
	return String(left.world_id) < String(right.world_id)


## Adds a length-delimited UTF-8 value to a digest without concatenation ambiguity.
func _update_hash_text(context: HashingContext, value: String) -> void:
	var bytes: PackedByteArray = value.to_utf8_buffer()
	var length_bytes := PackedByteArray()
	length_bytes.resize(8)
	length_bytes.encode_u64(0, bytes.size())
	context.update(length_bytes)
	context.update(bytes)


## Validates bounded string-like identity fields before comparison or allocation.
func _valid_identity_field(value: Variant) -> bool:
	if not (value is String or value is StringName):
		return false
	var bytes: int = String(value).to_utf8_buffer().size()
	return bytes > 0 and bytes <= MAX_IDENTITY_BYTES


## Creates the normalized admission failure expected by Session and Replication.
func _content_failure() -> Dictionary:
	return {
		"ok": false,
		"failure": {
			"code": FAILURE_CONTENT_INVALID,
			"retryable": false,
			"message_key": &"content_invalid",
		},
	}
