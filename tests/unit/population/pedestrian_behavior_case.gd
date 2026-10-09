class_name PedestrianBehaviorCase
extends RefCounted
## Runs seeded 64-agent synthetic-grid behavior metrics through production APIs.

const AGENT_COUNT: int = 64
const TICKS_PER_SECOND: int = 60
const RUN_TICKS: int = 2 * 60 * TICKS_PER_SECOND
const ACTOR_SPEED_MPS: float = 5.0
const OVERLAP_DISTANCE_M: float = 0.7
const OVERLAP_SAMPLE_TICKS: int = TICKS_PER_SECOND
const STUCK_WINDOW_TICKS: int = 4 * TICKS_PER_SECOND
const STUCK_DISPLACEMENT_M: float = 0.25
const NORMAL_THREAT_INTERVAL_TICKS: int = 20 * TICKS_PER_SECOND
const STORM_THREAT_INTERVAL_TICKS: int = 5 * TICKS_PER_SECOND


## Runs one normal or flee-storm seed and returns S10-compatible behavior metrics.
func run(seed: int, storm: bool) -> Dictionary:
	var navigation: SyntheticPopulationNavigation = SyntheticPopulationNavigation.new()
	var reservations: CrossingReservations = CrossingReservations.new()
	if not reservations.configure(navigation, 4, 16, 3 * TICKS_PER_SECOND, 5 * TICKS_PER_SECOND):
		return { "ok": false, "failure": "reservation configuration failed" }
	var core: PedestrianCore = PedestrianCore.new()
	if not core.configure(navigation, reservations):
		return { "ok": false, "failure": "core configuration failed" }

	var state: Dictionary = _make_state(core, navigation, reservations, seed, storm)
	if not _admit_agents(state):
		return { "ok": false, "failure": "agent admission failed" }
	_simulate(state)
	return _result(state)


## Allocates one case's metric state outside the measured host tick loop.
func _make_state(
	core: PedestrianCore,
	navigation: SyntheticPopulationNavigation,
	reservations: CrossingReservations,
	seed: int,
	storm: bool,
) -> Dictionary:
	var rng: RandomNumberGenerator = RandomNumberGenerator.new()
	rng.seed = seed
	return {
		"core": core,
		"navigation": navigation,
		"reservations": reservations,
		"seed": seed,
		"storm": storm,
		"rng": rng,
		"positions": PackedVector2Array(),
		"checkpoints": PackedVector2Array(),
		"pending": {},
		"latencies": PackedInt32Array(),
		"ongoing": {},
		"stuck": {},
		"grid": PopulationSpatialGrid.new(),
		"max_overlap_ticks": 0,
		"max_sampled_pairs": 0,
	}


## Admits all 64 identities at distinct synthetic grid nodes.
func _admit_agents(state: Dictionary) -> bool:
	var navigation: SyntheticPopulationNavigation = state.navigation
	var core: PedestrianCore = state.core
	var positions: PackedVector2Array = state.positions
	var checkpoints: PackedVector2Array = state.checkpoints
	var node_offset: int = absi(int(state.seed)) % 3 if state.storm else 0
	for slot: int in AGENT_COUNT:
		var start_node: int = (slot + node_offset) % AGENT_COUNT
		var start: Vector2 = navigation.node_position(start_node)
		positions.append(start)
		checkpoints.append(start)
		if not core.add_agent(slot + 1, start_node, start):
			return false
	state.positions = positions
	state.checkpoints = checkpoints
	return true


## Advances threats, commands, synthetic motion, and acceptance metrics.
func _simulate(state: Dictionary) -> void:
	for host_tick: int in RUN_TICKS:
		var interval: int = (
			STORM_THREAT_INTERVAL_TICKS if state.storm else NORMAL_THREAT_INTERVAL_TICKS
		)
		if host_tick % interval == 0:
			_inject_threat(state, host_tick)

		var core: PedestrianCore = state.core
		var commands: Array[FootCommand] = core.step(host_tick)
		var positions: PackedVector2Array = state.positions
		for slot: int in AGENT_COUNT:
			positions[slot] += (
				commands[slot].move as Vector2
			) * ACTOR_SPEED_MPS / TICKS_PER_SECOND
			core.sync_position(slot + 1, positions[slot])
		state.positions = positions
		_collect_reactions(state)
		state.max_overlap_ticks = maxi(
			state.max_overlap_ticks,
			_update_continuous_overlaps(positions, state.grid, state.ongoing),
		)
		if host_tick % OVERLAP_SAMPLE_TICKS == 0:
			state.max_sampled_pairs = maxi(
				state.max_sampled_pairs,
				_count_overlap_pairs(positions, state.grid),
			)
		if host_tick > 0 and host_tick % STUCK_WINDOW_TICKS == 0:
			_sample_stuck(positions, state.checkpoints, state.stuck)


## Chooses and publishes the scenario's deterministic threat.
func _inject_threat(state: Dictionary, host_tick: int) -> void:
	var position := Vector2(21.0, 21.0)
	var radius_m: float = 100.0
	var kind := PedestrianCore.ThreatKind.BLAST
	if not state.storm:
		var node_id: int = (state.rng as RandomNumberGenerator).randi_range(
			0, AGENT_COUNT - 1
		)
		position = (state.navigation as SyntheticPopulationNavigation).node_position(node_id)
		radius_m = 14.0
		kind = PedestrianCore.ThreatKind.GUNFIRE
	_publish_expected_reactions(state, position, radius_m, kind, host_tick)


## Publishes one threat and records every currently eligible stable identity.
func _publish_expected_reactions(
	state: Dictionary,
	position: Vector2,
	radius_m: float,
	kind: PedestrianCore.ThreatKind,
	host_tick: int,
) -> void:
	var core: PedestrianCore = state.core
	if not core.publish_threat(position, radius_m, kind, host_tick):
		return
	var positions: PackedVector2Array = state.positions
	var pending: Dictionary = state.pending
	var threat_id: int = core.latest_threat_id()
	for slot: int in positions.size():
		if positions[slot].distance_to(position) > radius_m:
			continue
		var agent_id: int = slot + 1
		pending["%d:%d" % [host_tick, agent_id]] = {
			"agent_id": agent_id,
			"published_tick": host_tick,
			"threat_id": threat_id,
		}


## Retires every newly observed reaction and records its host-tick latency.
func _collect_reactions(state: Dictionary) -> void:
	var core: PedestrianCore = state.core
	var pending: Dictionary = state.pending
	var latencies: PackedInt32Array = state.latencies
	for key: String in pending.keys():
		var expectation: Dictionary = pending[key]
		var reaction_tick: int = core.reaction_tick(
			expectation.agent_id, expectation.threat_id
		)
		if reaction_tick < 0:
			continue
		latencies.append(reaction_tick - int(expectation.published_tick))
		pending.erase(key)
	state.latencies = latencies


## Updates every actual overlapping pair on each simulated motion tick.
func _update_continuous_overlaps(
	positions: PackedVector2Array,
	grid: PopulationSpatialGrid,
	ongoing: Dictionary,
) -> int:
	_build_grid(positions, grid)
	var current: Dictionary[String, bool] = {}
	var maximum: int = 0
	for slot: int in positions.size():
		for other_slot: int in grid.nearby(positions[slot], OVERLAP_DISTANCE_M):
			if other_slot <= slot:
				continue
			if positions[slot].distance_to(positions[other_slot]) >= OVERLAP_DISTANCE_M:
				continue
			var key: String = "%d:%d" % [slot, other_slot]
			current[key] = true
			ongoing[key] = ongoing.get(key, 0) + 1
			maximum = maxi(maximum, ongoing[key])
	for key: String in ongoing.keys():
		if not current.has(key):
			ongoing.erase(key)
	return maximum


## Counts sampled overlap pairs using the same actual-position definition as S10.
func _count_overlap_pairs(
	positions: PackedVector2Array,
	grid: PopulationSpatialGrid,
) -> int:
	_build_grid(positions, grid)
	var pairs: int = 0
	for slot: int in positions.size():
		for other_slot: int in grid.nearby(positions[slot], OVERLAP_DISTANCE_M):
			if other_slot > slot and positions[slot].distance_to(positions[other_slot]) < (
				OVERLAP_DISTANCE_M
			):
				pairs += 1
	return pairs


## Records identities moving less than 0.25 m during any four-second window.
func _sample_stuck(
	positions: PackedVector2Array,
	checkpoints: PackedVector2Array,
	stuck_ids: Dictionary,
) -> void:
	for slot: int in positions.size():
		if positions[slot].distance_to(checkpoints[slot]) < STUCK_DISPLACEMENT_M:
			stuck_ids[slot + 1] = true
		checkpoints[slot] = positions[slot]


## Rebuilds the reusable metric grid from current synthetic ActorMotion output.
func _build_grid(
	positions: PackedVector2Array,
	grid: PopulationSpatialGrid,
) -> void:
	grid.clear()
	for slot: int in positions.size():
		grid.insert(slot, positions[slot])


## Builds the final receipt without adding timing to behavior acceptance.
func _result(state: Dictionary) -> Dictionary:
	var reservations: CrossingReservations = state.reservations
	return {
		"ok": state.pending.is_empty() and not state.latencies.is_empty(),
		"seed": state.seed,
		"scenario": "flee" if state.storm else "normal",
		"ticks": RUN_TICKS,
		"max_sampled_overlap_pairs": state.max_sampled_pairs,
		"max_continuous_overlap_ticks": state.max_overlap_ticks,
		"stuck_identities": state.stuck.size(),
		"max_crossing_wait_ticks": reservations.max_queue_age_observed(),
		"max_crossing_queue": reservations.max_queue_length_observed(),
		"max_reservation_overlap_ticks": reservations.max_overlap_observed(),
		"max_flee_reaction_ticks": _packed_max(state.latencies),
		"reaction_count": state.latencies.size(),
		"pending_reaction_count": state.pending.size(),
		"pending_reaction_keys": state.pending.keys().slice(0, 8),
	}


## Returns the greatest reaction latency in one nonempty packed metric array.
func _packed_max(values: PackedInt32Array) -> int:
	var maximum: int = values[0]
	for value: int in values:
		maximum = maxi(maximum, value)
	return maximum
