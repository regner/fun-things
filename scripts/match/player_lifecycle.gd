class_name PlayerLifecycle
extends Node
## Owns player alive/dead state, respawn deadlines, safe-spawn retries, and admitted roster.

signal changed(view: Dictionary)
signal transition(participant_id: int, state: Dictionary)

const PHYSICS_TICKS_PER_SECOND: int = 60
const RESPAWN_DELAY_TICKS: int = 3 * PHYSICS_TICKS_PER_SECOND
const SEARCH_DEADLINE_TICKS: int = 5 * PHYSICS_TICKS_PER_SECOND
const MAX_CANDIDATES_PER_TICK: int = 10
const PLAYER_CLEARANCE_RADIUS_M: float = 0.45
const MAX_PLAYERS: int = 4

var _local_participant_id: int = 0
var _candidates: Array[Dictionary] = []
var _reservations: SpawnReservations
var _clearance_query: Callable
var _respawn_callback: Callable
var _states: Dictionary[int, Dictionary] = {}
var _current_tick: int = 0
var _revision: int = 0


## Configures host-owned candidates and injected clearance/spawn collaborators.
func configure_authority(
	local_participant_id: int,
	candidates: Array[Dictionary],
	reservations: SpawnReservations,
	clearance_query: Callable,
	respawn_callback: Callable,
) -> bool:
	if (
		local_participant_id <= 0
		or candidates.is_empty()
		or candidates.size() > MAX_CANDIDATES_PER_TICK
		or reservations == null
		or not clearance_query.is_valid()
		or not respawn_callback.is_valid()
	):
		return false
	for candidate: Dictionary in candidates:
		if not _valid_candidate(candidate):
			return false

	_local_participant_id = local_participant_id
	_candidates = candidates.duplicate(true)
	_reservations = reservations
	_clearance_query = clearance_query
	_respawn_callback = respawn_callback
	return true


## Configures a replica as a read-only lifecycle and roster presentation source.
func configure_replica(local_participant_id: int) -> bool:
	if local_participant_id <= 0:
		return false

	_local_participant_id = local_participant_id
	return true


## Registers one created player lifetime before it can be admitted or simulated.
func register_player(
	participant_id: int,
	entity_ref: Dictionary,
	admitted: bool,
	alive: bool = true,
) -> bool:
	if (
		participant_id <= 0
		or _states.size() >= MAX_PLAYERS and not _states.has(participant_id)
		or not ReplicationIdentity.is_valid_entity_ref(entity_ref)
	):
		return false

	_states[participant_id] = {
		"participant_id": participant_id,
		"entity_ref": entity_ref.duplicate(),
		"alive": alive,
		"admitted": admitted,
		"respawn_tick": -1,
		"search_deadline_tick": -1,
		"candidate_cursor": 0,
		"spawn_failure": &"",
	}
	_commit(participant_id)
	return true


## Changes only authoritative roster membership while retaining the player's life.
func set_admitted(participant_id: int, admitted: bool) -> bool:
	if not _states.has(participant_id):
		return false
	var state: Dictionary = _states[participant_id]
	if bool(state.admitted) == admitted:
		return true

	state.admitted = admitted
	_commit(participant_id)
	return true


## Commits death and the exact three-second server-tick respawn deadline once.
func mark_dead(participant_id: int, now_tick: int) -> bool:
	if not _states.has(participant_id) or now_tick < 0:
		return false
	var state: Dictionary = _states[participant_id]
	if not bool(state.alive):
		return false

	_current_tick = now_tick
	state.alive = false
	state.respawn_tick = now_tick + RESPAWN_DELAY_TICKS
	state.search_deadline_tick = int(state.respawn_tick) + SEARCH_DEADLINE_TICKS
	state.candidate_cursor = 0
	state.spawn_failure = &""
	_commit(participant_id)
	return true


## Advances bounded due respawns without allowing one blocked player to stall another.
func step(now_tick: int) -> void:
	if now_tick < _current_tick:
		return
	_current_tick = now_tick
	if _reservations == null:
		_emit_changed()
		return

	var participant_ids: Array[int] = _states.keys()
	participant_ids.sort()
	for participant_id: int in participant_ids:
		var state: Dictionary = _states[participant_id]
		if bool(state.alive) or int(state.respawn_tick) < 0:
			continue
		if now_tick < int(state.respawn_tick):
			continue
		_attempt_respawn(participant_id, now_tick)

	_emit_changed()


## Rehydrates retained players immediately under a new match revision and no old claims.
func reset_players(now_tick: int) -> Dictionary:
	if _reservations == null or now_tick < 0:
		return { "ok": false }

	_current_tick = now_tick
	_reservations.clear()
	var failed: Array[int] = []
	var participant_ids: Array[int] = _states.keys()
	participant_ids.sort()
	for participant_id: int in participant_ids:
		var state: Dictionary = _states[participant_id]
		state.alive = false
		state.respawn_tick = now_tick
		state.search_deadline_tick = now_tick + SEARCH_DEADLINE_TICKS
		state.candidate_cursor = 0
		state.spawn_failure = &""
		_commit(participant_id)
		if not _attempt_respawn(participant_id, now_tick):
			failed.append(participant_id)

	_emit_changed()
	return { "ok": failed.is_empty(), "failed_participants": failed }


## Installs bounded authoritative rows for late join, live lifecycle, or reset hydration.
func apply_replica_rows(match_revision: int, revision: int, rows: Array, now_tick: int) -> bool:
	if match_revision <= 0 or revision < _revision or rows.size() > MAX_PLAYERS or now_tick < 0:
		return false

	var candidate_states: Dictionary[int, Dictionary] = {}
	for value: Variant in rows:
		if not value is Dictionary or not _valid_replica_row(value):
			return false
		var row: Dictionary = value
		var participant_id: int = int(row.participant_id)
		if candidate_states.has(participant_id):
			return false
		candidate_states[participant_id] = {
			"participant_id": participant_id,
			"entity_ref": {
				"id": int(row.id),
				"generation": int(row.generation),
			},
			"alive": bool(row.alive),
			"admitted": bool(row.admitted),
			"respawn_tick": (
				now_tick + int(row.respawn_ticks_remaining) if not bool(row.alive) else -1
			),
			"search_deadline_tick": -1,
			"candidate_cursor": 0,
			"spawn_failure": StringName(row.spawn_failure),
		}

	_states = candidate_states
	_current_tick = now_tick
	_revision = revision
	_emit_changed()
	return true


## Removes one disconnected participant and all lifecycle-owned pending work.
func remove_player(participant_id: int) -> void:
	if not _states.has(participant_id):
		return
	if _reservations != null:
		_reservations.release(participant_id)
	_states.erase(participant_id)
	_revision += 1
	_emit_changed()


## Returns the local life view plus only authoritative admitted roster rows.
func view() -> Dictionary:
	var result: Dictionary = { "roster": _roster_rows(), "revision": _revision }
	var state: Dictionary = _states.get(_local_participant_id, {})
	if state.is_empty():
		return result

	result.alive = bool(state.alive)
	result.entity_ref = state.entity_ref.duplicate()
	if not bool(state.alive):
		result.respawn_seconds = maxf(
			0.0,
			float(int(state.respawn_tick) - _current_tick) / PHYSICS_TICKS_PER_SECOND,
		)
		if state.spawn_failure != &"":
			result.spawn_failure = state.spawn_failure
	return result


## Returns one participant's immutable state for enclosing coordinator diagnostics.
func player_view(participant_id: int) -> Dictionary:
	var state: Dictionary = _states.get(participant_id, {})
	if state.is_empty():
		return {}
	return {
		"participant_id": participant_id,
		"entity_ref": state.entity_ref.duplicate(),
		"alive": state.alive,
		"admitted": state.admitted,
		"respawn_ticks_remaining": (
			maxi(0, int(state.respawn_tick) - _current_tick)
			if not bool(state.alive) and int(state.respawn_tick) >= 0
			else 0
		),
		"spawn_failure": state.spawn_failure,
	}


## Captures complete bounded lifecycle and roster state for reliable hydration.
func hydration_rows(now_tick: int) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	var participant_ids: Array[int] = _states.keys()
	participant_ids.sort()
	for participant_id: int in participant_ids:
		var state: Dictionary = _states[participant_id]
		var entity_ref: Dictionary = state.entity_ref
		rows.append(
			{
				"participant_id": participant_id,
				"id": entity_ref.id,
				"generation": entity_ref.generation,
				"alive": state.alive,
				"admitted": state.admitted,
				"respawn_ticks_remaining": (
					maxi(0, int(state.respawn_tick) - now_tick)
					if not bool(state.alive)
					else 0
				),
				"spawn_failure": state.spawn_failure,
			}
		)
	return rows


## Reports whether one participant may currently submit or receive movement.
func is_alive(participant_id: int) -> bool:
	return _states.has(participant_id) and bool(_states[participant_id].alive)


## Returns the current generation fence owned by one player lifecycle.
func entity_ref_for(participant_id: int) -> Dictionary:
	var state: Dictionary = _states.get(participant_id, {})
	return state.get("entity_ref", {}).duplicate()


## Returns the monotonic lifecycle revision carried by reliable state messages.
func revision() -> int:
	return _revision


## Tries a fixed bounded candidate window and keeps a blocked player dead on failure.
func _attempt_respawn(participant_id: int, now_tick: int) -> bool:
	var state: Dictionary = _states[participant_id]
	var candidate_count: int = _candidates.size()
	var attempts: int = mini(MAX_CANDIDATES_PER_TICK, candidate_count)
	for offset: int in attempts:
		var index: int = (int(state.candidate_cursor) + offset) % candidate_count
		var candidate: Dictionary = _candidates[index]
		var position: Vector3 = candidate.transform.origin
		if _reservations.conflicts(position, PLAYER_CLEARANCE_RADIUS_M, participant_id):
			continue
		if bool(_clearance_query.call(candidate, participant_id)):
			continue
		if not _reservations.reserve(
			participant_id,
			candidate.world_id,
			position,
			PLAYER_CLEARANCE_RADIUS_M,
		):
			continue

		var result: Variant = _respawn_callback.call(participant_id, candidate)
		if result is Dictionary and result.get("ok", false):
			state.entity_ref = result.entity_ref.duplicate()
			state.alive = true
			state.respawn_tick = -1
			state.search_deadline_tick = -1
			state.candidate_cursor = (index + 1) % candidate_count
			state.spawn_failure = &""
			_reservations.release(participant_id)
			_commit(participant_id)
			return true

		_reservations.release(participant_id)

	state.candidate_cursor = (int(state.candidate_cursor) + attempts) % candidate_count
	if now_tick >= int(state.search_deadline_tick):
		state.respawn_tick = -1
		state.spawn_failure = &"SPAWN_BLOCKED"
		_commit(participant_id)
	return false


## Advances owner revision and emits immutable state only after transition completion.
func _commit(participant_id: int) -> void:
	_revision += 1
	transition.emit(participant_id, _states[participant_id].duplicate(true))
	_emit_changed()


## Publishes a defensive presentation snapshot to all read-only consumers.
func _emit_changed() -> void:
	changed.emit(view().duplicate(true))


## Builds the authoritative admitted roster without padding or inferred participants.
func _roster_rows() -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	var participant_ids: Array[int] = _states.keys()
	participant_ids.sort()
	for participant_id: int in participant_ids:
		var state: Dictionary = _states[participant_id]
		if bool(state.admitted):
			rows.append({ "participant_id": participant_id, "phase": &"ADMITTED" })
	return rows


## Validates one immutable authored spawn descriptor before accepting configuration.
func _valid_candidate(candidate: Dictionary) -> bool:
	return (
		candidate.has("world_id")
		and candidate.world_id is StringName
		and candidate.world_id != &""
		and candidate.has("transform")
		and candidate.transform is Transform3D
		and candidate.transform.origin.is_finite()
	)


## Validates one exact bounded lifecycle wire row before replacing replica state.
func _valid_replica_row(row: Dictionary) -> bool:
	if row.size() != 7:
		return false
	for field: String in [
		"participant_id",
		"id",
		"generation",
		"alive",
		"admitted",
		"respawn_ticks_remaining",
		"spawn_failure",
	]:
		if not row.has(field):
			return false
	return (
		row.participant_id is int
		and int(row.participant_id) > 0
		and ReplicationIdentity.has_valid_entity_ref_fields(row)
		and row.alive is bool
		and row.admitted is bool
		and row.respawn_ticks_remaining is int
		and int(row.respawn_ticks_remaining) >= 0
		and int(row.respawn_ticks_remaining) <= SEARCH_DEADLINE_TICKS + RESPAWN_DELAY_TICKS
		and (row.spawn_failure is String or row.spawn_failure is StringName)
		and String(row.spawn_failure).to_utf8_buffer().size() <= 32
	)
