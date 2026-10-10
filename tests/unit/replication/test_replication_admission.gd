extends GutTest
## Verifies bounded current-state transfer, journal order, and sender-derived input gating.

const NATIVE_PEER_ID: int = 22
const BASELINE_ID: int = 71

var _codec: MeasuredReplicationCodec
var _transport: FakeReplicationTransport
var _identities: PeerIdentityRegistry
var _admission: ReplicationAdmission
var _session_id: String


## Builds one admitted sender and injected fake transport per case.
func before_each() -> void:
	_codec = MeasuredReplicationCodec.new()
	_transport = FakeReplicationTransport.new()
	_identities = PeerIdentityRegistry.new()
	_session_id = ReplicationIdentity.create_session_id()
	assert_true(_identities.bind_peer(NATIVE_PEER_ID, 2).ok)
	_admission = ReplicationAdmission.new(
		_codec,
		_transport,
		_identities,
		_session_id,
		1,
	)


## Sends current state, journal, marker, then grant while input stays closed beforehand.
func test_baseline_and_journal_complete_before_input_grant() -> void:
	var started: Dictionary = _admission.start(NATIVE_PEER_ID, BASELINE_ID, 40, [_row(1)])
	assert_true(started.ok)
	assert_eq(_transport.events[0].kind, &"baseline")
	assert_eq(_admission.input_participant(NATIVE_PEER_ID), 0)

	assert_true(_admission.publish_durable(_event(1, 41)).ok)
	assert_eq(_transport.events.size(), 1)

	var baseline_ack: Dictionary = _admission.acknowledge_baseline(
		NATIVE_PEER_ID,
		BASELINE_ID,
	)
	assert_true(baseline_ack.ok)
	assert_eq(_transport.events[1].kind, &"durable")
	assert_eq(_transport.events[2].kind, &"handoff")
	assert_eq(_admission.input_participant(NATIVE_PEER_ID), 0)

	assert_true(_admission.publish_durable(_event(2, 42)).ok)
	assert_eq(_transport.events.size(), 3)
	assert_false(_admission.acknowledge_handoff(NATIVE_PEER_ID, BASELINE_ID, 0).ok)
	assert_eq(_admission.input_participant(NATIVE_PEER_ID), 0)
	var repeated_handoff: Dictionary = _admission.acknowledge_handoff(
		NATIVE_PEER_ID,
		BASELINE_ID,
		1,
	)
	assert_true(repeated_handoff.ok)
	assert_false(repeated_handoff.admitted)
	assert_eq(_transport.events[3].kind, &"durable")
	assert_eq(_transport.events[4].kind, &"handoff")
	assert_eq(_admission.input_participant(NATIVE_PEER_ID), 0)

	var granted: Dictionary = _admission.acknowledge_handoff(NATIVE_PEER_ID, BASELINE_ID, 2)
	assert_true(granted.ok)
	assert_true(granted.admitted)
	assert_eq(_transport.events[5].kind, &"grant")
	assert_gt(_admission.input_participant(NATIVE_PEER_ID), 0)


## Rejects unmapped senders and old acknowledgements without opening input.
func test_sender_mapping_and_baseline_id_fence_acknowledgements() -> void:
	assert_false(_admission.start(999, BASELINE_ID, 40, [_row(1)]).ok)
	assert_true(_admission.start(NATIVE_PEER_ID, BASELINE_ID, 40, [_row(1)]).ok)
	assert_false(_admission.acknowledge_baseline(999, BASELINE_ID).ok)
	assert_false(_admission.acknowledge_baseline(NATIVE_PEER_ID, BASELINE_ID - 1).ok)
	assert_eq(_admission.input_participant(NATIVE_PEER_ID), 0)


## Reassembles out-of-order chunks, ignores identical duplicates, and validates checksum.
func test_baseline_assembler_exposes_only_complete_validated_rows() -> void:
	var rows: Array[Dictionary] = []
	for entity_id: int in range(1, 149):
		rows.append(_row(entity_id))
	var started: Dictionary = _admission.start(NATIVE_PEER_ID, BASELINE_ID, 40, rows)
	var transfer: Dictionary = _transport.events[0]
	var assembler := BaselineAssembler.new()

	assert_true(assembler.begin(_codec, transfer.metadata).ok)
	assert_false(assembler.is_complete())
	assert_true(
		assembler.receive(_session_id, 1, BASELINE_ID, transfer.packets[1]).ok,
	)
	var duplicate: Dictionary = assembler.receive(
		_session_id,
		1,
		BASELINE_ID,
		transfer.packets[1],
	)
	assert_true(duplicate.ok)
	assert_true(duplicate.duplicate)
	assert_false(assembler.receive(_session_id, 2, BASELINE_ID, transfer.packets[0]).ok)
	assert_true(
		assembler.receive(_session_id, 1, BASELINE_ID, transfer.packets[0]).ok,
	)

	var finished: Dictionary = assembler.finish()
	assert_true(started.ok)
	assert_true(finished.ok)
	assert_eq(finished.rows.size(), 148)
	assert_eq(finished.cut_durable_revision, 0)


## Closes only an admitted peer whose reliable durable send fails.
func test_admitted_durable_send_failure_closes_input_while_other_peer_continues() -> void:
	const OTHER_PEER_ID: int = 23
	assert_true(_identities.bind_peer(OTHER_PEER_ID, 3).ok)
	assert_true(_admission.start(NATIVE_PEER_ID, BASELINE_ID, 40, [_row(1)]).ok)
	assert_true(_admission.start(OTHER_PEER_ID, BASELINE_ID + 1, 40, [_row(1)]).ok)
	assert_true(_admission.acknowledge_baseline(NATIVE_PEER_ID, BASELINE_ID).ok)
	assert_true(_admission.acknowledge_baseline(OTHER_PEER_ID, BASELINE_ID + 1).ok)
	assert_true(_admission.acknowledge_handoff(NATIVE_PEER_ID, BASELINE_ID, 0).ok)
	assert_true(_admission.acknowledge_handoff(OTHER_PEER_ID, BASELINE_ID + 1, 0).ok)

	_transport.fail_durable_peer = NATIVE_PEER_ID
	assert_true(_admission.publish_durable(_event(1, 41)).ok)
	assert_eq(_admission.input_participant(NATIVE_PEER_ID), 0)
	assert_eq(_admission.input_participant(OTHER_PEER_ID), 3)
	assert_true(_has_event(&"abort", NATIVE_PEER_ID))
	assert_true(_has_event(&"durable", OTHER_PEER_ID))


## Aborts only one expired admission and never converts timeout into a grant.
func test_admission_timeout_clears_attempt_and_input() -> void:
	assert_true(_admission.start(NATIVE_PEER_ID, BASELINE_ID, 40, [_row(1)]).ok)
	_admission.expire_attempts(
		Time.get_ticks_msec() + ReplicationAdmission.BASELINE_TIMEOUT_MSEC,
	)

	assert_eq(_transport.events.back().kind, &"abort")
	assert_eq(_transport.events.back().code, &"SYNC_TIMEOUT")
	assert_eq(_admission.input_participant(NATIVE_PEER_ID), 0)


## Applies the shorter handoff deadline after a baseline acknowledgement.
func test_handoff_timeout_clears_attempt_without_grant() -> void:
	assert_true(_admission.start(NATIVE_PEER_ID, BASELINE_ID, 40, [_row(1)]).ok)
	assert_true(_admission.acknowledge_baseline(NATIVE_PEER_ID, BASELINE_ID).ok)
	_admission.expire_attempts(
		Time.get_ticks_msec() + ReplicationAdmission.HANDOFF_TIMEOUT_MSEC,
	)

	assert_eq(_transport.events.back().kind, &"abort")
	assert_eq(_transport.events.back().code, &"SYNC_TIMEOUT")
	assert_eq(_admission.input_participant(NATIVE_PEER_ID), 0)


## Reports whether the fake transport observed one kind for a specific peer.
func _has_event(kind: StringName, native_peer_id: int) -> bool:
	for event: Dictionary in _transport.events:
		if event.kind == kind and int(event.peer) == native_peer_id:
			return true
	return false


## Builds one current baseline row independent of transfer ordering.
func _row(entity_id: int) -> Dictionary:
	return {
		"id": entity_id,
		"generation": 1,
		"kind": 1,
		"phase": 1,
		"flags": 0,
		"x": float(entity_id),
		"z": 200.0,
		"vx": 0.0,
		"vz": 0.0,
		"yaw": 0.0,
	}


## Builds one reliable lifecycle record after the baseline cut.
func _event(revision: int, tick: int) -> Dictionary:
	return {
		"event_kind": 3,
		"phase": 2,
		"id": 1,
		"generation": 1,
		"revision": revision,
		"tick": tick,
	}
