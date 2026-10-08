class_name S03Replication
extends Node

signal baseline_installed(baseline_id: int)
signal handoff_confirmed(peer_id: int, baseline_id: int)
signal admission_received()
signal held_result(reason: String, sequence: int)
signal snapshot_requested(peer_id: int)

const MAX_BASELINE_BYTES: int = 8192
const CHUNK_COUNT: int = 2
const MAX_HELD_BYTES: int = 1200
const HELD_BURST: int = 8
const HELD_RATE: float = 60.0

var match_state: S03Match
var resolve_participant: Callable
var next_baseline: int = 0
var pending: Dictionary = {}
var receiving: Dictionary = {}
var hold_ack: bool = false
var last_baseline: int = 0
var rate: Dictionary = {}
var movement_received: int = 0
var baseline_bytes: int = 0
var max_movement_bytes: int = 0
var max_held_bytes: int = 0


## Capture a bounded immutable cut, then record a durable change during loading.
func begin(peer_id: int, participant: int) -> void:
	next_baseline += 1
	var data: Dictionary = match_state.baseline(participant, next_baseline)
	var bytes: PackedByteArray = JSON.stringify(data).to_utf8_buffer()
	baseline_bytes = maxi(baseline_bytes, bytes.size())
	assert(bytes.size() <= MAX_BASELINE_BYTES)
	pending[peer_id] = {"id": next_baseline, "participant": participant,
		"revision": match_state.durable_revision + 1, "health": 70, "stage": "BASELINE"}
	# The fixture change still commits through the sole state owner.
	var journal_applied: bool = match_state.apply_journal(
		participant, 70, match_state.durable_revision + 1
	)
	assert(journal_applied)
	_start.rpc_id(
		peer_id,
		match_state.session_id,
		next_baseline,
		bytes.size(),
		bytes.hex_encode().sha256_text(),
	)
	var midpoint: int = bytes.size() / CHUNK_COUNT
	_chunk.rpc_id(peer_id, match_state.session_id, next_baseline, 0, bytes.slice(0, midpoint))
	_chunk.rpc_id(peer_id, match_state.session_id, next_baseline, 1, bytes.slice(midpoint))


## Start only a fresh bounded transfer from the authority.
@rpc("authority", "call_remote", "reliable", 1)
func _start(session: String, baseline_id: int, byte_count: int, checksum: String) -> void:
	if multiplayer.is_server() or session != match_state.session_id:
		return

	if byte_count <= 0 or byte_count > MAX_BASELINE_BYTES or baseline_id <= last_baseline:
		return

	receiving = { "id": baseline_id, "bytes": byte_count, "checksum": checksum, "chunks": {} }


## Install a complete checksummed baseline before sending application acknowledgement.
@rpc("authority", "call_remote", "reliable", 1)
func _chunk(session: String, baseline_id: int, index: int, bytes: PackedByteArray) -> void:
	if session != match_state.session_id or receiving.get("id") != baseline_id:
		return

	if index < 0 or index >= CHUNK_COUNT or bytes.size() > MAX_BASELINE_BYTES / CHUNK_COUNT:
		return

	receiving.chunks[index] = bytes
	if receiving.chunks.size() != CHUNK_COUNT:
		return

	var payload: PackedByteArray = receiving.chunks[0] + receiving.chunks[1]
	if (payload.size() != receiving.bytes
			or payload.hex_encode().sha256_text() != receiving.checksum):
		return

	var data: Variant = JSON.parse_string(payload.get_string_from_utf8())
	if not data is Dictionary or not match_state.apply_baseline(data):
		return

	last_baseline = baseline_id
	receiving.clear()
	baseline_installed.emit(baseline_id)
	if not hold_ack:
		_applied.rpc_id(1, session, baseline_id)


## Publish the journal and marker only for the sender's current baseline.
@rpc("any_peer", "call_remote", "reliable", 1)
func _applied(session: String, baseline_id: int) -> void:
	if not multiplayer.is_server() or session != match_state.session_id:
		return

	var peer_id: int = multiplayer.get_remote_sender_id()
	if not pending.has(peer_id):
		return

	var transfer: Dictionary = pending[peer_id]
	if transfer.id != baseline_id or transfer.stage != "BASELINE":
		return

	transfer.stage = "HANDOFF"
	_handoff.rpc_id(peer_id, session, baseline_id, transfer.participant,
		transfer.health, transfer.revision)


## Apply the reliable durable journal before acknowledging its handoff marker.
@rpc("authority", "call_remote", "reliable", 1)
func _handoff(
	session: String,
	baseline_id: int,
	participant: int,
	health: int,
	revision: int,
) -> void:
	if session != match_state.session_id or baseline_id != last_baseline:
		return

	if not match_state.apply_journal(participant, health, revision):
		return

	_marker_ack.rpc_id(1, session, baseline_id, revision)


## Admit only a matching completed handoff; obsolete acknowledgements have no effect.
@rpc("any_peer", "call_remote", "reliable", 1)
func _marker_ack(session: String, baseline_id: int, revision: int) -> void:
	if not multiplayer.is_server() or session != match_state.session_id:
		return

	var peer_id: int = multiplayer.get_remote_sender_id()
	if not pending.has(peer_id):
		return

	var transfer: Dictionary = pending[peer_id]
	if transfer.id != baseline_id or transfer.revision != revision or transfer.stage != "HANDOFF":
		return

	pending.erase(peer_id)
	handoff_confirmed.emit(peer_id, baseline_id)


## Publish the admission grant and a fresh movement row on separate streams.
func grant(peer_id: int, participant: int, baseline_id: int) -> void:
	_grant.rpc_id(peer_id, match_state.session_id, baseline_id, match_state.durable_revision)
	send_movement(peer_id, [participant], 1, 0.0)


## Record admission; input still waits for a fresh movement row.
@rpc("authority", "call_remote", "reliable", 1)
func _grant(session: String, baseline_id: int, revision: int) -> void:
	if session != match_state.session_id or baseline_id != last_baseline:
		return

	if revision != match_state.durable_revision:
		return

	match_state.admit(match_state.participant_id)
	admission_received.emit()
	_try_enable_input()


## Enable controls after both grant and matching revision-gated movement.
func _try_enable_input() -> void:
	var participant: int = match_state.participant_id
	if not match_state.bindings.has(participant):
		return

	var binding: Dictionary = match_state.bindings[participant]
	if binding.admitted and match_state.motion_ticks.has(int(binding.entity)):
		match_state.enable_local()


## Send independently replaceable entity rows on the proposed ordered stream.
func send_movement(peer_id: int, participants: Array, tick: int, sample: float) -> void:
	var rows: Array = []
	for participant: int in participants:
		var binding: Dictionary = match_state.bindings[participant]
		rows.append({"entity": binding.entity, "tick": tick, "control": binding.control,
			"durable": match_state.durable_revision, "sample": sample})

	var envelope: Dictionary = {
		"session": match_state.session_id, "revision": 1, "rows": rows,
	}
	max_movement_bytes = maxi(max_movement_bytes, var_to_bytes(envelope).size())
	assert(max_movement_bytes <= MAX_HELD_BYTES)
	_movement.rpc_id(peer_id, envelope)


## Apply per-entity motion watermarks across subset packets.
@rpc("authority", "call_remote", "unreliable_ordered", 3)
func _movement(envelope: Dictionary) -> void:
	movement_received += 1
	if match_state.apply_movement(envelope):
		_try_enable_input()


## Submit one held frame through the same network boundary used by clients.
func send_held(envelope: Dictionary) -> void:
	_held.rpc_id(1, envelope)


## Bound serialized receipt and rate before sender-bound intent validation.
@rpc("any_peer", "call_remote", "unreliable_ordered", 2)
func _held(envelope: Variant) -> void:
	if not multiplayer.is_server():
		return

	var peer_id: int = multiplayer.get_remote_sender_id()
	var participant: int = int(resolve_participant.call(peer_id))
	max_held_bytes = maxi(max_held_bytes, var_to_bytes(envelope).size())
	if not rate.has(peer_id):
		rate[peer_id] = { "tokens": float(HELD_BURST), "time": Time.get_ticks_msec() }

	var bucket: Dictionary = rate[peer_id]
	var now: int = Time.get_ticks_msec()
	bucket.tokens = minf(HELD_BURST, bucket.tokens + (now - bucket.time) * HELD_RATE / 1000.0)
	bucket.time = now
	var reason: String = "RATE_LIMIT"
	if bucket.tokens >= 1.0:
		bucket.tokens -= 1.0
		reason = "INVALID"
		if var_to_bytes(envelope).size() <= MAX_HELD_BYTES:
			reason = match_state.submit_held(participant, envelope)

	var sequence: int = -1
	if envelope is Dictionary and envelope.get("sequence") is int:
		sequence = envelope.sequence

	_result.rpc_id(peer_id, reason, sequence)


## Expose command outcomes to observers without acknowledging unconsumed simulation.
@rpc("authority", "call_remote", "reliable", 0)
func _result(reason: String, sequence: int) -> void:
	held_result.emit(reason, sequence)


## Drop disconnected transfer/rate work.
func forget(peer_id: int) -> void:
	pending.erase(peer_id)
	rate.erase(peer_id)


## Clear all attempt-specific receipt buffers and identities.
func clear() -> void:
	pending.clear()
	receiving.clear()
	rate.clear()
	last_baseline = 0


## Ask the host fixture coordinator for a split-snapshot experiment.
func request_snapshots() -> void:
	_snapshot_request.rpc_id(1, match_state.session_id)


## Forward an admitted sender request without giving the client state-writing authority.
@rpc("any_peer", "call_remote", "reliable", 0)
func _snapshot_request(session: String) -> void:
	if not multiplayer.is_server() or session != match_state.session_id:
		return

	var peer_id: int = multiplayer.get_remote_sender_id()
	var participant: int = int(resolve_participant.call(peer_id))
	if match_state.bindings.has(participant) and match_state.bindings[participant].admitted:
		snapshot_requested.emit(peer_id)
