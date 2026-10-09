class_name S17CombatAdapter
extends RefCounted
## Feeds four scripted players through S12's actual host validator without networking.

const PLAYER_COUNT: int = 4
const FIRST_PEER_ID: int = 2
const SHOT_INTERVAL_TICKS: int = 15
const STEP_SECONDS: float = 1.0 / 60.0

var _combat: S12Combat
var _session: S03Session
var _sequences: Dictionary = {}
var _accepted: int = 0
var _rejected: Dictionary = {}
var _rewind_queries: int = 0


## Installs an admitted four-player host context around the unchanged S12 combat owner.
func begin(combat: S12Combat, session: S03Session) -> void:
	_combat = combat
	_session = session
	_session.phase = "ACTIVE"
	_session.session_id = "17171717171717171717171717171717"
	_session.roster.clear()
	for offset: int in PLAYER_COUNT:
		var peer_id: int = FIRST_PEER_ID + offset
		_session.roster[peer_id] = { "phase": "ADMITTED", "participant": peer_id }
		_sequences[peer_id] = 0
	_combat.configure(_session, "host", "normal")
	_reset_validator_state()


## Advances target history and validates one scripted shot per player at pistol cadence.
func step(tick: int) -> void:
	_combat.physics_step(STEP_SECONDS)
	if tick % SHOT_INTERVAL_TICKS != 0:
		return

	for offset: int in PLAYER_COUNT:
		var peer_id: int = FIRST_PEER_ID + offset
		var target_id: String = "pedestrian" if (tick / SHOT_INTERVAL_TICKS + offset) % (
			2) == 0 else "car"
		var target: S12Target = _combat.targets[target_id]
		_sequences[peer_id] = int(_sequences[peer_id]) + 1
		# Accelerated simulated ticks explicitly satisfy S12's wall-clock cadence/reload gates.
		_combat.next_fire_by_peer[peer_id] = 0
		if int(_combat.magazine_by_peer.get(peer_id, S12Combat.MAGAZINE_SIZE)) <= 0:
			_combat.magazine_by_peer[peer_id] = S12Combat.MAGAZINE_SIZE
			_combat.reload_end_by_peer[peer_id] = 0
		var direction: Vector3 = (
			target.global_position - _combat.global_position).normalized()
		var envelope: Dictionary = _intent(peer_id, target_id, direction)
		var outcome: String = _combat._validate_intent(peer_id, envelope)
		if not outcome.is_empty():
			_rejected[outcome] = int(_rejected.get(outcome, 0)) + 1
			continue

		_accepted += 1
		var now: int = int(Time.get_unix_time_from_system() * 1_000_000.0)
		var rewound: Dictionary = _combat._rewound_position(target_id,
			int(envelope.view_usec), now)
		_combat._ray_hits(_combat.global_position, direction, rewound.position,
			target.hit_radius_m)
		_rewind_queries += 1


## Clears only combat receipts while retaining warmed history, cadence and sequence state.
func begin_measurement() -> void:
	_accepted = 0
	_rejected.clear()
	_rewind_queries = 0


## Reports accepted validation and rewind-query work across all four scripted players.
func receipt() -> Dictionary:
	return {
		"players": PLAYER_COUNT,
		"accepted_shots": _accepted,
		"rejected_shots": _rejected.duplicate(),
		"rewind_queries": _rewind_queries,
		"history_samples": _combat.history.size(),
		"history_peak_bytes": _combat.history_peak_bytes,
	}


## Proves the adapter returns S12's expected valid, duplicate and malformed verdicts.
func equivalence() -> Dictionary:
	_reset_validator_state()
	var peer_id: int = FIRST_PEER_ID
	_sequences[peer_id] = 1
	var valid: Dictionary = _intent(peer_id, "pedestrian", Vector3.FORWARD)
	var accepted: String = _combat._validate_intent(peer_id, valid)
	var duplicate: String = _combat._validate_intent(peer_id, valid)
	_sequences[peer_id] = 2
	var malformed: Dictionary = _intent(peer_id, "pedestrian", Vector3(NAN, 0.0, -1.0))
	var invalid: String = _combat._validate_intent(peer_id, malformed)
	var result: Dictionary = {
		"ok": accepted.is_empty() and duplicate == "STALE_SEQUENCE" and invalid == "INVALID",
		"valid": "OK" if accepted.is_empty() else accepted,
		"duplicate": duplicate,
		"nonfinite": invalid,
	}
	_reset_validator_state()
	return result


## Builds the exact seven-field S12 host-validation intent shape.
func _intent(peer_id: int, target_id: String, direction: Vector3) -> Dictionary:
	return {
		"session": _session.session_id,
		"match": S12Combat.MATCH_REVISION,
		"sequence": _sequences[peer_id],
		"target": target_id,
		"view_usec": int(Time.get_unix_time_from_system() * 1_000_000.0),
		"direction": direction,
		"client_hit": false,
	}


## Clears only S12 validator state between the equivalence probe and measured run.
func _reset_validator_state() -> void:
	_combat.last_sequence_by_peer.clear()
	_combat.next_fire_by_peer.clear()
	_combat.magazine_by_peer.clear()
	_combat.reload_end_by_peer.clear()
	_combat.history.clear()
	_combat.history_peak_bytes = 0
	_accepted = 0
	_rejected.clear()
	_rewind_queries = 0
	for offset: int in PLAYER_COUNT:
		_sequences[FIRST_PEER_ID + offset] = 0
