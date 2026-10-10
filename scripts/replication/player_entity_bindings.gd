class_name PlayerEntityBindings
extends RefCounted
## Owns participant-to-EntityRef mappings, generations, and stable spawn slots.

var tracker := EntityGenerationTracker.new()
var binding_by_participant: Dictionary = {}
var participant_by_entity: Dictionary = {}
var spawn_slot_by_participant: Dictionary = {}


## Allocates one EntityRef independently from the Session participant identity.
func allocate(participant_id: int) -> Dictionary:
	if binding_by_participant.has(participant_id):
		return binding_by_participant[participant_id]
	var allocated: Dictionary = tracker.allocate()
	if not allocated.get("ok", false):
		return {}

	var entity_ref: Dictionary = allocated.entity_ref
	var binding: Dictionary = {
		"participant_id": participant_id,
		"id": entity_ref.id,
		"generation": entity_ref.generation,
	}
	binding_by_participant[participant_id] = binding
	participant_by_entity[int(entity_ref.id)] = participant_id
	return binding


## Retires one host binding after its reliable removal event is published.
func retire(participant_id: int) -> void:
	var binding: Dictionary = binding_by_participant.get(participant_id, {})
	if binding.is_empty():
		return
	tracker.retire({ "id": binding.id, "generation": binding.generation })
	participant_by_entity.erase(int(binding.id))
	binding_by_participant.erase(participant_id)


## Returns bounded immutable binding rows for reliable delivery before state records.
func rows() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for participant_id: int in binding_by_participant:
		result.append(binding_by_participant[participant_id].duplicate())
	return result


## Assigns the first free one-based spawn slot for this participant lifetime.
func allocate_spawn_slot(participant_id: int, slot_count: int) -> int:
	if spawn_slot_by_participant.has(participant_id):
		return spawn_slot_by_participant[participant_id]
	for slot: int in range(1, slot_count + 1):
		if slot not in spawn_slot_by_participant.values():
			spawn_slot_by_participant[participant_id] = slot
			return slot
	return 0


## Builds one reliable lifecycle row from the current participant binding.
func durable_event(
	event_kind: int,
	phase: int,
	participant_id: int,
	revision: int,
	tick: int,
) -> Dictionary:
	var binding: Dictionary = binding_by_participant[participant_id]
	return {
		"event_kind": event_kind,
		"phase": phase,
		"id": binding.id,
		"generation": binding.generation,
		"revision": revision,
		"tick": tick,
	}
