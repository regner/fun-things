class_name S03Match
extends Node3D

const SEQUENCE_WINDOW: int = 120
const HELD_EXPIRY_MS: int = 250
const MAX_ENTITIES: int = 4
const ENTITY_SCENE: String = "res://tests/fixtures/s03/entity.tscn"
const RIG_SCENE: String = "res://tests/fixtures/s03/local_rig.tscn"

var authoritative: bool = false
var session_id: String = ""
var participant_id: int = 0
var entities: Dictionary = {}
var bindings: Dictionary = {}
var motion_ticks: Dictionary = {}
var next_entity_id: int = 0
var rig: Node
var durable_revision: int = 1
var accepted_count: int = 0
var rejected: Dictionary = {}
var removed_count: int = 0


## Consume replaceable intent at fixed ticks, then advance acknowledgements.
func _physics_process(_delta: float) -> void:
	if not authoritative:
		return

	for participant: int in bindings:
		var binding: Dictionary = bindings[participant]
		if not binding.admitted:
			continue

		if Time.get_ticks_msec() - int(binding.receipt_ms) > HELD_EXPIRY_MS:
			binding.held = 0.0

		if binding.pending > binding.sequence:
			binding.sequence = binding.pending
			binding.sample = binding.held
			accepted_count += 1


## Create one provisional player; repeated readiness cannot create another.
func prepare_initial(participant: int) -> int:
	if bindings.has(participant):
		return int(bindings[participant].entity)

	next_entity_id += 1
	var entity: int = next_entity_id
	_create_entity(entity)
	bindings[participant] = {"entity": entity, "generation": 1, "life": 1,
		"control": 1, "health": 75, "admitted": false, "sequence": 0,
		"pending": 0, "held": 0.0, "receipt_ms": 0, "sample": 0.0}
	return entity


## Configure saved entity scenes off-tree, including replica ownership.
func _create_entity(entity: int) -> void:
	var packed: PackedScene = load(ENTITY_SCENE) as PackedScene
	var actor: S03Entity = packed.instantiate() as S03Entity
	actor.name = "e_%d_g_1" % entity
	actor.authoritative = authoritative
	actor.entity_id = entity
	actor.configured = true
	$RuntimeEntities.add_child(actor)
	entities[entity] = actor


## Remove provisional/admitted state idempotently on disconnect.
func rollback(participant: int) -> void:
	if not bindings.has(participant):
		return

	var entity: int = int(bindings[participant].entity)
	if entities.has(entity):
		entities[entity].queue_free()
		entities.erase(entity)
		removed_count += 1

	bindings.erase(participant)
	motion_ticks.erase(entity)


## Rebind input without changing entity, life or injured health.
func prepare_resync(participant: int) -> void:
	var binding: Dictionary = bindings[participant]
	binding.admitted = false
	binding.control += 1
	binding.sequence = 0
	binding.pending = 0
	binding.held = 0.0
	durable_revision += 1


## Capture an immutable tiny current-state cut.
func baseline(participant: int, baseline_id: int) -> Dictionary:
	var rows: Array = []
	for key: int in bindings:
		var binding: Dictionary = bindings[key]
		rows.append({"participant": key, "entity": binding.entity,
			"generation": binding.generation, "life": binding.life,
			"control": binding.control, "health": binding.health})

	return {"session": session_id, "revision": 1, "baseline": baseline_id,
		"participant": participant, "durable": durable_revision, "rows": rows}


## Validate complete baseline data before changing the replica.
func apply_baseline(data: Dictionary) -> bool:  # gdstyle:ignore=quality/max-returns
	# Full preflight validation is deliberately fail-fast and atomic.
	if data.get("session") != session_id or data.get("revision") != 1:
		return false

	var rows: Variant = data.get("rows")
	if not rows is Array or rows.is_empty() or rows.size() > MAX_ENTITIES:
		return false

	var seen: Dictionary = {}
	for row: Variant in rows:
		if not row is Dictionary or row.size() != 6:
			return false

		for field: String in ["participant", "entity", "generation", "life", "control", "health"]:
			if not row.has(field) or not (row[field] is int or row[field] is float):
				return false

			if not is_finite(float(row[field])) or float(row[field]) != int(row[field]):
				return false

		if row.entity <= 0 or row.participant <= 0 or seen.has(int(row.entity)):
			return false

		seen[int(row.entity)] = true

	clear()
	participant_id = int(data.participant)
	durable_revision = int(data.durable)
	for row: Dictionary in rows:
		var entity: int = int(row.entity)
		var participant: int = int(row.participant)
		_create_entity(entity)
		bindings[participant] = {"entity": entity, "generation": int(row.generation),
			"life": int(row.life), "control": int(row.control), "health": int(row.health),
			"admitted": false, "sequence": 0, "pending": 0, "held": 0.0,
			"receipt_ms": 0, "sample": 0.0}

	bind_local(participant_id)
	return true


## Bind exactly one saved local rig; it starts with input disabled.
func bind_local(participant: int) -> void:
	participant_id = participant
	if rig == null:
		var packed: PackedScene = load(RIG_SCENE) as PackedScene
		rig = packed.instantiate()
		rig.name = "LocalRig"
		add_child(rig)

	rig.set_meta("participant", participant)
	rig.set_meta("input_enabled", false)


## Commit durable current health before the handoff is acknowledged.
func apply_journal(participant: int, new_health: int, revision: int) -> bool:
	if not bindings.has(participant) or revision != durable_revision + 1:
		return false

	bindings[participant].health = new_health
	durable_revision = revision
	return true


## Open host command admission only after the matching handoff.
func admit(participant: int) -> void:
	bindings[participant].admitted = true


## Enable local controls only after grant and fresh dependent movement.
func enable_local() -> void:
	if rig != null:
		rig.set_meta("input_enabled", true)


## Return the current binding context for a held frame.
func context(participant: int) -> Dictionary:
	var binding: Dictionary = bindings[participant]
	return {"session": session_id, "revision": 1, "entity": binding.entity,
		"generation": binding.generation, "life": binding.life, "control": binding.control}


## Validate trusted sender binding and exact primitive shape before queueing.
func submit_held(participant: int, envelope: Variant) -> String:
	if not authoritative or not bindings.has(participant) or not bindings[participant].admitted:
		return _reject("NOT_ADMITTED")

	if not _held_shape_valid(envelope):
		return _reject("INVALID")

	if not envelope.context is Dictionary or envelope.context != context(participant):
		return _reject("STALE_CONTEXT")

	var binding: Dictionary = bindings[participant]
	var floor_sequence: int = maxi(int(binding.sequence), int(binding.pending))
	if envelope.sequence <= floor_sequence:
		return _reject("STALE_SEQUENCE")

	if envelope.sequence > int(binding.sequence) + SEQUENCE_WINDOW:
		return _reject("WINDOW")

	binding.pending = envelope.sequence
	binding.held = envelope.move
	binding.receipt_ms = Time.get_ticks_msec()
	return "OK"


## Reject malformed primitives before accessing command fields.
func _held_shape_valid(envelope: Variant) -> bool:
	if not envelope is Dictionary or envelope.size() != 3:
		return false

	if not envelope.has("context") or not envelope.has("sequence") or not envelope.has("move"):
		return false

	if not envelope.sequence is int or not envelope.move is float:
		return false

	return is_finite(envelope.move) and absf(envelope.move) <= 1.0


## Count rejection reasons without mutating simulation.
func _reject(reason: String) -> String:
	rejected[reason] = int(rejected.get(reason, 0)) + 1
	return reason


## Apply movement with a per-entity watermark; never write durable fields.
func apply_movement(envelope: Dictionary) -> bool:
	if envelope.get("session") != session_id or envelope.get("revision") != 1:
		return false

	var rows: Variant = envelope.get("rows")
	if not rows is Array or rows.size() > MAX_ENTITIES:
		return false

	for row: Variant in rows:
		if not row is Dictionary or row.size() != 5:
			return false

		for field: String in ["entity", "tick", "control", "durable", "sample"]:
			if not row.has(field) or not (row[field] is int or row[field] is float):
				return false

			if not is_finite(float(row[field])):
				return false

	for row: Dictionary in rows:
		var entity: int = int(row.entity)
		if not entities.has(entity) or row.durable > durable_revision:
			continue

		if row.tick <= int(motion_ticks.get(entity, -1)):
			continue

		for participant: int in bindings:
			var binding: Dictionary = bindings[participant]
			if binding.entity == entity and binding.control == int(row.control):
				motion_ticks[entity] = int(row.tick)
				binding.sample = float(row.sample)

	return true


## Discard match state and saved scene instances on teardown.
func clear() -> void:
	for actor: S03Entity in entities.values():
		actor.queue_free()

	entities.clear()
	bindings.clear()
	motion_ticks.clear()
	if rig != null:
		rig.queue_free()
		rig = null
