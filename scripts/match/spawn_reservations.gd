class_name SpawnReservations
extends RefCounted
## Owns bounded atomic spawn-clearance claims shared by dynamic entity lifecycles.

const MAX_RESERVATIONS: int = 148

var _claims_by_owner: Dictionary[int, Dictionary] = {}


## Atomically reserves one planar clearance circle when it overlaps no other owner.
func reserve(owner_id: int, world_id: StringName, position: Vector3, radius_m: float) -> bool:
	if (
		owner_id <= 0
		or world_id == &""
		or not position.is_finite()
		or not is_finite(radius_m)
		or radius_m <= 0.0
	):
		return false
	if _claims_by_owner.has(owner_id):
		return false
	if _claims_by_owner.size() >= MAX_RESERVATIONS:
		return false
	if conflicts(position, radius_m, owner_id):
		return false

	_claims_by_owner[owner_id] = {
		"world_id": world_id,
		"position": position,
		"radius_m": radius_m,
	}
	return true


## Reports whether one candidate overlaps an existing claim other than its owner.
func conflicts(position: Vector3, radius_m: float, ignored_owner_id: int = 0) -> bool:
	if not position.is_finite() or not is_finite(radius_m) or radius_m <= 0.0:
		return true

	var planar_position := Vector2(position.x, position.z)
	for owner_id: int in _claims_by_owner:
		if owner_id == ignored_owner_id:
			continue
		var claim: Dictionary = _claims_by_owner[owner_id]
		var claim_position: Vector3 = claim.position
		var combined_radius: float = radius_m + float(claim.radius_m)
		if planar_position.distance_squared_to(
			Vector2(claim_position.x, claim_position.z)
		) < combined_radius * combined_radius:
			return true

	return false


## Releases one completed or canceled owner claim idempotently.
func release(owner_id: int) -> void:
	_claims_by_owner.erase(owner_id)


## Clears all obsolete claims during coherent match reset or teardown.
func clear() -> void:
	_claims_by_owner.clear()


## Reports current bounded work for lifecycle tests and diagnostics.
func count() -> int:
	return _claims_by_owner.size()
