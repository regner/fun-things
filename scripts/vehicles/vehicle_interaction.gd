class_name VehicleInteraction
extends RefCounted
## Owns authoritative seat claims, foot/car transfer, exit clearance, and control revisions.

signal action_resolved(participant_id: int, result: Dictionary)
signal transaction_committed(participant_id: int, result: Dictionary)

const ENTRY_RANGE_M: float = 2.25
const ENTRY_MAX_SPEED_MPS: float = 0.5
const EXIT_MAX_SPEED_MPS: float = 0.5
const MAX_PENDING_ACTIONS_PER_PARTICIPANT: int = 16
const MAX_ACTIONS_PER_PARTICIPANT_TICK: int = 4
const ACTION_RATE_PER_SECOND: float = 16.0
const ACTION_BURST: float = 32.0
const PHYSICS_TICKS_PER_SECOND: float = 60.0
const ACTION_SEQUENCE_WINDOW: int = 64
const RESULT_CACHE_CAPACITY: int = 64
const ACTION_ENTER: StringName = &"ENTER"
const ACTION_EXIT: StringName = &"EXIT"
const STATUS_APPLIED: StringName = &"APPLIED"
const STATUS_REJECTED: StringName = &"REJECTED"
const EXIT_SOCKET_PATHS: Array[NodePath] = [
	NodePath("Sockets/ExitLeft"),
	NodePath("Sockets/ExitRight"),
]
const ENTRY_SOCKET_PATHS: Array[NodePath] = [
	NodePath("Sockets/EntryLeft"),
	NodePath("Sockets/EntryRight"),
]

var _replicator: VehicleReplicator
var _player_lookup: Callable
var _player_state_lookup: Callable
var _clearance_blocked_query: Callable
var _foot_rebind_preflight: Callable
var _foot_rebind_commit: Callable
var _match_revision: int = 0
var _transaction_revision: int = 0
var _pending_actions_by_participant: Dictionary[int, Array] = { }
var _action_rate_by_participant: Dictionary[int, Dictionary] = { }
var _pending_keys: Dictionary[String, bool] = { }
var _result_cache: Dictionary[String, Dictionary] = { }
var _result_order: Array[String] = []
var _last_action_sequence: Dictionary[int, int] = { }
var _highest_admitted_sequence: Dictionary[int, int] = { }


## Injects Match-owned participants and clearance while retaining sole seat-rule ownership.
func configure(  # gdstyle:ignore=quality/max-parameters
	replicator: VehicleReplicator,
	player_lookup: Callable,
	player_state_lookup: Callable,
	clearance_blocked_query: Callable,
	match_revision: int,
	foot_rebind_preflight: Callable = Callable(),
	foot_rebind_commit: Callable = Callable(),
) -> bool:
	if (
		_replicator != null
		or replicator == null
		or not player_lookup.is_valid()
		or not player_state_lookup.is_valid()
		or not clearance_blocked_query.is_valid()
		or match_revision <= 0
	):
		return false

	_replicator = replicator
	_player_lookup = player_lookup
	_player_state_lookup = player_state_lookup
	_clearance_blocked_query = clearance_blocked_query
	_foot_rebind_preflight = foot_rebind_preflight
	_foot_rebind_commit = foot_rebind_commit
	_match_revision = match_revision
	return true


## Queues one reliable action for deterministic host ordering on its accepted tick.
func enqueue_action(request: Dictionary) -> Dictionary:
	var validated: Dictionary = _validate_action_request(request)
	if not validated.get("ok", false):
		return validated
	var key: String = _action_key(int(request.participant_id), int(request.action_sequence))
	if _result_cache.has(key):
		return { "ok": true, "cached_result": _result_cache[key].duplicate(true) }
	if _pending_keys.has(key):
		return { "ok": true, "pending": true }
	var participant_id: int = int(request.participant_id)
	var queue: Array = _pending_actions_by_participant.get(participant_id, [])
	if queue.size() >= MAX_PENDING_ACTIONS_PER_PARTICIPANT:
		return { "ok": false, "failure": &"STATE_LIMIT" }
	if not _consume_action_rate(participant_id, int(request.accepted_tick)):
		return { "ok": false, "failure": &"RATE_LIMIT" }

	queue.append(request.duplicate(true))
	_pending_actions_by_participant[participant_id] = queue
	_highest_admitted_sequence[participant_id] = maxi(
		int(_highest_admitted_sequence.get(participant_id, 0)),
		int(request.action_sequence),
	)
	_pending_keys[key] = true
	return { "ok": true, "pending": true }


## Resolves due actions by tick, participant, then action sequence so one seat claim wins.
func process_actions(through_tick: int) -> Array[Dictionary]:
	var due: Array[Dictionary] = []
	for participant_id: int in _pending_actions_by_participant:
		var retained: Array = []
		var accepted_count: int = 0
		var queue: Array = _pending_actions_by_participant[participant_id]
		queue.sort_custom(_action_precedes)
		for request: Dictionary in queue:
			if (
				int(request.accepted_tick) > through_tick
				or accepted_count >= MAX_ACTIONS_PER_PARTICIPANT_TICK
			):
				retained.append(request)
				continue
			due.append(request)
			accepted_count += 1
		_pending_actions_by_participant[participant_id] = retained

	due.sort_custom(_action_precedes)
	var resolved: Array[Dictionary] = []
	for request: Dictionary in due:
		var result: Dictionary = _resolve_action(request)
		var participant_id: int = int(request.participant_id)
		var key: String = _action_key(participant_id, int(request.action_sequence))
		_pending_keys.erase(key)
		_cache_result(key, result)
		_last_action_sequence[participant_id] = maxi(
			int(_last_action_sequence.get(participant_id, 0)),
			int(request.action_sequence),
		)
		resolved.append(
			{
				"participant_id": participant_id,
				"result": result.duplicate(true),
			}
		)
		action_resolved.emit(participant_id, result.duplicate(true))
	return resolved


## Commits one host-confirmed entry only after all lifecycle, range, and epoch checks pass.
func try_enter(
	participant_id: int,
	player_ref: Dictionary,
	vehicle_ref: Dictionary,
	context: Dictionary,
	action_sequence: int,
) -> Dictionary:
	var failure: StringName = _entry_failure(participant_id, player_ref, vehicle_ref, context)
	if failure != &"":
		return _rejected(action_sequence, failure)

	var actor: ActorMotion = _player_lookup.call(participant_id) as ActorMotion
	var entity_id: int = int(vehicle_ref.id)
	var vehicle: VehicleMotion = _replicator.vehicle_for_entity(entity_id)
	var assigned: Dictionary = _replicator.commit_driver_assignment(participant_id, entity_id)
	if not assigned.get("ok", false):
		return _rejected(action_sequence, &"CONTROL_REVISION_EXHAUSTED")
	var foot_input_epoch: int = _commit_foot_rebind(participant_id)
	if _foot_rebind_commit.is_valid() and foot_input_epoch <= 0:
		return _rejected(action_sequence, &"STALE_COMMAND_CONTEXT")
	assigned.foot_input_epoch = foot_input_epoch

	actor.neutralize()
	actor.collision_layer = 0
	actor.collision_mask = 0
	var presentation: Node3D = actor.get_node_or_null("PresentationAnchor") as Node3D
	if presentation != null:
		presentation.visible = false
	var seat: Marker3D = vehicle.get_node_or_null("Sockets/DriverSeat") as Marker3D
	actor.global_transform = seat.global_transform
	_transaction_revision += 1
	var result: Dictionary = _applied(action_sequence, assigned)
	transaction_committed.emit(participant_id, result.duplicate(true))
	return result


## Commits one stopped exit at the first clear authored candidate, otherwise changes nothing.
func try_exit(  # gdstyle:ignore=quality/max-branches
	participant_id: int,
	player_ref: Dictionary,
	context: Dictionary,
	action_sequence: int,
) -> Dictionary:
	var failure: StringName = _exit_context_failure(participant_id, player_ref, context)
	if failure != &"":
		return _rejected(action_sequence, failure)
	var binding: Dictionary = _replicator.binding_for_participant(participant_id)
	var vehicle: VehicleMotion = _replicator.vehicle_for_entity(int(binding.id))
	if vehicle.velocity.length() >= EXIT_MAX_SPEED_MPS:
		return _rejected(action_sequence, &"EXIT_MOVING")

	var actor: ActorMotion = _player_lookup.call(participant_id) as ActorMotion
	var exit_transform := Transform3D.IDENTITY
	var found_clear: bool = false
	for socket_path: NodePath in EXIT_SOCKET_PATHS:
		var socket: Marker3D = vehicle.get_node_or_null(socket_path) as Marker3D
		if socket == null:
			continue
		if not bool(
			_clearance_blocked_query.call(socket.global_transform, participant_id, actor, vehicle)
		):
			exit_transform = socket.global_transform
			found_clear = true
			break
	if not found_clear:
		return _rejected(action_sequence, &"EXIT_BLOCKED")
	if not _replicator.can_release_driver(participant_id) or not _can_rebind_foot(participant_id):
		return _rejected(action_sequence, &"CONTROL_REVISION_EXHAUSTED")

	var released: Dictionary = _replicator.commit_driver_release(participant_id, false)
	if not released.get("ok", false):
		return _rejected(action_sequence, &"STALE_COMMAND_CONTEXT")
	var foot_input_epoch: int = _commit_foot_rebind(participant_id)
	if _foot_rebind_commit.is_valid() and foot_input_epoch <= 0:
		return _rejected(action_sequence, &"STALE_COMMAND_CONTEXT")
	released.foot_input_epoch = foot_input_epoch
	actor.global_transform = exit_transform
	actor.neutralize()
	actor.collision_layer = 2
	actor.collision_mask = 1
	var presentation: Node3D = actor.get_node_or_null("PresentationAnchor") as Node3D
	if presentation != null:
		presentation.visible = true
	_transaction_revision += 1
	var result: Dictionary = _applied(action_sequence, released)
	transaction_committed.emit(participant_id, result.duplicate(true))
	return result


## Releases a dead or disconnected driver atomically and leaves the surviving car coasting.
func release_for_lifecycle(participant_id: int, reason: StringName) -> Dictionary:
	if reason not in [&"DEATH", &"DISCONNECT"]:
		return { "ok": false, "failure": &"INVALID_REASON" }
	if _replicator.binding_for_participant(participant_id).is_empty():
		return { "ok": true, "changed": false }
	if not _replicator.can_release_driver(participant_id):
		return { "ok": false, "failure": &"CONTROL_REVISION_EXHAUSTED" }

	var released: Dictionary = _replicator.commit_driver_release(participant_id, true)
	if released.get("ok", false):
		_transaction_revision += 1
		transaction_committed.emit(participant_id, released.duplicate(true))
	return released


## Releases a terminal vehicle once without restoring its occupant to an unsafe foot pose.
func release_for_destruction(entity_id: int) -> Dictionary:
	var participant_id: int = _replicator.driver_for_entity(entity_id)
	if participant_id == 0:
		return { "ok": true, "changed": false }
	if not _replicator.can_release_driver(participant_id):
		return { "ok": false, "failure": &"CONTROL_REVISION_EXHAUSTED" }

	var released: Dictionary = _replicator.commit_driver_release(participant_id, false)
	var vehicle: VehicleMotion = _replicator.vehicle_for_entity(entity_id)
	if vehicle != null:
		vehicle.neutralize()
	if released.get("ok", false):
		_transaction_revision += 1
		transaction_committed.emit(participant_id, released.duplicate(true))
	return released


## Advances a seated participant's command epoch for resync without changing occupancy.
func rebind_commands(participant_id: int) -> Dictionary:
	var rebound: Dictionary = _replicator.commit_driver_rebind(participant_id)
	if rebound.get("ok", false):
		_transaction_revision += 1
		transaction_committed.emit(participant_id, rebound.duplicate(true))
	return rebound


## Clears pending old-revision actions before Match restores authored vehicle state.
func reset(match_revision: int) -> bool:
	if match_revision <= _match_revision:
		return false
	_pending_actions_by_participant.clear()
	_action_rate_by_participant.clear()
	_pending_keys.clear()
	_result_cache.clear()
	_result_order.clear()
	_last_action_sequence.clear()
	_highest_admitted_sequence.clear()
	_match_revision = match_revision
	_replicator.reset_authority()
	_transaction_revision += 1
	return true


## Returns the durable transaction revision for hydration and acceptance diagnostics.
func transaction_revision() -> int:
	return _transaction_revision


## Checks the Match-owned foot epoch before any seat-side state mutates.
func _can_rebind_foot(participant_id: int) -> bool:
	return (
		not _foot_rebind_preflight.is_valid()
		or bool(_foot_rebind_preflight.call(participant_id))
	)


## Advances and clears Match-owned foot intent at the committed seat-transfer fence.
func _commit_foot_rebind(participant_id: int) -> int:
	if not _foot_rebind_commit.is_valid():
		return 0
	return int(_foot_rebind_commit.call(participant_id))


## Consumes one participant-scoped token using the host-accepted simulation tick.
func _consume_action_rate(participant_id: int, accepted_tick: int) -> bool:
	var state: Dictionary = _action_rate_by_participant.get(
		participant_id,
		{
			"tokens": ACTION_BURST,
			"updated_tick": accepted_tick,
		},
	)
	var elapsed_ticks: int = maxi(0, accepted_tick - int(state.updated_tick))
	state.tokens = minf(
		ACTION_BURST,
		float(state.tokens)
		+ float(elapsed_ticks) * ACTION_RATE_PER_SECOND / PHYSICS_TICKS_PER_SECOND,
	)
	state.updated_tick = maxi(int(state.updated_tick), accepted_tick)
	if float(state.tokens) < 1.0:
		_action_rate_by_participant[participant_id] = state
		return false
	state.tokens = float(state.tokens) - 1.0
	_action_rate_by_participant[participant_id] = state
	return true


## Returns one request's deterministic cache key without exposing mutable cache state.
func _action_key(participant_id: int, action_sequence: int) -> String:
	return "%d:%d" % [participant_id, action_sequence]


## Orders same-tick claims independently of callback arrival order.
func _action_precedes(left: Dictionary, right: Dictionary) -> bool:
	var left_key: Array[int] = [
		int(left.accepted_tick),
		int(left.participant_id),
		int(left.action_sequence),
	]
	var right_key: Array[int] = [
		int(right.accepted_tick),
		int(right.participant_id),
		int(right.action_sequence),
	]
	return left_key < right_key


## Resolves one already-bounded action against current authoritative state.
func _resolve_action(request: Dictionary) -> Dictionary:
	var participant_id: int = int(request.participant_id)
	var player_ref: Dictionary = request.player_ref
	var context: Dictionary = { "match_revision": int(request.match_revision) }
	if request.kind == ACTION_ENTER:
		return try_enter(
			participant_id,
			player_ref,
			request.vehicle_ref,
			context,
			int(request.action_sequence),
		)
	return try_exit(
		participant_id,
		player_ref,
		context,
		int(request.action_sequence),
	)


## Rejects malformed, stale, excessive, or replayed action requests before queue mutation.
func _validate_action_request(  # gdstyle:ignore=quality/max-returns,quality/max-branches
	request: Dictionary,
) -> Dictionary:
	if (
		request.size() not in [6, 7]
		or not request.has_all(
			[
				"participant_id",
				"player_ref",
				"match_revision",
				"accepted_tick",
				"action_sequence",
				"kind",
			]
		)
	):
		return { "ok": false, "failure": &"MALFORMED_ACTION" }
	if (
		request.participant_id is not int
		or int(request.participant_id) <= 0
		or request.player_ref is not Dictionary
		or not ReplicationIdentity.is_valid_entity_ref(request.player_ref)
		or request.match_revision is not int
		or int(request.match_revision) != _match_revision
		or request.accepted_tick is not int
		or int(request.accepted_tick) < 0
		or request.action_sequence is not int
		or int(request.action_sequence) <= 0
		or (request.kind is not String and request.kind is not StringName)
	):
		return { "ok": false, "failure": &"MALFORMED_ACTION" }
	var kind := StringName(request.kind)
	if kind not in [ACTION_ENTER, ACTION_EXIT]:
		return { "ok": false, "failure": &"UNKNOWN_ACTION" }
	if kind == ACTION_ENTER:
		if request.size() != 7 or request.get("vehicle_ref") is not Dictionary:
			return { "ok": false, "failure": &"MALFORMED_ACTION" }
		if not ReplicationIdentity.is_valid_entity_ref(request.vehicle_ref):
			return { "ok": false, "failure": &"MALFORMED_ACTION" }
	if kind == ACTION_EXIT and (request.size() != 6 or request.has("vehicle_ref")):
		return { "ok": false, "failure": &"MALFORMED_ACTION" }
	return _validate_action_sequence(
		int(request.participant_id), int(request.action_sequence)
	)


## Accepts exact idempotent replay while fencing every newly admitted sequence monotonically.
func _validate_action_sequence(participant_id: int, action_sequence: int) -> Dictionary:
	var key: String = _action_key(participant_id, action_sequence)
	if _result_cache.has(key) or _pending_keys.has(key):
		return { "ok": true }
	var highest_admitted: int = int(_highest_admitted_sequence.get(participant_id, 0))
	if action_sequence <= highest_admitted:
		return { "ok": false, "failure": &"STALE_SEQUENCE" }
	if action_sequence > highest_admitted + ACTION_SEQUENCE_WINDOW:
		return { "ok": false, "failure": &"SEQUENCE_WINDOW" }
	return { "ok": true }


## Checks every entry dependency without changing seat, body, or command state.
func _entry_failure(  # gdstyle:ignore=quality/max-returns,quality/max-branches
	participant_id: int,
	player_ref: Dictionary,
	vehicle_ref: Dictionary,
	context: Dictionary,
) -> StringName:
	if not _valid_context(participant_id, player_ref, context):
		return &"STALE_ACTION_CONTEXT"
	if not _replicator.binding_for_participant(participant_id).is_empty():
		return &"ALREADY_SEATED"
	var entity_id: int = int(vehicle_ref.get("id", 0))
	var descriptor: Dictionary = _replicator.descriptor_for_entity(entity_id)
	if descriptor.is_empty() or int(descriptor.generation) != int(vehicle_ref.get("generation", 0)):
		return &"STALE_VEHICLE"
	if int(descriptor.driver_participant_id) > 0:
		return &"SEAT_OCCUPIED"
	if not _replicator.can_assign_driver(participant_id, entity_id) or not _can_rebind_foot(
		participant_id
	):
		return &"CONTROL_REVISION_EXHAUSTED"
	var actor: ActorMotion = _player_lookup.call(participant_id) as ActorMotion
	var vehicle: VehicleMotion = _replicator.vehicle_for_entity(entity_id)
	if actor == null or vehicle == null or vehicle.velocity.length() >= ENTRY_MAX_SPEED_MPS:
		return &"ENTRY_MOVING"
	var nearest_distance: float = INF
	var nearest_transform := Transform3D.IDENTITY
	for socket_path: NodePath in ENTRY_SOCKET_PATHS:
		var socket: Marker3D = vehicle.get_node_or_null(socket_path) as Marker3D
		if socket == null:
			continue
		var distance: float = actor.global_position.distance_to(socket.global_position)
		if distance < nearest_distance:
			nearest_distance = distance
			nearest_transform = socket.global_transform
	if not is_finite(nearest_distance):
		return &"SOCKET_MISSING"
	if nearest_distance > ENTRY_RANGE_M:
		return &"ENTRY_OUT_OF_RANGE"
	if bool(_clearance_blocked_query.call(nearest_transform, participant_id, actor, vehicle)):
		return &"ENTRY_BLOCKED"
	return &""


## Checks the live player and exact current seat before an exit candidate is queried.
func _exit_context_failure(
	participant_id: int,
	player_ref: Dictionary,
	context: Dictionary,
) -> StringName:
	if not _valid_context(participant_id, player_ref, context):
		return &"STALE_ACTION_CONTEXT"
	if _replicator.binding_for_participant(participant_id).is_empty():
		return &"NOT_SEATED"
	return &""


## Applies MatchRevision and PlayerLifecycle EntityRef/alive fences to every transaction.
func _valid_context(
	participant_id: int,
	player_ref: Dictionary,
	context: Dictionary,
) -> bool:
	if int(context.get("match_revision", 0)) != _match_revision:
		return false
	var state: Variant = _player_state_lookup.call(participant_id)
	if state is not Dictionary:
		return false
	var player_state: Dictionary = state
	var current_ref: Dictionary = player_state.get("entity_ref", { })
	return (
		bool(player_state.get("alive", false))
		and int(current_ref.get("id", 0)) == int(player_ref.get("id", 0))
		and int(current_ref.get("generation", 0)) == int(player_ref.get("generation", 0))
	)


## Builds an immutable applied result tied to the committed descriptor revision.
func _applied(action_sequence: int, mutation: Dictionary) -> Dictionary:
	return {
		"action_sequence": action_sequence,
		"status": STATUS_APPLIED,
		"durable_revision": _transaction_revision,
		"entity_ref": mutation.get("entity_ref", { }).duplicate(),
		"control_revision": int(mutation.get("input_epoch", 0)),
	}


## Builds one consumed rejection result without exposing implementation details.
func _rejected(action_sequence: int, failure: StringName) -> Dictionary:
	return {
		"action_sequence": action_sequence,
		"status": STATUS_REJECTED,
		"failure": failure,
	}


## Retains only the bounded recent action-result window for idempotent duplicates.
func _cache_result(key: String, result: Dictionary) -> void:
	_result_cache[key] = result.duplicate(true)
	_result_order.append(key)
	while _result_order.size() > RESULT_CACHE_CAPACITY:
		_result_cache.erase(_result_order.pop_front())
