class_name EntityGenerationTracker
extends RefCounted
## Allocates positive entity IDs and advances generations before any deliberate reuse.

var _next_entity_id: int = 1
var _generation_by_id: Dictionary[int, int] = {}
var _active_ids: Dictionary[int, bool] = {}


## Allocates a never-before-used entity reference for the current session.
func allocate() -> Dictionary:
	if _next_entity_id > ReplicationIdentity.MAX_WIRE_ENTITY_ID:
		return {}

	var entity_id: int = _next_entity_id
	_next_entity_id += 1
	_generation_by_id[entity_id] = 1
	_active_ids[entity_id] = true
	return ReplicationIdentity.entity_ref(entity_id, 1)


## Retires an active reference without making the old generation valid again.
func retire(entity_ref: Dictionary) -> bool:
	if not is_current(entity_ref):
		return false

	_active_ids.erase(int(entity_ref.id))
	return true


## Reuses one retired ID only after advancing its generation.
func reuse(entity_id: int) -> Dictionary:
	if entity_id <= 0 or entity_id >= _next_entity_id or _active_ids.has(entity_id):
		return {}

	var generation: int = int(_generation_by_id.get(entity_id, 0)) + 1
	if generation > ReplicationIdentity.MAX_WIRE_GENERATION:
		return {}

	_generation_by_id[entity_id] = generation
	_active_ids[entity_id] = true
	return ReplicationIdentity.entity_ref(entity_id, generation)


## Checks both generation and active lifetime for one reference.
func is_current(entity_ref: Variant) -> bool:
	if not ReplicationIdentity.is_valid_entity_ref(entity_ref):
		return false

	var entity_id: int = int(entity_ref.id)
	return (
		_active_ids.has(entity_id)
		and int(_generation_by_id.get(entity_id, 0)) == int(entity_ref.generation)
	)
