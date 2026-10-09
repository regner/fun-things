class_name ReplicationAdmission
extends RefCounted
## Owns bounded baseline, durable journal, handoff, and sender-derived input admission.

const MAX_JOURNAL_BYTES: int = 2 * 1024 * 1024
const MAX_JOURNAL_RECORDS: int = 4096
const ADMISSION_TIMEOUT_MSEC: int = 15_000
const PHASE_BASELINE: StringName = &"BASELINE"
const PHASE_HANDOFF: StringName = &"HANDOFF"
const PHASE_ADMITTED: StringName = &"ADMITTED"

var _codec: MeasuredReplicationCodec
var _transport: ReplicationTransport
var _identities: PeerIdentityRegistry
var _session_id: String
var _match_revision: int
var _durable_revision: int = 0
var _attempt_by_peer: Dictionary[int, Dictionary] = {}


## Configures one match-local admission owner with injected transport and sender registry.
func _init(
	codec: MeasuredReplicationCodec,
	transport: ReplicationTransport,
	identities: PeerIdentityRegistry,
	session_id: String,
	match_revision: int,
) -> void:
	_codec = codec
	_transport = transport
	_identities = identities
	_session_id = session_id
	_match_revision = match_revision


## Captures and sends one immutable current-state baseline while input remains closed.
func start(
	native_peer_id: int,
	baseline_id: int,
	cut_tick: int,
	rows: Array[Dictionary],
) -> Dictionary:
	if (
		_identities.resolve_sender(native_peer_id) == 0
		or baseline_id <= 0
		or cut_tick < 0
		or _attempt_by_peer.has(native_peer_id)
	):
		return _failure(&"INVALID_ADMISSION")

	var encoded: Dictionary = _codec.encode_movement(baseline_id & 0xffff, cut_tick, rows)
	if not encoded.ok:
		return encoded
	var packets: Array[PackedByteArray] = encoded.packets
	if packets.size() > BaselineAssembler.MAX_BASELINE_CHUNKS:
		return _failure(&"STATE_LIMIT")

	var metadata: Dictionary = _baseline_metadata(baseline_id, cut_tick, rows.size(), packets)
	if metadata.is_empty():
		return _failure(&"STATE_LIMIT")
	_attempt_by_peer[native_peer_id] = {
		"baseline_id": baseline_id,
		"phase": PHASE_BASELINE,
		"cut_revision": _durable_revision,
		"commit_revision": -1,
		"journal": [],
		"journal_bytes": 0,
		"sent_journal_count": 0,
		"deadline_msec": Time.get_ticks_msec() + ADMISSION_TIMEOUT_MSEC,
	}
	if not _transport.send_baseline(native_peer_id, metadata, packets):
		_abort(native_peer_id, &"TRANSPORT_FAILED")
		return _failure(&"TRANSPORT_FAILED")

	return { "ok": true, "metadata": metadata }


## Appends one ordered durable transition and bounds every active admission journal.
func publish_durable(event: Dictionary) -> Dictionary:
	var encoded: Dictionary = _codec.encode_durable(event)
	if not encoded.ok:
		return encoded
	if int(event.revision) != _durable_revision + 1:
		return _failure(&"STALE_REVISION")

	_durable_revision = int(event.revision)
	var packet: PackedByteArray = encoded.packet
	for native_peer_id: int in _attempt_by_peer.keys():
		var attempt: Dictionary = _attempt_by_peer[native_peer_id]
		if attempt.phase == PHASE_ADMITTED:
			_transport.send_durable(native_peer_id, packet)
			continue
		if not _append_journal(attempt, packet):
			_abort(native_peer_id, &"STATE_LIMIT")

	return { "ok": true, "revision": _durable_revision }


## Handles a baseline acknowledgement only from its mapped native sender.
func acknowledge_baseline(native_peer_id: int, baseline_id: int) -> Dictionary:
	var attempt: Dictionary = _current_attempt(native_peer_id, baseline_id, PHASE_BASELINE)
	if attempt.is_empty():
		return _failure(&"STALE_ACK")

	if not _send_unsent_journal(native_peer_id, attempt):
		_abort(native_peer_id, &"TRANSPORT_FAILED")
		return _failure(&"TRANSPORT_FAILED")
	attempt.phase = PHASE_HANDOFF
	attempt.commit_revision = _durable_revision
	if not _transport.send_handoff(native_peer_id, baseline_id, _durable_revision):
		_abort(native_peer_id, &"TRANSPORT_FAILED")
		return _failure(&"TRANSPORT_FAILED")

	return { "ok": true, "commit_revision": _durable_revision }


## Opens commands only after the sender acknowledges the current reliable marker.
func acknowledge_handoff(
	native_peer_id: int,
	baseline_id: int,
	commit_revision: int,
) -> Dictionary:
	var attempt: Dictionary = _current_attempt(native_peer_id, baseline_id, PHASE_HANDOFF)
	if attempt.is_empty() or int(attempt.commit_revision) != commit_revision:
		return _failure(&"STALE_ACK")
	if int(attempt.sent_journal_count) < attempt.journal.size():
		if not _send_unsent_journal(native_peer_id, attempt):
			_abort(native_peer_id, &"TRANSPORT_FAILED")
			return _failure(&"TRANSPORT_FAILED")
		attempt.commit_revision = _durable_revision
		if not _transport.send_handoff(native_peer_id, baseline_id, _durable_revision):
			_abort(native_peer_id, &"TRANSPORT_FAILED")
			return _failure(&"TRANSPORT_FAILED")

		return { "ok": true, "admitted": false, "commit_revision": _durable_revision }

	attempt.phase = PHASE_ADMITTED
	if not _transport.send_grant(native_peer_id, baseline_id, commit_revision):
		_abort(native_peer_id, &"TRANSPORT_FAILED")
		return _failure(&"TRANSPORT_FAILED")

	return {
		"ok": true,
		"admitted": true,
		"participant_id": _identities.resolve_sender(native_peer_id),
		"commit_revision": commit_revision,
	}


## Resolves command identity from the sender and rejects every pre-handoff phase.
func input_participant(native_peer_id: int) -> int:
	var participant_id: int = _identities.resolve_sender(native_peer_id)
	if participant_id == 0 or not _attempt_by_peer.has(native_peer_id):
		return 0

	var attempt: Dictionary = _attempt_by_peer[native_peer_id]
	return participant_id if attempt.phase == PHASE_ADMITTED else 0


## Aborts only expired attempts without pausing admitted peers or host simulation.
func expire_attempts(now_msec: int) -> void:
	for native_peer_id: int in _attempt_by_peer.keys():
		var attempt: Dictionary = _attempt_by_peer[native_peer_id]
		if attempt.phase != PHASE_ADMITTED and now_msec >= int(attempt.deadline_msec):
			_abort(native_peer_id, &"SYNC_TIMEOUT")


## Retires one peer's bounded transfer and journal on disconnect or cancellation.
func remove_peer(native_peer_id: int) -> void:
	_attempt_by_peer.erase(native_peer_id)
	_identities.remove_peer(native_peer_id)


## Builds bounded transaction metadata and one checksum over chunks in wire order.
func _baseline_metadata(
	baseline_id: int,
	cut_tick: int,
	row_count: int,
	packets: Array[PackedByteArray],
) -> Dictionary:
	var total_bytes: int = 0
	var checksum_context := HashingContext.new()
	if checksum_context.start(HashingContext.HASH_SHA256) != OK:
		return {}
	for packet: PackedByteArray in packets:
		total_bytes += packet.size()
		checksum_context.update(packet)
	if total_bytes > BaselineAssembler.MAX_BASELINE_BYTES:
		return {}

	return {
		"session_id": _session_id,
		"match_revision": _match_revision,
		"baseline_id": baseline_id,
		"cut_tick": cut_tick,
		"cut_durable_revision": _durable_revision,
		"chunk_count": packets.size(),
		"total_bytes": total_bytes,
		"row_count": row_count,
		"checksum": checksum_context.finish().hex_encode(),
	}


## Sends only records not covered by the previous reliable handoff marker.
func _send_unsent_journal(native_peer_id: int, attempt: Dictionary) -> bool:
	var journal: Array = attempt.journal
	for index: int in range(int(attempt.sent_journal_count), journal.size()):
		if not _transport.send_durable(native_peer_id, journal[index]):
			return false
	attempt.sent_journal_count = journal.size()
	return true


## Adds one record by value and rejects count or byte overflow before mutation.
func _append_journal(attempt: Dictionary, packet: PackedByteArray) -> bool:
	var journal: Array = attempt.journal
	if (
		journal.size() >= MAX_JOURNAL_RECORDS
		or int(attempt.journal_bytes) + packet.size() > MAX_JOURNAL_BYTES
	):
		return false

	journal.append(packet.duplicate())
	attempt.journal_bytes = int(attempt.journal_bytes) + packet.size()
	return true


## Finds an attempt only after resolving the native sender and all current fences.
func _current_attempt(
	native_peer_id: int,
	baseline_id: int,
	expected_phase: StringName,
) -> Dictionary:
	if _identities.resolve_sender(native_peer_id) == 0:
		return {}
	if not _attempt_by_peer.has(native_peer_id):
		return {}

	var attempt: Dictionary = _attempt_by_peer[native_peer_id]
	if int(attempt.baseline_id) != baseline_id or attempt.phase != expected_phase:
		return {}

	return attempt


## Clears one failed admission and reports its normalized reason through the transport.
func _abort(native_peer_id: int, failure_code: StringName) -> void:
	_attempt_by_peer.erase(native_peer_id)
	_transport.abort_admission(native_peer_id, failure_code)


## Returns one normalized admission failure without changing another peer.
func _failure(code: StringName) -> Dictionary:
	return { "ok": false, "failure": { "code": code } }
