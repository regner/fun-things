class_name S09GridlockTracker
extends RefCounted
## Tracks unresolved no-progress episodes for traffic local to one intersection zone.

const LOCAL_RADIUS_M: float = 20.0
const PROGRESS_WINDOW_TICKS: int = 240
const PROGRESS_DISTANCE_M: float = 0.25
const PHYSICS_HZ: int = 60

var _center: Vector3
var _window_ticks: int = 0
var _window_origins: Dictionary = {}
var _episode_active: bool = false
var _episode_ticks: int = 0
var _episodes: int = 0
var _resolved: int = 0
var _max_stall_ticks: int = 0


## Starts one independent tracker at an authored conflict-zone center.
func configure(center: Vector3) -> void:
	_center = center
	_window_ticks = 0
	_window_origins.clear()
	_episode_active = false
	_episode_ticks = 0
	_episodes = 0
	_resolved = 0
	_max_stall_ticks = 0


## Advances only crossing-route cars, so unrelated outer-loop motion cannot mask gridlock.
func advance(cars: Array[Dictionary]) -> void:
	var local: Dictionary = _local_positions(cars)
	if local.is_empty():
		_resolve_or_reset()
		return
	if _window_origins.is_empty() or not _same_id_set(local, _window_origins):
		_resolve_or_reset()
		_window_origins = local
		return

	_window_ticks += 1
	if _made_progress(local):
		_resolve_or_reset()
		_window_origins = local
		return
	if _episode_active:
		_episode_ticks += 1
		_max_stall_ticks = maxi(_max_stall_ticks, _episode_ticks)
	elif _window_ticks >= PROGRESS_WINDOW_TICKS:
		_episode_active = true
		_episode_ticks = _window_ticks
		_episodes += 1
		_max_stall_ticks = maxi(_max_stall_ticks, _episode_ticks)


## Reports started, resolved and currently unresolved local episodes plus worst duration.
func receipt() -> Dictionary:
	return {
		"episodes": _episodes, "resolved": _resolved,
		"unresolved": 1 if _episode_active else 0,
		"max_stall_seconds": float(_max_stall_ticks) / PHYSICS_HZ,
	}


## Selects only cars assigned to the crossing loops inside this queue/conflict region.
func _local_positions(cars: Array[Dictionary]) -> Dictionary:
	var result: Dictionary = {}
	for car: Dictionary in cars:
		if car.family == "outer" or car.position.distance_to(_center) > LOCAL_RADIUS_M:
			continue
		result[int(car.id)] = car.position
	return result


## Resolves one active episode on renewed progress and clears the current observation window.
func _resolve_or_reset() -> void:
	if _episode_active:
		_resolved += 1
	_episode_active = false
	_episode_ticks = 0
	_window_ticks = 0
	_window_origins.clear()


## Requires every local identity to remain stable during one no-progress observation window.
func _same_id_set(left: Dictionary, right: Dictionary) -> bool:
	if left.size() != right.size():
		return false
	for identity: int in left:
		if not right.has(identity):
			return false
	return true


## Detects meaningful displacement by any local car from the start of the current window.
func _made_progress(local: Dictionary) -> bool:
	for identity: int in local:
		if local[identity].distance_to(_window_origins[identity]) >= PROGRESS_DISTANCE_M:
			return true
	return false
