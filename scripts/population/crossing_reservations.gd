class_name CrossingReservations
extends RefCounted
## Owns finite marked-crossing queues and the query consumed by AI traffic.

const STATUS_NONE: StringName = &"NONE"
const STATUS_QUEUED: StringName = &"QUEUED"
const STATUS_ACTIVE: StringName = &"ACTIVE"
const STATUS_REJECTED: StringName = &"REJECTED"
const DEFAULT_ACTIVE_CAP: int = 4
const DEFAULT_QUEUE_CAP: int = 16
const DEFAULT_MAX_WAIT_TICKS: int = 6 * 60
const DEFAULT_MAX_OVERLAP_TICKS: int = 5 * 60

var _crossing_ids: Array[StringName] = []
var _conflicts: Dictionary[StringName, Array] = {}
var _queues: Dictionary[StringName, Array] = {}
var _active: Dictionary[StringName, Array] = {}
var _queued_at: Dictionary[int, int] = {}
var _entered_at: Dictionary[int, int] = {}
var _agent_crossing: Dictionary[int, StringName] = {}
var _active_cap: int = DEFAULT_ACTIVE_CAP
var _queue_cap: int = DEFAULT_QUEUE_CAP
var _max_wait_ticks: int = DEFAULT_MAX_WAIT_TICKS
var _max_overlap_ticks: int = DEFAULT_MAX_OVERLAP_TICKS
var _max_queue_length_observed: int = 0
var _max_queue_age_observed: int = 0
var _max_overlap_observed: int = 0


## Installs crossing identities and conflict sets from the injected navigation owner.
func configure(
	navigation: PopulationNavigation,
	active_cap: int = DEFAULT_ACTIVE_CAP,
	queue_cap: int = DEFAULT_QUEUE_CAP,
	max_wait_ticks: int = DEFAULT_MAX_WAIT_TICKS,
	max_overlap_ticks: int = DEFAULT_MAX_OVERLAP_TICKS,
) -> bool:
	if navigation == null or not navigation.is_valid():
		return false
	if active_cap <= 0 or queue_cap <= 0 or max_wait_ticks <= 0 or max_overlap_ticks <= 0:
		return false

	var crossing_ids: Array[StringName] = navigation.crossing_ids()
	var known: Dictionary[StringName, bool] = {}
	for crossing_id: StringName in crossing_ids:
		if crossing_id == &"" or known.has(crossing_id):
			return false
		known[crossing_id] = true
	for crossing_id: StringName in crossing_ids:
		for conflict_id: StringName in navigation.crossing_conflicts(crossing_id):
			if not known.has(conflict_id) or conflict_id == crossing_id:
				return false
			if crossing_id not in navigation.crossing_conflicts(conflict_id):
				return false

	_crossing_ids = crossing_ids.duplicate()
	_active_cap = active_cap
	_queue_cap = queue_cap
	_max_wait_ticks = max_wait_ticks
	_max_overlap_ticks = max_overlap_ticks
	_conflicts.clear()
	for crossing_id: StringName in _crossing_ids:
		_conflicts[crossing_id] = navigation.crossing_conflicts(crossing_id).duplicate()
	reset()
	return true


## Clears transient claims while retaining the configured finite crossing set.
func reset() -> void:
	_queues.clear()
	_active.clear()
	_queued_at.clear()
	_entered_at.clear()
	_agent_crossing.clear()
	_max_queue_length_observed = 0
	_max_queue_age_observed = 0
	_max_overlap_observed = 0
	for crossing_id: StringName in _crossing_ids:
		_queues[crossing_id] = []
		_active[crossing_id] = []


## Requests one crossing claim without allowing duplicate queue entries.
func request(crossing_id: StringName, agent_id: int, host_tick: int) -> StringName:
	if not _queues.has(crossing_id) or agent_id <= 0 or host_tick < 0:
		return STATUS_REJECTED
	advance(host_tick)
	if _agent_crossing.has(agent_id):
		if _agent_crossing[agent_id] != crossing_id:
			return STATUS_REJECTED
		return STATUS_ACTIVE if _entered_at.has(agent_id) else STATUS_QUEUED

	var queue: Array = _queues[crossing_id]
	if queue.size() >= _queue_cap:
		return STATUS_REJECTED
	queue.append(agent_id)
	_queues[crossing_id] = queue
	_queued_at[agent_id] = host_tick
	_agent_crossing[agent_id] = crossing_id
	_max_queue_length_observed = maxi(_max_queue_length_observed, queue.size())
	_promote(host_tick)
	return STATUS_ACTIVE if _entered_at.has(agent_id) else STATUS_QUEUED


## Releases an active or queued claim and admits the next compatible pedestrians.
func release(agent_id: int, host_tick: int) -> void:
	if not _agent_crossing.has(agent_id):
		return

	_remove_agent(agent_id)
	_promote(host_tick)


## Expires bounded waits and occupancy before promoting compatible queue heads.
func advance(host_tick: int) -> void:
	if host_tick < 0:
		return

	for agent_id: int in _queued_at.keys():
		var age: int = host_tick - _queued_at[agent_id]
		_max_queue_age_observed = maxi(_max_queue_age_observed, age)
		if age >= _max_wait_ticks:
			_remove_agent(agent_id)
	for agent_id: int in _entered_at.keys():
		var duration: int = host_tick - _entered_at[agent_id]
		_max_overlap_observed = maxi(_max_overlap_observed, duration)
		if duration >= _max_overlap_ticks:
			_remove_agent(agent_id)
	_promote(host_tick)


## Returns whether an agent is queued, active, or currently unclaimed.
func status(agent_id: int) -> StringName:
	if _entered_at.has(agent_id):
		return STATUS_ACTIVE
	if _queued_at.has(agent_id):
		return STATUS_QUEUED
	return STATUS_NONE


## Lets AI traffic yield to an occupied crossing or any active conflict.
func should_ai_traffic_yield(crossing_id: StringName) -> bool:
	if not _active.has(crossing_id):
		return false
	if not (_active[crossing_id] as Array).is_empty():
		return true
	for conflict_id: StringName in _conflicts[crossing_id]:
		if not (_active[conflict_id] as Array).is_empty():
			return true
	return false


## Reports the configured wait bound for behavior acceptance checks.
func max_wait_ticks() -> int:
	return _max_wait_ticks


## Reports the configured occupancy bound for behavior acceptance checks.
func max_overlap_ticks() -> int:
	return _max_overlap_ticks


## Reports the largest finite queue observed since reset.
func max_queue_length_observed() -> int:
	return _max_queue_length_observed


## Reports the oldest queue entry observed before grant or expiry.
func max_queue_age_observed() -> int:
	return _max_queue_age_observed


## Reports the longest active reservation observed before release or expiry.
func max_overlap_observed() -> int:
	return _max_overlap_observed


## Promotes queue heads while capacity and every configured conflict permit entry.
func _promote(host_tick: int) -> void:
	var changed: bool = true
	while changed:
		changed = false
		for crossing_id: StringName in _crossing_ids:
			var queue: Array = _queues[crossing_id]
			var occupants: Array = _active[crossing_id]
			if queue.is_empty() or occupants.size() >= _active_cap:
				continue
			if _has_active_conflict(crossing_id):
				continue

			var agent_id: int = queue.pop_front()
			occupants.append(agent_id)
			_queues[crossing_id] = queue
			_active[crossing_id] = occupants
			_queued_at.erase(agent_id)
			_entered_at[agent_id] = host_tick
			changed = true


## Checks active crossings that conflict with one candidate crossing.
func _has_active_conflict(crossing_id: StringName) -> bool:
	for conflict_id: StringName in _conflicts[crossing_id]:
		if not (_active[conflict_id] as Array).is_empty():
			return true
	return false


## Removes one agent from its configured crossing and all timing indices.
func _remove_agent(agent_id: int) -> void:
	var crossing_id: StringName = _agent_crossing.get(agent_id, &"")
	if crossing_id != &"":
		(_queues[crossing_id] as Array).erase(agent_id)
		(_active[crossing_id] as Array).erase(agent_id)
	_queued_at.erase(agent_id)
	_entered_at.erase(agent_id)
	_agent_crossing.erase(agent_id)
