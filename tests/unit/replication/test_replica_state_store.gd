extends GutTest
## Verifies stale fences, one-writer state application, and per-entity subset recovery.

var _codec: MeasuredReplicationCodec
var _session_id: String
var _store: ReplicaStateStore


## Installs two current entities before each live-state case.
func before_each() -> void:
	_codec = MeasuredReplicationCodec.new()
	_session_id = ReplicationIdentity.create_session_id()
	_store = ReplicaStateStore.new(_codec, _session_id, 1)
	var baseline: Dictionary = {
		"session_id": _session_id,
		"match_revision": 1,
		"cut_tick": 10,
		"cut_durable_revision": 0,
		"rows": [_row(1, 1, 1, 1, 0.0), _row(2, 1, 1, 1, 0.0)],
	}
	assert_true(_store.install_baseline(baseline).ok)


## Recovers alternating subsets through independent entity tick watermarks.
func test_subset_recovery_does_not_use_global_packet_watermark() -> void:
	assert_eq(_apply_rows(100, [_row(1, 1, 1, 1, 10.0)]).applied, 1)
	assert_eq(_apply_rows(101, [_row(2, 1, 1, 1, 20.0)]).applied, 1)
	assert_eq(_apply_rows(104, [_row(1, 1, 1, 1, 14.0)]).applied, 1)

	assert_almost_eq(float(_store.entity_state(1).x), 14.00435, 0.011)
	assert_almost_eq(float(_store.entity_state(1).y), 3.5, 0.011)
	assert_almost_eq(float(_store.entity_state(1).vy), -2.0, 0.001)
	assert_almost_eq(float(_store.entity_state(2).x), 20.00435, 0.011)
	assert_eq(_apply_rows(99, [_row(1, 1, 1, 1, 99.0)]).rejected, 1)
	assert_almost_eq(float(_store.entity_state(1).x), 14.00435, 0.011)


## Rejects stale durable revisions and prevents movement from undoing lifecycle phase.
func test_stale_revision_and_movement_cannot_resurrect_lifecycle() -> void:
	var death: PackedByteArray = _durable_packet(3, 2, 1, 1, 20)
	assert_true(_store.apply_durable(_session_id, 1, death).ok)
	assert_false(_store.apply_durable(_session_id, 1, death).ok)
	assert_eq(_store.durable_revision(), 1)

	var stale_motion: Dictionary = _apply_rows(30, [_row(1, 1, 1, 1, 30.0)])
	assert_eq(stale_motion.applied, 0)
	assert_eq(_store.entity_state(1).phase, 2)
	assert_almost_eq(float(_store.entity_state(1).x), 0.00435, 0.011)


## Materializes movement that arrived before its reliable spawn authorization.
func test_movement_before_spawn_recovers_from_newest_bounded_row() -> void:
	var remove: PackedByteArray = _durable_packet(2, 3, 1, 1, 20)
	assert_true(_store.apply_durable(_session_id, 1, remove).ok)
	assert_eq(_store.entity_state(1).phase, 3)

	var future: Dictionary = _apply_rows(25, [_row(1, 2, 1, 1, 25.0)])
	assert_eq(future.applied, 0)
	assert_eq(_store.pending_movement_count(), 1)
	assert_eq(_store.entity_state(1).generation, 1)

	var spawn: PackedByteArray = _durable_packet(1, 1, 2, 2, 26)
	assert_true(_store.apply_durable(_session_id, 1, spawn).ok)
	assert_eq(_store.entity_state(1).generation, 2)
	assert_eq(_store.entity_state(1).phase, 1)
	assert_almost_eq(float(_store.entity_state(1).x), 25.00435, 0.011)
	assert_eq(_store.pending_movement_count(), 0)


## Advances reliable spawn revision before its first lossy movement row arrives.
func test_spawn_before_movement_authorizes_then_materializes_entity() -> void:
	assert_true(_store.apply_durable(_session_id, 1, _durable_packet(2, 3, 1, 1, 20)).ok)
	var spawn: PackedByteArray = _durable_packet(1, 1, 2, 2, 21)
	assert_true(_store.apply_durable(_session_id, 1, spawn).ok)
	assert_eq(_store.durable_revision(), 2)
	assert_true(_store.entity_state(1).is_empty())

	var movement: Dictionary = _apply_rows(22, [_row(1, 2, 1, 1, 22.0)])
	assert_eq(movement.applied, 1)
	assert_eq(_store.entity_state(1).generation, 2)
	assert_almost_eq(float(_store.entity_state(1).x), 22.00435, 0.011)


## Keeps spawn authorization valid across another entity's intervening durable event.
func test_durable_event_between_spawn_and_movement_does_not_block_pose() -> void:
	assert_true(_store.apply_durable(_session_id, 1, _durable_packet(2, 3, 1, 1, 20)).ok)
	assert_true(_store.apply_durable(_session_id, 1, _durable_packet(1, 1, 2, 2, 21)).ok)
	var other_death: PackedByteArray = _other_durable_packet(3, 2, 1, 3, 22)
	assert_true(_store.apply_durable(_session_id, 1, other_death).ok)
	assert_eq(_store.durable_revision(), 3)

	assert_eq(_apply_rows(23, [_row(1, 2, 1, 1, 23.0)]).applied, 1)
	assert_eq(_store.entity_state(1).generation, 2)
	assert_eq(_store.entity_state(2).phase, 2)


## Requests resync on a reliable revision gap without partially applying the event.
func test_revision_gap_and_stale_envelope_fail_closed() -> void:
	var gap: PackedByteArray = _durable_packet(3, 2, 1, 2, 20)
	assert_false(_store.apply_durable(_session_id, 1, gap).ok)
	assert_true(_store.needs_resync())
	assert_eq(_store.durable_revision(), 0)
	assert_eq(_store.entity_state(1).phase, 1)

	var packet: PackedByteArray = _movement_packet(20, [_row(1, 1, 1, 1, 20.0)])
	assert_false(_store.apply_movement(_session_id, 2, packet).ok)
	assert_false(_store.apply_movement(ReplicationIdentity.create_session_id(), 1, packet).ok)


## Encodes and applies one fixed movement subset through the production codec.
func _apply_rows(tick: int, rows: Array[Dictionary]) -> Dictionary:
	return _store.apply_movement(_session_id, 1, _movement_packet(tick, rows))


## Encodes one movement packet and asserts the test row fits a single complete chunk.
func _movement_packet(tick: int, rows: Array[Dictionary]) -> PackedByteArray:
	var encoded: Dictionary = _codec.encode_movement(tick & 0xffff, tick, rows)
	assert_true(encoded.ok)
	assert_eq(encoded.packets.size(), 1)
	return encoded.packets[0]


## Encodes one reliable lifecycle event through the exact durable shape.
func _durable_packet(
	event_kind: int,
	phase: int,
	generation: int,
	revision: int,
	tick: int,
) -> PackedByteArray:
	return _encode_durable_packet(1, event_kind, phase, generation, revision, tick)


## Encodes one durable event for the second baseline entity.
func _other_durable_packet(
	event_kind: int,
	phase: int,
	generation: int,
	revision: int,
	tick: int,
) -> PackedByteArray:
	return _encode_durable_packet(2, event_kind, phase, generation, revision, tick)


## Encodes one reliable lifecycle event for the selected test entity.


# gdstyle:ignore=quality/max-parameters
func _encode_durable_packet(
	entity_id: int,
	event_kind: int,
	phase: int,
	generation: int,
	revision: int,
	tick: int,
) -> PackedByteArray:
	var encoded: Dictionary = _codec.encode_durable(
		{
			"event_kind": event_kind,
			"phase": phase,
			"id": entity_id,
			"generation": generation,
			"revision": revision,
			"tick": tick,
		}
	)
	assert_true(encoded.ok)
	return encoded.packet


## Builds one complete movement row with independently selected expected positions.
func _row(
	entity_id: int,
	generation: int,
	kind: int,
	phase: int,
	x: float,
) -> Dictionary:
	return {
		"id": entity_id,
		"generation": generation,
		"kind": kind,
		"phase": phase,
		"flags": 0,
		"x": x,
		"y": 3.5,
		"z": 200.0,
		"vx": 1.0,
		"vy": -2.0,
		"vz": 0.0,
		"yaw": 0.0,
	}
