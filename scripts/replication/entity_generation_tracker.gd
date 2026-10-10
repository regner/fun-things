class_name EntityGenerationTracker
extends RefCounted
## Allocates bounded entity references and advances generations before deliberate reuse.

const MAX_SPAWNED_REFERENCES: int = 65_536

var _next_entity_id: int = 1
var _spawned_reference_count: int = 0
var _generation_by_id: Dictionary[int, int] = {}
var _active_ids: Dictionary[int, bool] = {}


## Allocates a never-before-used entity reference within the match-local spawn ceiling.
func allocate() -> Dictionary:
	if _spawned_reference_count >= MAX_SPAWNED_REFERENCES:
		return _failure(&"SPAWNED_REFERENCE_LIMIT")
	if _next_entity_id > ReplicationIdentity.MAX_WIRE_ENTITY_ID:
		return _failure(&"ENTITY_ID_LIMIT")

	var entity_id: int = _next_entity_id
	_next_entity_id += 1
	_generation_by_id[entity_id] = 1
	_active_ids[entity_id] = true
	_spawned_reference_count += 1
	return _success(ReplicationIdentity.entity_ref(entity_id, 1))


## Retires an active reference without making the old generation valid again.
func retire(entity_ref: Dictionary) -> bool:
	if not is_current(entity_ref):
		return false

	_active_ids.erase(int(entity_ref.id))
	return true


## Reuses one retired ID only after advancing generation and consuming match capacity.
func reuse(entity_id: int) -> Dictionary:
	if entity_id <= 0 or entity_id >= _next_entity_id or _active_ids.has(entity_id):
		return _failure(&"INVALID_REUSE")
	if _spawned_reference_count >= MAX_SPAWNED_REFERENCES:
		return _failure(&"SPAWNED_REFERENCE_LIMIT")

	var generation: int = int(_generation_by_id.get(entity_id, 0)) + 1
	if generation > ReplicationIdentity.MAX_WIRE_GENERATION:
		return _failure(&"GENERATION_LIMIT")

	_generation_by_id[entity_id] = generation
	_active_ids[entity_id] = true
	_spawned_reference_count += 1
	return _success(ReplicationIdentity.entity_ref(entity_id, generation))


## Checks both generation and active lifetime for one reference.
func is_current(entity_ref: Variant) -> bool:
	if not ReplicationIdentity.is_valid_entity_ref(entity_ref):
		return false

	var entity_id: int = int(entity_ref.id)
	return (
		_active_ids.has(entity_id)
		and int(_generation_by_id.get(entity_id, 0)) == int(entity_ref.generation)
	)


## Reports successful allocation and reuse operations for boundary diagnostics.
func spawned_reference_count() -> int:
	return _spawned_reference_count


## Wraps one valid reference in an explicit allocation result.
func _success(entity_ref: Dictionary) -> Dictionary:
	return { "ok": true, "entity_ref": entity_ref }


## Returns one specific refusal without consuming an ID, generation, or count.
func _failure(code: StringName) -> Dictionary:
	return { "ok": false, "failure": { "code": code } }
