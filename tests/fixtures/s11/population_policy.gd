class_name S11PopulationPolicy
extends RefCounted

const PEDESTRIAN_CAP: int = 64
const LIVE_CAR_CAP: int = 32
const WRECK_CAP: int = 16
const DEAD_PEDESTRIAN_CAP: int = 16
const VIEW_RADIUS_M: float = 30.0

var counts: Dictionary = {}
var reservations: Array[Dictionary] = []


## Restore empty runtime counts and release every pending spawn reservation.
func reset() -> void:
	counts = {"pedestrian": 0, "car": 0, "wreck": 0, "dead_pedestrian": 0}
	reservations.clear()


## Report whether adding one entity would preserve the global kind cap.
func can_add(kind: String) -> bool:
	if not counts.has(kind):
		return false

	return int(counts[kind]) < _cap_for(kind)


## Select and reserve the first bounded candidate outside every player view with clearance.
func reserve_replenishment(
	kind: String,
	candidates: Array[Dictionary],
	player_positions: Array[Vector2],
	clearance_radius_m: float,
	max_candidates: int = 10
) -> Dictionary:
	if not can_add(kind) or clearance_radius_m <= 0.0:
		return {}

	for index: int in range(mini(candidates.size(), max_candidates)):
		var candidate: Dictionary = candidates[index]
		if not _valid_candidate(candidate) or _in_any_view(candidate.position, player_positions):
			continue
		if not _has_clearance(candidate.position, clearance_radius_m):
			continue

		var reservation: Dictionary = {
			"kind": kind,
			"position": candidate.position,
			"radius": clearance_radius_m,
		}
		reservations.append(reservation)
		return reservation.duplicate(true)

	return {}


## Commit one owned reservation to the population without exceeding its cap.
func commit(reservation: Dictionary) -> bool:
	var index: int = reservations.find(reservation)
	if index < 0 or not can_add(str(reservation.get("kind", ""))):
		return false

	var kind: String = reservation.kind
	reservations.remove_at(index)
	counts[kind] = int(counts[kind]) + 1
	return true


## Release an abandoned reservation without changing population counts.
func release(reservation: Dictionary) -> void:
	var index: int = reservations.find(reservation)
	if index >= 0:
		reservations.remove_at(index)


## Resolve the fixed cap owned by each population category.
func _cap_for(kind: String) -> int:
	match kind:
		"pedestrian":
			return PEDESTRIAN_CAP
		"car":
			return LIVE_CAR_CAP
		"wreck":
			return WRECK_CAP
		"dead_pedestrian":
			return DEAD_PEDESTRIAN_CAP
		_:
			return 0


## Reject malformed candidates before any distance work or reservation mutation.
func _valid_candidate(candidate: Dictionary) -> bool:
	return candidate.has("position") and candidate.position is Vector2


## Keep replenishment outside the conservative circular view of every player.
func _in_any_view(position: Vector2, player_positions: Array[Vector2]) -> bool:
	for player_position: Vector2 in player_positions:
		if position.distance_to(player_position) <= VIEW_RADIUS_M:
			return true

	return false


## Apply the shared circular clearance model to all pending spawn reservations.
func _has_clearance(position: Vector2, radius_m: float) -> bool:
	for reservation: Dictionary in reservations:
		var separation: float = position.distance_to(reservation.position)
		if separation < radius_m + float(reservation.radius):
			return false

	return true
