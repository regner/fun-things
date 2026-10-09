class_name S04Replication
extends S03Replication
## Extends the existing S03 RPC writer with actual poses; provider/admission stay unchanged.

signal exit_result(reason: String)
signal exit_rate_notified(peer_id: int)

const EXIT_BURST: float = 2.0
const EXIT_RATE: float = 1.0

var exit_pending: bool = false
var next_exit_request: int = 0
var exit_rate: Dictionary = {}


## Builds a movement envelope including binding-independent coasting vehicles.
func movement_envelope(participants: Array) -> Dictionary:
	var actual: S04Match = match_state as S04Match
	var rows: Array = []
	for participant: int in participants:
		rows.append(actual.pose_for_entity(int(actual.bindings[participant].entity)))
	for entity: int in actual.coasting_entities():
		rows.append(actual.pose_for_entity(entity))
	return { "session": actual.session_id, "revision": 1, "rows": rows }


## Sends complete refreshed actual movement rows within the original message budget.
func send_movement(peer_id: int, participants: Array, _tick: int, _sample: float) -> void:
	var envelope: Dictionary = movement_envelope(participants)
	max_movement_bytes = maxi(max_movement_bytes, var_to_bytes(envelope).size())
	assert(max_movement_bytes <= MAX_HELD_BYTES)
	_movement.rpc_id(peer_id, envelope)


## Sends at most one authoritative seat-exit request until its matching verdict arrives.
func request_exit() -> bool:
	var request_id: int = _begin_exit_request()
	if request_id == 0:
		return false

	_request_exit.rpc_id(1, match_state.session_id, request_id)
	return true


## Reserves one bounded client request identity without changing predicted ownership.
func _begin_exit_request() -> int:
	if exit_pending:
		return 0

	next_exit_request += 1
	exit_pending = true
	return next_exit_request


## Consumes a small per-peer token bucket before any authoritative exit work or reply.
func _allow_exit_request(peer_id: int, now_ms: int) -> bool:
	if not exit_rate.has(peer_id):
		exit_rate[peer_id] = { "tokens": EXIT_BURST, "time": now_ms, "notified": false }

	var bucket: Dictionary = exit_rate[peer_id]
	bucket.tokens = minf(
		EXIT_BURST, bucket.tokens + (now_ms - int(bucket.time)) * EXIT_RATE / 1000.0
	)
	bucket.time = now_ms
	if bucket.tokens < 1.0:
		return false

	bucket.tokens -= 1.0
	bucket.notified = false
	return true


## Reserves at most one denied-request notification until the bucket next admits work.
func _take_exit_rate_notification(peer_id: int) -> bool:
	if not exit_rate.has(peer_id) or exit_rate[peer_id].notified:
		return false

	exit_rate[peer_id].notified = true
	return true


## Derives the sender and rate-bounds the host-owned exit verdict.
@rpc("any_peer", "call_remote", "reliable", 0)
func _request_exit(session: String, request_id: int) -> void:
	if not multiplayer.is_server() or session != match_state.session_id or request_id <= 0:
		return

	var peer_id: int = multiplayer.get_remote_sender_id()
	if not _allow_exit_request(peer_id, Time.get_ticks_msec()):
		if _take_exit_rate_notification(peer_id):
			exit_rate_notified.emit(peer_id)
			_exit_result.rpc_id(peer_id, request_id, "RATE_LIMIT")
		return

	var participant: int = int(resolve_participant.call(peer_id))
	var reason: String = (match_state as S04Match).request_exit(participant)
	_exit_result.rpc_id(peer_id, request_id, reason)


## Applies successful lifecycle state before publishing the matching verdict.
@rpc("authority", "call_remote", "reliable", 0)
func _exit_result(request_id: int, reason: String) -> void:
	if not exit_pending or request_id != next_exit_request:
		return

	exit_pending = false
	if reason == "OK":
		(match_state as S04Match).apply_local_exit()
	exit_result.emit(reason)


## Drops disconnected exit-rate work alongside inherited replication buffers.
func forget(peer_id: int) -> void:
	super.forget(peer_id)
	exit_rate.erase(peer_id)


## Clears attempt-local request and rate state during session teardown.
func clear() -> void:
	super.clear()
	exit_pending = false
	next_exit_request = 0
	exit_rate.clear()
