class_name CityData
extends Node
## Publishes saved-world compatibility identity and authored spawn-anchor descriptors.

const FAILURE_CONTENT_INVALID: StringName = &"CONTENT_INVALID"
const MAX_IDENTITY_BYTES: int = 128

@export var district_id: StringName
@export var content_revision: int = 1
@export var content_signature: String
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
	if world == null or StringName(world.get("world_id")) != district_id:
		return _content_failure()
	if content_revision <= 0 or content_signature.length() != 64:
		return _content_failure()
	if FileAccess.get_sha256(world.scene_file_path) != content_signature:
		return _content_failure()

	var seen: Dictionary[StringName, bool] = {}
	for kind: StringName in [WorldAnchor.KIND_PLAYER_SPAWN, WorldAnchor.KIND_PARKED_CAR]:
		var descriptors: Array[Dictionary] = anchor_descriptors(kind)
		if descriptors.is_empty():
			return _content_failure()
		for descriptor: Dictionary in descriptors:
			var world_id: StringName = descriptor.world_id
			if world_id == &"" or seen.has(world_id):
				return _content_failure()
			seen[world_id] = true

	return { "ok": true, "identity": identity(), "anchor_count": seen.size() }


## Builds the bounded admission fingerprint while keeping the source signature inspectable.
func _content_id() -> String:
	return "%s-r%d-%s" % [district_id, content_revision, content_signature]


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
