class_name ReplicaStateStore
extends RefCounted
## Installs baselines and applies durable and movement fields through distinct writers.

const MAX_PENDING_MOVEMENT_ROWS: int = 148

var _codec: MeasuredReplicationCodec
var _session_id: String
var _match_revision: int
var _durable_revision: int = 0
var _entities: Dictionary[int, Dictionary] = {}
var _pending_movement: Dictionary[String, Dictionary] = {}
var _resync_required: bool = false


## Configures one replica for exactly one current session and match revision.
func _init(codec: MeasuredReplicationCodec, session_id: String, match_revision: int) -> void:
	_codec = codec
	_session_id = session_id
	_match_revision = match_revision


## Atomically installs a fully validated baseline before any live movement is accepted.
func install_baseline(baseline: Dictionary) -> Dictionary:
	if not _valid_baseline(baseline):
		return _failure(&"MALFORMED_BASELINE")

	var candidate: Dictionary[int, Dictionary] = {}
	for row: Dictionary in baseline.rows:
		var entity_id: int = int(row.id)
		if candidate.has(entity_id):
			return _failure(&"MALFORMED_BASELINE")
		candidate[entity_id] = _baseline_entity(row, int(baseline.cut_tick))

	_entities = candidate
	_durable_revision = int(baseline.cut_durable_revision)
	_pending_movement.clear()
	_resync_required = false
	return { "ok": true, "entity_count": _entities.size() }


## Applies one reliable lifecycle record in exact global durable revision order.
func apply_durable(
	session_id: String,
	match_revision: int,
	packet: PackedByteArray,
) -> Dictionary:
	if not _current_envelope(session_id, match_revision):
		return _failure(&"STALE_ENVELOPE")

	var event: Dictionary = _codec.decode_durable(packet)
	if not event.ok or not _valid_event_phase(event):
		return _failure(&"MALFORMED_DURABLE")
	var revision: int = int(event.revision)
	if revision <= _durable_revision:
		return _failure(&"STALE_REVISION")
	if revision != _durable_revision + 1:
		_resync_required = true
		return _failure(&"REVISION_GAP")

	var applied: Dictionary = _apply_durable_event(event)
	if not applied.ok:
		return applied

	_durable_revision = revision
	_apply_pending_for(int(event.id), int(event.generation))
	return { "ok": true, "revision": _durable_revision }


## Applies fresh motion per entity without writing lifecycle kind or phase.
func apply_movement(
	session_id: String,
	match_revision: int,
	packet: PackedByteArray,
) -> Dictionary:
	if not _current_envelope(session_id, match_revision):
		return _failure(&"STALE_ENVELOPE")

	var decoded: Dictionary = _codec.decode_movement(packet)
	if not decoded.ok:
		return decoded

	var applied_count: int = 0
	var rejected_count: int = 0
	for row: Dictionary in decoded.rows:
		if _apply_movement_row(row, int(decoded.tick)):
			applied_count += 1
		else:
			rejected_count += 1

	return {
		"ok": true,
		"applied": applied_count,
		"rejected": rejected_count,
		"resync_required": _resync_required,
	}


## Returns a defensive copy of current authoritative replica state by entity ID.
func entity_state(entity_id: int) -> Dictionary:
	return _entities.get(entity_id, {}).duplicate(true)


## Reports the last contiguous durable revision installed locally.
func durable_revision() -> int:
	return _durable_revision


## Reports whether a gap or bounded future-row overflow requires canonical resync.
func needs_resync() -> bool:
	return _resync_required


## Reports bounded future movement retained newest-per-entity rather than appended.
func pending_movement_count() -> int:
	return _pending_movement.size()


## Validates current identity and the complete assembler output shape.
func _valid_baseline(baseline: Dictionary) -> bool:
	if (
		not baseline.has("session_id")
		or not baseline.has("match_revision")
		or not baseline.has("cut_tick")
		or not baseline.has("cut_durable_revision")
		or not baseline.has("rows")
	):
		return false
	if not _current_envelope(baseline.session_id, baseline.match_revision):
		return false
	if (
		baseline.cut_tick is not int
		or baseline.cut_tick < 0
		or baseline.cut_durable_revision is not int
		or baseline.cut_durable_revision < 0
		or baseline.rows is not Array
	):
		return false

	for value: Variant in baseline.rows:
		if value is not Dictionary:
			return false
		var row: Dictionary = value
		if not ReplicationIdentity.has_valid_entity_ref_fields(row):
			return false

	return true


## Creates one state row with lifecycle and movement fields ready in dependency order.
func _baseline_entity(row: Dictionary, tick: int) -> Dictionary:
	return {
		"id": row.id,
		"generation": row.generation,
		"kind": row.kind,
		"phase": row.phase,
		"flags": row.flags,
		"x": row.x,
		"z": row.z,
		"vx": row.vx,
		"vz": row.vz,
		"yaw": row.yaw,
		"movement_tick": tick,
	}


## Applies the lifecycle owner fields while retaining tombstones after removal.
func _apply_durable_event(event: Dictionary) -> Dictionary:
	var entity_id: int = int(event.id)
	var generation: int = int(event.generation)
	var event_kind: int = int(event.event_kind)
	var current: Dictionary = _entities.get(entity_id, {})
	if not current.is_empty() and generation < int(current.generation):
		return _failure(&"STALE_GENERATION")
	if event_kind == 1:
		return _apply_spawn(event, current)
	if current.is_empty() or generation != int(current.generation):
		return _failure(&"STALE_GENERATION")

	# Durable lifecycle is the sole writer of phase; movement only confirms dependencies.
	current.phase = event.phase
	if event_kind == 2:
		current.flags = 0
		current.vx = 0.0
		current.vz = 0.0
		_pending_movement.erase(_pending_key(entity_id, generation))
	return { "ok": true }


## Installs a generation only from reliable spawn plus its complete pending movement row.
func _apply_spawn(event: Dictionary, current: Dictionary) -> Dictionary:
	var entity_id: int = int(event.id)
	var generation: int = int(event.generation)
	if not current.is_empty() and generation <= int(current.generation):
		return _failure(&"STALE_GENERATION")

	var key: String = _pending_key(entity_id, generation)
	if not _pending_movement.has(key):
		return _failure(&"MISSING_SPAWN_STATE")

	var pending: Dictionary = _pending_movement[key]
	var row: Dictionary = pending.row
	if int(row.phase) != int(event.phase):
		return _failure(&"DEPENDENCY_MISMATCH")

	_entities[entity_id] = _baseline_entity(row, int(pending.tick))
	return { "ok": true }


## Applies one row only when reliable generation and phase dependencies already match.
func _apply_movement_row(row: Dictionary, tick: int) -> bool:
	var entity_id: int = int(row.id)
	var generation: int = int(row.generation)
	var current: Dictionary = _entities.get(entity_id, {})
	if (
		current.is_empty()
		or generation > int(current.generation)
		or int(row.phase) > int(current.phase)
	):
		_queue_pending(row, tick)
		return false
	if (
		generation != int(current.generation)
		or int(row.phase) != int(current.phase)
		or int(current.phase) == 3
		or tick <= int(current.movement_tick)
	):
		return false

	current.flags = row.flags
	current.x = row.x
	current.z = row.z
	current.vx = row.vx
	current.vz = row.vz
	current.yaw = row.yaw
	current.movement_tick = tick
	return true


## Keeps at most the newest future row per entity generation under a fixed global cap.
func _queue_pending(row: Dictionary, tick: int) -> void:
	var key: String = _pending_key(int(row.id), int(row.generation))
	if _pending_movement.has(key):
		if tick > int(_pending_movement[key].tick):
			_pending_movement[key] = { "row": row.duplicate(true), "tick": tick }
		return
	if _pending_movement.size() >= MAX_PENDING_MOVEMENT_ROWS:
		_resync_required = true
		return

	_pending_movement[key] = { "row": row.duplicate(true), "tick": tick }


## Applies and removes one future row after its reliable dependency is installed.
func _apply_pending_for(entity_id: int, generation: int) -> void:
	var key: String = _pending_key(entity_id, generation)
	if not _pending_movement.has(key):
		return

	var pending: Dictionary = _pending_movement[key]
	_pending_movement.erase(key)
	_apply_movement_row(pending.row, int(pending.tick))


## Maps each accepted durable kind to its frozen S11 lifecycle phase.
func _valid_event_phase(event: Dictionary) -> bool:
	var event_kind: int = int(event.event_kind)
	var phase: int = int(event.phase)
	return (
		(event_kind == 1 and phase == 1)
		or (event_kind == 2 and phase == 3)
		or (event_kind in [3, 4] and phase == 2)
	)


## Checks the sideband session and match fence associated with the fixed measured packet.
func _current_envelope(session_id: Variant, match_revision: Variant) -> bool:
	return ReplicationIdentity.is_current_envelope(
		session_id,
		match_revision,
		_session_id,
		_match_revision,
	)


## Builds one stable pending-row key without relying on a scene node identity.
func _pending_key(entity_id: int, generation: int) -> String:
	return "%d:%d" % [entity_id, generation]


## Returns one normalized state-apply failure without partial packet fields.
func _failure(code: StringName) -> Dictionary:
	return { "ok": false, "failure": { "code": code } }
