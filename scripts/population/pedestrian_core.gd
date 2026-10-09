class_name PedestrianCore
extends RefCounted
## Owns compact host-only pedestrian decisions and emits ActorMotion-compatible intent.

enum ThreatKind {
	GUNFIRE,
	BLAST,
	VEHICLE,
}

const STATE_WANDER: int = 0
const STATE_WAIT_CROSSING: int = 1
const STATE_CROSSING: int = 2
const STATE_FLEE: int = 3
const TICKS_PER_SECOND: int = 60
const DECISION_INTERVAL_TICKS: int = 6
const MAX_AGENTS: int = 64
const MAX_THREATS_PER_DECISION: int = 8
const MAX_THREATS: int = MAX_THREATS_PER_DECISION
const THREAT_LIFETIME_CAP_TICKS: int = 5 * TICKS_PER_SECOND
const FLEE_DURATION_TICKS: int = 5 * TICKS_PER_SECOND
const ARRIVAL_DISTANCE_M: float = 0.2
const SEPARATION_RADIUS_M: float = 1.2
const SEPARATION_WEIGHT: float = 3.0
const LANE_WEIGHT: float = 0.12
const WALK_COMMAND_SCALE: float = 0.3
const FLEE_COMMAND_SCALE: float = 0.6

var _navigation: PopulationNavigation
var _reservations: CrossingReservations
var _grid: PopulationSpatialGrid = PopulationSpatialGrid.new()
var _node_set: Dictionary[int, bool] = {}
var _agent_slots: Dictionary[int, int] = {}
var _state: PedestrianStateStore = PedestrianStateStore.new()
var _commands: Array[FootCommand] = []
var _threats: Array[Dictionary] = []
var _last_reaction_ticks: Dictionary[int, int] = {}
var _last_reaction_threat_ids: Dictionary[int, int] = {}
var _reaction_ticks_by_agent: Dictionary[int, Dictionary] = {}
var _next_threat_id: int = 1


## Installs the graph and finite reservation owner before any slots are admitted.
func configure(
	navigation: PopulationNavigation,
	reservations: CrossingReservations,
) -> bool:
	if navigation == null or reservations == null or not navigation.is_valid():
		return false

	var nodes: PackedInt32Array = navigation.node_ids()
	if nodes.is_empty():
		return false
	var node_set: Dictionary[int, bool] = {}
	for node_id: int in nodes:
		if node_id < 0 or node_set.has(node_id):
			return false
		if not navigation.node_position(node_id).is_finite():
			return false
		node_set[node_id] = true
	for node_id: int in nodes:
		var neighbors: PackedInt32Array = navigation.sidewalk_neighbors(node_id)
		if neighbors.is_empty():
			return false
		for neighbor_id: int in neighbors:
			if not node_set.has(neighbor_id):
				return false

	_navigation = navigation
	_reservations = reservations
	_node_set = node_set
	reset()
	return true


## Clears every host-owned slot, event, command, and reservation claim.
func reset() -> void:
	_agent_slots.clear()
	_state.clear()
	_commands.clear()
	_threats.clear()
	_last_reaction_ticks.clear()
	_last_reaction_threat_ids.clear()
	_reaction_ticks_by_agent.clear()
	_next_threat_id = 1
	_grid.clear()
	if _reservations != null:
		_reservations.reset()


## Adds one stable host identity at a valid graph node and observed position.
func add_agent(agent_id: int, start_node: int, position: Vector2) -> bool:
	if _navigation == null or _state.ids.size() >= MAX_AGENTS:
		return false
	if agent_id <= 0 or _agent_slots.has(agent_id) or not _node_set.has(start_node):
		return false
	if not position.is_finite():
		return false

	var slot: int = _state.ids.size()
	_agent_slots[agent_id] = slot
	_state.append(
		agent_id,
		start_node,
		position,
		agent_id % DECISION_INTERVAL_TICKS,
		STATE_WANDER,
	)
	_commands.append(null)
	return true


## Updates one slot from authoritative motion output without making AI a pose writer.
func sync_position(agent_id: int, position: Vector2) -> bool:
	if not _agent_slots.has(agent_id) or not position.is_finite():
		return false

	_state.positions[_agent_slots[agent_id]] = position
	return true


## Publishes one bounded host threat for staggered perception.
func publish_threat(
	position: Vector2,
	radius_m: float,
	kind: ThreatKind,
	host_tick: int,
	lifetime_ticks: int = DECISION_INTERVAL_TICKS,
) -> bool:
	if not position.is_finite() or not is_finite(radius_m) or radius_m <= 0.0:
		return false
	if kind < ThreatKind.GUNFIRE or kind > ThreatKind.VEHICLE:
		return false
	if host_tick < 0 or lifetime_ticks <= 0 or lifetime_ticks > THREAT_LIFETIME_CAP_TICKS:
		return false

	_expire_threats(host_tick)
	if _threats.size() >= MAX_THREATS:
		return false

	_threats.append({
		"id": _next_threat_id,
		"position": position,
		"radius_squared": radius_m * radius_m,
		"kind": kind,
		"published_tick": host_tick,
		"expires_tick": host_tick + lifetime_ticks,
	})
	_next_threat_id += 1
	return true


## Runs one 60 Hz host decision/motion-intent tick for every admitted slot.
func step(host_tick: int) -> Array[FootCommand]:
	if _navigation == null or host_tick < 0:
		return []

	_reservations.advance(host_tick)
	_expire_threats(host_tick)
	_grid.clear()
	for slot: int in _state.ids.size():
		_grid.insert(slot, _state.positions[slot])
	for slot: int in _state.ids.size():
		_update_arrival(slot, host_tick)
		if host_tick % DECISION_INTERVAL_TICKS == _state.decision_phases[slot]:
			_decide(slot, host_tick)
		_commands[slot] = to_foot_command(slot, host_tick)

	return _commands.duplicate()


## Adapts one AI slot to A2.1's validated world-relative FootCommand type.
func to_foot_command(slot: int, host_tick: int) -> FootCommand:
	if slot < 0 or slot >= _state.ids.size() or host_tick < 0:
		return null

	var movement: Vector2 = _movement_for(slot)
	_state.sequences[slot] += 1
	if movement.length_squared() > 0.000001:
		_state.aim_yaws[slot] = atan2(-movement.x, -movement.y)
	if not movement.is_finite():
		movement = Vector2.ZERO
	elif movement.length_squared() > FootCommand.MAX_MOVE_LENGTH_SQUARED:
		movement = movement.normalized()
	if not is_finite(_state.aim_yaws[slot]):
		_state.aim_yaws[slot] = 0.0
	else:
		_state.aim_yaws[slot] = wrapf(_state.aim_yaws[slot], -PI, PI)
	return FootCommand.new(
		_state.sequences[slot],
		host_tick,
		movement,
		_state.aim_yaws[slot],
		false,
		false,
	)


## Returns the compact behavior state for focused integration and acceptance checks.
func state_for_agent(agent_id: int) -> int:
	if not _agent_slots.has(agent_id):
		return -1
	return _state.states[_agent_slots[agent_id]]


## Returns the most recent host tick on which one identity received a threat.
func last_reaction_tick(agent_id: int) -> int:
	return _last_reaction_ticks.get(agent_id, -1)


## Returns the last bounded threat identity observed by one pedestrian.
func last_reaction_threat_id(agent_id: int) -> int:
	return _last_reaction_threat_ids.get(agent_id, 0)


## Returns the receipt tick for one exact pedestrian and live threat identity.
func reaction_tick(agent_id: int, threat_id: int) -> int:
	var receipts: Dictionary = _reaction_ticks_by_agent.get(agent_id, {})
	return receipts.get(threat_id, -1)


## Returns one pedestrian's bounded count of currently live threat receipts.
func reaction_receipt_count(agent_id: int) -> int:
	var receipts: Dictionary = _reaction_ticks_by_agent.get(agent_id, {})
	return receipts.size()


## Returns the most recently published bounded threat identity.
func latest_threat_id() -> int:
	return _next_threat_id - 1


## Returns how many staggered 10 Hz decisions one identity has executed.
func decision_count(agent_id: int) -> int:
	if not _agent_slots.has(agent_id):
		return 0
	return _state.decision_counts[_agent_slots[agent_id]]


## Exposes the reservation owner for AI-traffic yielding and behavior metrics.
func reservations() -> CrossingReservations:
	return _reservations


## Applies threat perception, reservation state, and the next bounded graph choice.
func _decide(slot: int, host_tick: int) -> void:
	_state.decision_counts[slot] += 1
	_perceive_threats(slot, host_tick)
	if _state.states[slot] == STATE_WAIT_CROSSING:
		var reservation_status: StringName = _reservations.status(_state.ids[slot])
		if reservation_status == CrossingReservations.STATUS_ACTIVE:
			_state.states[slot] = STATE_CROSSING
		elif reservation_status == CrossingReservations.STATUS_NONE:
			_state.target_nodes[slot] = _state.current_nodes[slot]
			_state.crossings[slot] = &""
			_state.states[slot] = STATE_WANDER
		return
	if host_tick >= _state.flee_until_ticks[slot] and _state.states[slot] == STATE_FLEE:
		_state.states[slot] = STATE_WANDER
	if _state.target_nodes[slot] != _state.current_nodes[slot]:
		return

	var next_node: int = _choose_next_node(slot, host_tick < _state.flee_until_ticks[slot])
	_state.target_nodes[slot] = next_node
	var crossing_id: StringName = _navigation.crossing_between(
		_state.current_nodes[slot], next_node
	)
	_state.crossings[slot] = crossing_id
	if crossing_id == &"":
		return

	var status: StringName = _reservations.request(crossing_id, _state.ids[slot], host_tick)
	if status == CrossingReservations.STATUS_ACTIVE:
		_state.states[slot] = STATE_CROSSING
	else:
		_state.states[slot] = STATE_WAIT_CROSSING


## Selects a deterministic wander edge or the edge farthest from the active threat.
func _choose_next_node(slot: int, fleeing: bool) -> int:
	var neighbors: PackedInt32Array = _navigation.sidewalk_neighbors(_state.current_nodes[slot])
	if fleeing:
		var selected: int = neighbors[0]
		var best_distance: float = -1.0
		for node_id: int in neighbors:
			var distance: float = _navigation.node_position(node_id).distance_squared_to(
				_state.threat_positions[slot]
			)
			if distance > best_distance:
				selected = node_id
				best_distance = distance
		return selected

	var hash_value: int = absi(
		int(_state.ids[slot]) * 1_103_515_245 + _state.decision_counts[slot] * 12_345
	)
	return neighbors[hash_value % neighbors.size()]


## Records every eligible receipt and selects the latest threat for steering.
func _perceive_threats(slot: int, host_tick: int) -> void:
	var agent_id: int = _state.ids[slot]
	var selected_id: int = 0
	var selected_position: Vector2 = Vector2.ZERO
	for threat: Dictionary in _threats:
		var threat_id: int = threat.id
		if reaction_tick(agent_id, threat_id) >= 0:
			continue
		if _state.positions[slot].distance_squared_to(threat.position) > threat.radius_squared:
			continue

		_record_threat_receipt(agent_id, threat_id, host_tick)
		if threat_id > selected_id:
			selected_id = threat_id
			selected_position = threat.position

	if selected_id == 0:
		return

	_state.threat_positions[slot] = selected_position
	_state.flee_until_ticks[slot] = host_tick + FLEE_DURATION_TICKS
	_state.last_threat_ids[slot] = selected_id
	if _state.states[slot] != STATE_WAIT_CROSSING:
		_state.states[slot] = STATE_FLEE
	_last_reaction_ticks[agent_id] = host_tick
	_last_reaction_threat_ids[agent_id] = selected_id


## Retains one exact receipt while its structurally bounded threat remains live.
func _record_threat_receipt(agent_id: int, threat_id: int, host_tick: int) -> void:
	var receipts: Dictionary = _reaction_ticks_by_agent.get(agent_id, {})
	receipts[threat_id] = host_tick
	_reaction_ticks_by_agent[agent_id] = receipts


## Releases a completed crossing and advances graph ownership at the observed pose.
func _update_arrival(slot: int, host_tick: int) -> void:
	if _state.target_nodes[slot] == _state.current_nodes[slot]:
		return
	var target_position: Vector2 = _navigation.node_position(_state.target_nodes[slot])
	if _state.positions[slot].distance_to(target_position) > ARRIVAL_DISTANCE_M:
		return

	_state.current_nodes[slot] = _state.target_nodes[slot]
	if _state.crossings[slot] != &"":
		_reservations.release(_state.ids[slot], host_tick)
	_state.crossings[slot] = &""
	_state.states[slot] = STATE_FLEE if host_tick < _state.flee_until_ticks[slot] else STATE_WANDER


## Combines graph travel, flow lanes, and bounded local separation into held intent.
func _movement_for(slot: int) -> Vector2:
	if _state.states[slot] == STATE_WAIT_CROSSING:
		return Vector2.ZERO
	if _state.target_nodes[slot] == _state.current_nodes[slot]:
		return Vector2.ZERO

	var target: Vector2 = _navigation.node_position(_state.target_nodes[slot])
	var offset: Vector2 = target - _state.positions[slot]
	if offset.length_squared() <= 0.000001:
		return Vector2.ZERO
	var direction: Vector2 = offset.normalized()
	var lane_sign: float = -1.0 if _state.ids[slot] % 2 == 0 else 1.0
	var lane_strength: float = minf(1.0, offset.length()) * LANE_WEIGHT
	var lane: Vector2 = Vector2(-direction.y, direction.x) * lane_sign * lane_strength
	var separation: Vector2 = _separation_for(slot)
	var steering: Vector2 = (direction + lane + separation * SEPARATION_WEIGHT).normalized()
	var scale: float = (
		FLEE_COMMAND_SCALE if _state.states[slot] == STATE_FLEE else WALK_COMMAND_SCALE
	)
	return steering * scale


## Uses the reusable grid to repel only nearby slots with deterministic tie breaks.
func _separation_for(slot: int) -> Vector2:
	var steering: Vector2 = Vector2.ZERO
	for other_slot: int in _grid.nearby(_state.positions[slot], SEPARATION_RADIUS_M):
		if other_slot == slot:
			continue
		var offset: Vector2 = _state.positions[slot] - _state.positions[other_slot]
		var distance: float = offset.length()
		if distance >= SEPARATION_RADIUS_M:
			continue
		if distance <= 0.0001:
			var tie_sign: float = -1.0 if _state.ids[slot] < _state.ids[other_slot] else 1.0
			steering += Vector2(tie_sign, 0.0)
		else:
			steering += offset / distance * (SEPARATION_RADIUS_M - distance)
	return steering


## Removes expired records and their exact per-agent receipts at the supplied tick.
func _expire_threats(host_tick: int) -> void:
	for index: int in range(_threats.size() - 1, -1, -1):
		if host_tick >= int(_threats[index].expires_tick):
			var threat_id: int = _threats[index].id
			_threats.remove_at(index)
			_forget_threat_receipts(threat_id)


## Prunes one expired threat identity from every bounded pedestrian receipt map.
func _forget_threat_receipts(threat_id: int) -> void:
	for agent_id: int in _reaction_ticks_by_agent.keys():
		var receipts: Dictionary = _reaction_ticks_by_agent[agent_id]
		receipts.erase(threat_id)
		if receipts.is_empty():
			_reaction_ticks_by_agent.erase(agent_id)
		else:
			_reaction_ticks_by_agent[agent_id] = receipts
