class_name WorldAnchor
extends Marker3D
## Publishes one authored spawn candidate without deciding runtime clearance or reservation.

const KIND_PLAYER_SPAWN: StringName = &"PLAYER_SPAWN"
const KIND_PARKED_CAR: StringName = &"PARKED_CAR"

@export var world_id: StringName
@export_enum("PLAYER_SPAWN", "PARKED_CAR") var anchor_kind: StringName
@export var provisional_owner_answer: bool = true


## Returns immutable authored data for CityData consumers and clearance queries.
func descriptor() -> Dictionary:
	return {
		"world_id": world_id,
		"kind": anchor_kind,
		"transform": global_transform,
		"provisional_owner_answer": provisional_owner_answer,
	}
