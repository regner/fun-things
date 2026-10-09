class_name SessionService
extends Node
## Owns process-lifetime session operations, compatibility admission, and cleanup.

signal changed(view: Dictionary)
signal completed(operation_id: int, result: Dictionary)
signal standalone_started(operation_id: int, district_id: StringName)

const CLOSE_TIMEOUT_SECONDS: float = 5.0
const CONNECTION_TIMEOUT_SECONDS: float = 15.0
const HANDSHAKE_TIMEOUT_SECONDS: float = 5.0
const MAX_ID_BYTES: int = 128
const PROVIDER_STANDALONE: StringName = &"standalone"
const OPERATION_NONE: StringName = &"NONE"
const OPERATION_HOST: StringName = &"HOST"
const OPERATION_JOIN: StringName = &"JOIN"
const OPERATION_STANDALONE: StringName = &"STANDALONE"
const OPERATION_LEAVE: StringName = &"LEAVE"
const PHASE_IDLE: StringName = &"IDLE"
const PHASE_STARTING: StringName = &"STARTING"
const PHASE_CONNECTING: StringName = &"CONNECTING"
const PHASE_NEGOTIATING: StringName = &"NEGOTIATING"
const PHASE_LOADING: StringName = &"LOADING"
const PHASE_SYNCHRONIZING: StringName = &"SYNCHRONIZING"
const PHASE_ACTIVE: StringName = &"ACTIVE"
const PHASE_CLOSING: StringName = &"CLOSING"

var close_timeout_seconds: float = CLOSE_TIMEOUT_SECONDS
var connection_timeout_seconds: float = CONNECTION_TIMEOUT_SECONDS
var handshake_timeout_seconds: float = HANDSHAKE_TIMEOUT_SECONDS
var _operation: Dictionary = {
	"phase": PHASE_IDLE,
	"id": 0,
	"kind": OPERATION_NONE,
	"provider_id": &"",
	"deadline_seconds": 0.0,
}
var _next_operation_id: int = 1
var _identity: Dictionary = { "session_id": "", "local_participant_id": 0 }
var _failure: Dictionary = {}
var _transport: SessionTransport
var _close_result: Dictionary = {}
var _last_request: Dictionary = {}
var _completed_operations: Dictionary[int, bool] = {}
var _provider_reusable: bool = true
var _ignored_callback_count: int = 0
var _compatibility: Dictionary = {
	"protocol_version": 1,
	"content_id": "development",
	"district_id": &"brackett_island",
	"topology_revision": 0,
	"definition_set_id": "development",
}
var _host_state: Dictionary = {
	"capacity": 0,
	"next_participant_id": 2,
	"participant_by_peer": {},
	"token_by_peer": {},
	"pending_deadlines": {},
	"roster_by_participant": {},
}


## Enforces connection, handshake, and shared close deadlines using monotonic time.
func _process(_delta: float) -> void:
	var now_seconds: float = Time.get_ticks_msec() / 1000.0
	if _operation.phase == PHASE_CLOSING and now_seconds >= _operation.deadline_seconds:
		_provider_reusable = false
		_close_result = {
			"reuse_status": SessionTransport.REUSE_UNAVAILABLE,
			"failure": _make_failure(&"CLEANUP_TIMEOUT", false),
		}
		_finish_close()
	elif _operation.phase in [PHASE_CONNECTING, PHASE_NEGOTIATING]:
		if now_seconds >= _operation.deadline_seconds:
			var code: StringName = (
				&"UNREACHABLE_HOST" if _operation.phase == PHASE_CONNECTING else &"INCOMPATIBLE"
			)
			_begin_close(_make_failure(code, true))
	elif _operation.kind == OPERATION_HOST and _operation.phase == PHASE_ACTIVE:
		_expire_pending_peers(now_seconds)


## Registers the one fixed provider binding while the service is idle.
func register_transport(transport: SessionTransport) -> Dictionary:
	if _operation.phase != PHASE_IDLE:
		return _rejection(&"BUSY", false)
	if transport == null or transport.provider_id() == &"":
		return _rejection(&"INVALID_REQUEST", false)
	if _transport == transport:
		_provider_reusable = _provider_reusable and transport.is_available()
		return _acceptance(0)
	if _next_operation_id > 1:
		return _rejection(&"SERVICE_UNAVAILABLE", false)

	if _transport != null:
		_disconnect_transport(_transport)

	_transport = transport
	_transport.peer_ready.connect(_on_peer_ready)
	_transport.connected.connect(_on_transport_connected)
	_transport.disconnected.connect(_on_transport_disconnected)
	_transport.failed.connect(_on_transport_failed)
	_transport.closed.connect(_on_transport_closed)
	_provider_reusable = transport.is_available()
	return _acceptance(0)


## Sets the exact handshake identity before accepting a session operation.
func configure_compatibility(compatibility: Dictionary) -> Dictionary:
	if _operation.phase != PHASE_IDLE or _next_operation_id > 1:
		return _rejection(&"BUSY", false)
	if not _valid_compatibility(compatibility):
		return _rejection(&"INVALID_REQUEST", false)

	_compatibility = compatibility.duplicate(true)
	return _acceptance(0)


## Reports an exact compatibility failure without mutating session state.
func validate_compatibility(candidate: Dictionary) -> Dictionary:
	if not _valid_compatibility(candidate):
		return _rejection(&"INVALID_REQUEST", false)
	if candidate.protocol_version != _compatibility.protocol_version:
		return _rejection(&"INCOMPATIBLE", false)
	if (
		candidate.content_id != _compatibility.content_id
		or candidate.district_id != _compatibility.district_id
		or candidate.topology_revision != _compatibility.topology_revision
		or candidate.definition_set_id != _compatibility.definition_set_id
	):
		return _rejection(&"CONTENT_INVALID", false)

	return _acceptance(0)


## Accepts a host request for the registered provider or rejects it synchronously.
func host(request: Dictionary) -> Dictionary:
	if _operation.phase != PHASE_IDLE:
		return _rejection(&"BUSY", true)
	if not _valid_host_request(request):
		return _rejection(&"INVALID_REQUEST", false)
	if not _can_use_provider(request.provider_id):
		return _rejection(&"SERVICE_UNAVAILABLE", true)

	_last_request = { "kind": OPERATION_HOST, "payload": request.duplicate(true) }
	_begin_operation(OPERATION_HOST, PHASE_STARTING, request.provider_id)
	_host_state.capacity = request.capacity
	var provider_options: Dictionary = request.get("provider_options", {}).duplicate(true)
	provider_options["capacity"] = _host_state.capacity
	var adapter_result: Dictionary = _transport.open_host(_operation.id, provider_options)
	if not adapter_result.get("ok", false):
		_begin_close(_adapter_failure(adapter_result))

	return _acceptance(_operation.id)


## Accepts an opaque provider-owned join target or rejects it synchronously.
func join(target: Dictionary) -> Dictionary:
	if _operation.phase != PHASE_IDLE:
		return _rejection(&"BUSY", true)
	if not _valid_join_target(target):
		return _rejection(&"INVALID_REQUEST", false)
	if not _can_use_provider(target.provider_id):
		return _rejection(&"SERVICE_UNAVAILABLE", true)

	_last_request = { "kind": OPERATION_JOIN, "payload": target.duplicate(true) }
	_begin_operation(OPERATION_JOIN, PHASE_CONNECTING, target.provider_id)
	_operation.deadline_seconds = _now_seconds() + connection_timeout_seconds
	var adapter_result: Dictionary = _transport.open_client(_operation.id, target)
	if not adapter_result.get("ok", false):
		_begin_close(_adapter_failure(adapter_result))

	return _acceptance(_operation.id)


## Starts the no-network authority path without creating a fake remote peer.
func start_standalone(district_id: StringName) -> Dictionary:
	if _operation.phase != PHASE_IDLE:
		return _rejection(&"BUSY", true)
	if district_id == &"" or district_id.to_utf8_buffer().size() > MAX_ID_BYTES:
		return _rejection(&"INVALID_REQUEST", false)

	_last_request = { "kind": OPERATION_STANDALONE, "payload": district_id }
	_begin_operation(OPERATION_STANDALONE, PHASE_STARTING, PROVIDER_STANDALONE)
	_host_state.capacity = 1
	_activate_standalone.call_deferred(_operation.id, district_id)
	return _acceptance(_operation.id)


## Cancels only the accepted in-flight operation and shares its cleanup completion.
func cancel(requested_operation_id: int) -> Dictionary:
	if requested_operation_id != _operation.id:
		return _rejection(&"STALE_OPERATION", false)
	if _operation.phase == PHASE_CLOSING:
		return _acceptance(_operation.id)
	if _operation.phase in [PHASE_IDLE, PHASE_ACTIVE]:
		return _rejection(&"NOT_CANCELABLE", false)

	_begin_close(_make_failure(&"CANCELED", true))
	return _acceptance(_operation.id)


## Leaves an active session or returns the already-running close operation.
func leave() -> Dictionary:
	if _operation.phase == PHASE_CLOSING:
		return _acceptance(_operation.id)
	if _operation.phase != PHASE_ACTIVE:
		return _rejection(&"NOT_ACTIVE", false)

	_begin_operation(OPERATION_LEAVE, PHASE_CLOSING, _operation.provider_id)
	_operation.deadline_seconds = _now_seconds() + close_timeout_seconds
	_close_result = { "reuse_status": SessionTransport.REUSE_SAFE }
	_detach_peer()
	if _operation.provider_id == PROVIDER_STANDALONE:
		_finish_close.call_deferred()
	else:
		_request_transport_close()

	_emit_changed()
	return _acceptance(_operation.id)


## Repeats the last accepted start request only after cleanup has restored idle.
func retry() -> Dictionary:
	if _operation.phase != PHASE_IDLE:
		return _rejection(&"BUSY", true)
	if _last_request.is_empty():
		return _rejection(&"NO_RETRY", false)

	var kind: StringName = _last_request.kind
	var payload: Variant = _last_request.payload
	if kind == OPERATION_HOST:
		return host((payload as Dictionary).duplicate(true))
	if kind == OPERATION_JOIN:
		return join((payload as Dictionary).duplicate(true))
	if kind == OPERATION_STANDALONE:
		return start_standalone(payload as StringName)

	return _rejection(&"NO_RETRY", false)


## Returns an immutable snapshot suitable for menus and status presentation.
func view() -> Dictionary:
	return {
		"phase": _operation.phase,
		"operation_id": _operation.id if _operation.phase != PHASE_IDLE else 0,
		"operation_kind": _operation.kind,
		"provider_id": _operation.provider_id,
		"session_id": _identity.session_id,
		"local_participant_id": _identity.local_participant_id,
		"capacity": _host_state.capacity if _operation.phase != PHASE_IDLE else 0,
		"roster": _roster_view(),
		"failure": _failure.duplicate(true),
		"provider_reusable": _provider_reusable,
	}


## Exposes ignored callback count for lifecycle diagnostics and focused tests.
func ignored_callback_count() -> int:
	return _ignored_callback_count


## Completes a still-current standalone start after callers can observe STARTING.
func _activate_standalone(source_operation_id: int, district_id: StringName) -> void:
	if source_operation_id != _operation.id or _operation.phase != PHASE_STARTING:
		_ignored_callback_count += 1
		return

	_identity.session_id = Crypto.new().generate_random_bytes(16).hex_encode()
	_identity.local_participant_id = 1
	_host_state.roster_by_participant[1] = _roster_row(1, "Host")
	_operation.phase = PHASE_ACTIVE
	standalone_started.emit(source_operation_id, district_id)
	_complete(source_operation_id, { "ok": true, "view": view() })
	_emit_changed()


## Begins one accepted operation with a process-unique positive identifier.
func _begin_operation(kind: StringName, phase: StringName, provider_id: StringName) -> void:
	_operation.id = _next_operation_id
	_next_operation_id += 1
	_operation.kind = kind
	_operation.phase = phase
	_operation.provider_id = provider_id
	_failure = {}
	_close_result = {}
	_operation.deadline_seconds = 0.0
	_emit_changed()


## Invalidates producers and enters the one bounded cleanup path.
func _begin_close(failure: Dictionary) -> void:
	if _operation.phase == PHASE_CLOSING:
		return

	_failure = _normalize_failure(failure)
	_operation.phase = PHASE_CLOSING
	_operation.deadline_seconds = _now_seconds() + close_timeout_seconds
	_close_result = { "reuse_status": SessionTransport.REUSE_SAFE }
	_detach_peer()
	if _operation.provider_id == PROVIDER_STANDALONE:
		_finish_close.call_deferred()
	else:
		_request_transport_close()

	_emit_changed()


## Requests provider cleanup after session state and peer access are invalidated.
func _request_transport_close() -> void:
	if _transport == null:
		_finish_close.call_deferred()
		return

	var close_acceptance: Dictionary = _transport.close(_operation.id)
	if not close_acceptance.get("ok", false):
		_provider_reusable = false
		_close_result = {
			"reuse_status": SessionTransport.REUSE_UNAVAILABLE,
			"failure": _adapter_failure(close_acceptance),
		}
		_finish_close.call_deferred()


## Restores idle once and emits the accepted operation's terminal result.
func _finish_close() -> void:
	if _operation.phase != PHASE_CLOSING:
		return

	var finished_operation: int = _operation.id
	var terminal_failure: Dictionary = _failure.duplicate(true)
	var result: Dictionary = {
		"ok": terminal_failure.is_empty(),
		"failure": terminal_failure,
		"close": _close_result.duplicate(true),
	}
	_clear_session_state()
	_operation.phase = PHASE_IDLE
	_operation.kind = OPERATION_NONE
	_operation.provider_id = &""
	_operation.id = 0
	_operation.deadline_seconds = 0.0
	if terminal_failure.get("code", &"") == &"CANCELED":
		_failure = {}

	_complete(finished_operation, result)
	_emit_changed()


## Publishes exactly one terminal completion for an accepted operation.
func _complete(source_operation_id: int, result: Dictionary) -> void:
	if source_operation_id <= 0 or _completed_operations.has(source_operation_id):
		return

	_completed_operations[source_operation_id] = true
	completed.emit(source_operation_id, result.duplicate(true))


## Attaches only a current peer and waits for connectivity before client admission.
func _on_peer_ready(source_operation_id: int, peer: MultiplayerPeer) -> void:
	if (
		source_operation_id != _operation.id
		or _operation.phase not in [PHASE_STARTING, PHASE_CONNECTING]
	):
		_ignored_callback_count += 1
		if _transport != null:
			_transport.dispose_obsolete(source_operation_id, peer)
		else:
			peer.close()

		return

	multiplayer.multiplayer_peer = peer
	if _operation.kind == OPERATION_HOST:
		_identity.session_id = Crypto.new().generate_random_bytes(16).hex_encode()
		_identity.local_participant_id = 1
		_host_state.participant_by_peer[1] = 1
		_host_state.roster_by_participant[1] = _roster_row(1, "Host")
		_operation.phase = PHASE_ACTIVE
		_complete(source_operation_id, { "ok": true, "view": view() })
		_emit_changed()


## Starts the fixed handshake only for a current connected client operation.
func _on_transport_connected(
	source_operation_id: int,
	connection_token: int,
	native_peer_id: int,
) -> void:
	if _operation.kind == OPERATION_HOST and _operation.phase == PHASE_ACTIVE:
		_host_state.token_by_peer[native_peer_id] = connection_token
		_host_state.pending_deadlines[native_peer_id] = _now_seconds() + handshake_timeout_seconds
		return
	if source_operation_id != _operation.id or _operation.phase != PHASE_CONNECTING:
		_ignored_callback_count += 1
		return

	_host_state.token_by_peer[native_peer_id] = connection_token
	_operation.phase = PHASE_NEGOTIATING
	_operation.deadline_seconds = _now_seconds() + handshake_timeout_seconds
	_emit_changed()
	_request_admission.rpc_id(
		1,
		_operation.id,
		[
			_compatibility.protocol_version,
			String(_compatibility.content_id),
			String(_compatibility.district_id),
			_compatibility.topology_revision,
			String(_compatibility.definition_set_id),
		],
	)


## Releases a host reservation or closes a client after native disconnection.
func _on_transport_disconnected(
	source_operation_id: int,
	connection_token: int,
	native_peer_id: int,
	failure: Dictionary,
) -> void:
	if _operation.kind == OPERATION_HOST and _operation.phase == PHASE_ACTIVE:
		if _host_state.token_by_peer.get(native_peer_id, -1) != connection_token:
			_ignored_callback_count += 1
			return

		_host_state.token_by_peer.erase(native_peer_id)
		_host_state.pending_deadlines.erase(native_peer_id)
		var participant_id: int = _host_state.participant_by_peer.get(native_peer_id, 0)
		_host_state.participant_by_peer.erase(native_peer_id)
		_host_state.roster_by_participant.erase(participant_id)
		_emit_changed()
		return
	if source_operation_id != _operation.id or _operation.phase in [PHASE_IDLE, PHASE_CLOSING]:
		_ignored_callback_count += 1
		return

	_begin_close(failure)


## Converts a current provider failure into bounded cleanup without double completion.
func _on_transport_failed(source_operation_id: int, failure: Dictionary) -> void:
	if source_operation_id != _operation.id or _operation.phase in [PHASE_IDLE, PHASE_CLOSING]:
		_ignored_callback_count += 1
		return

	_begin_close(failure)


## Applies only the current close result; late results remain cleanup-only.
func _on_transport_closed(source_operation_id: int, result: Dictionary) -> void:
	if source_operation_id != _operation.id or _operation.phase != PHASE_CLOSING:
		_ignored_callback_count += 1
		return

	_close_result = result.duplicate(true)
	_provider_reusable = result.get("reuse_status", SessionTransport.REUSE_UNAVAILABLE) == (
		SessionTransport.REUSE_SAFE
	)
	_finish_close()


## Validates one sender-derived handshake and delegates its explicit verdict.
@rpc("any_peer", "call_remote", "reliable", 0)
func _request_admission(client_operation_id: int, handshake: Array) -> void:
	var sender_peer_id: int = multiplayer.get_remote_sender_id()
	if _operation.kind != OPERATION_HOST or _operation.phase != PHASE_ACTIVE:
		return
	if sender_peer_id <= 1 or handshake.size() != 5:
		return

	var candidate: Dictionary = {
		"protocol_version": handshake[0],
		"content_id": handshake[1],
		"district_id": StringName(handshake[2]) if handshake[2] is String else &"",
		"topology_revision": handshake[3],
		"definition_set_id": handshake[4],
	}
	_evaluate_admission(sender_peer_id, client_operation_id, candidate)


## Allocates or rejects one participant after compatibility and duplicate checks.
func _evaluate_admission(
	sender_peer_id: int,
	client_operation_id: int,
	candidate: Dictionary,
) -> void:
	if _host_state.participant_by_peer.has(sender_peer_id):
		var existing_id: int = _host_state.participant_by_peer[sender_peer_id]
		_send_admission(sender_peer_id, client_operation_id, &"", existing_id)
		return
	if not _host_state.pending_deadlines.has(sender_peer_id):
		return

	_host_state.pending_deadlines.erase(sender_peer_id)
	var validation: Dictionary = validate_compatibility(candidate)
	var failure_code: StringName = validation.get("failure", {}).get("code", &"")
	if failure_code == &"" and _host_state.roster_by_participant.size() >= _host_state.capacity:
		failure_code = &"SESSION_FULL"
	if failure_code != &"":
		_send_admission(sender_peer_id, client_operation_id, failure_code, 0)
		_disconnect_rejected_peer.call_deferred(sender_peer_id)
		return

	var participant_id: int = _host_state.next_participant_id
	_host_state.next_participant_id += 1
	_host_state.participant_by_peer[sender_peer_id] = participant_id
	_host_state.roster_by_participant[participant_id] = _roster_row(
		participant_id, "Player %d" % participant_id
	)
	_send_admission(sender_peer_id, client_operation_id, &"", participant_id)
	_emit_changed()


## Sends one fixed-shape admission verdict on the reliable session channel.
func _send_admission(
	peer_id: int,
	client_operation_id: int,
	failure_code: StringName,
	participant_id: int,
) -> void:
	_receive_admission.rpc_id(
		peer_id,
		client_operation_id,
		[
			failure_code == &"",
			String(failure_code),
			participant_id,
			_identity.session_id if failure_code == &"" else "",
			_host_state.capacity,
		],
	)


## Applies a host verdict only to the current negotiating client operation.
@rpc("authority", "call_remote", "reliable", 0)
func _receive_admission(client_operation_id: int, verdict: Array) -> void:
	if (
		_operation.kind != OPERATION_JOIN
		or _operation.phase != PHASE_NEGOTIATING
		or client_operation_id != _operation.id
		or verdict.size() != 5
	):
		_ignored_callback_count += 1
		return

	var admitted: Variant = verdict[0]
	var failure_code: Variant = verdict[1]
	var participant_id: Variant = verdict[2]
	var session_id: Variant = verdict[3]
	var capacity: Variant = verdict[4]
	if admitted is not bool or failure_code is not String:
		_begin_close(_make_failure(&"INCOMPATIBLE", false))
		return
	if not admitted:
		_apply_admission_failure(failure_code)
		return
	if not _valid_admission_identity(participant_id, session_id, capacity):
		_begin_close(_make_failure(&"INCOMPATIBLE", false))
		return

	_identity.local_participant_id = participant_id
	_identity.session_id = session_id
	_host_state.capacity = capacity
	_host_state.roster_by_participant[participant_id] = _roster_row(
		participant_id, "Local player"
	)
	_operation.phase = PHASE_ACTIVE
	_operation.deadline_seconds = 0.0
	_complete(client_operation_id, { "ok": true, "view": view() })
	_emit_changed()


## Normalizes the finite host rejection codes before starting client cleanup.
func _apply_admission_failure(failure_code: String) -> void:
	var code: StringName = StringName(failure_code)
	if code not in [&"INCOMPATIBLE", &"CONTENT_INVALID", &"SESSION_FULL"]:
		code = &"INCOMPATIBLE"

	_begin_close(_make_failure(code, code != &"CONTENT_INVALID"))


## Validates the positive participant, session, and capacity fields of a grant.
func _valid_admission_identity(
	participant_id: Variant,
	session_id: Variant,
	capacity: Variant,
) -> bool:
	return (
		participant_id is int
		and participant_id > 0
		and session_id is String
		and session_id.length() == 32
		and capacity is int
		and capacity >= 1
		and capacity <= 4
	)


## Disconnects native peers that never submit a bounded handshake.
func _expire_pending_peers(now_seconds: float) -> void:
	for peer_id: int in _host_state.pending_deadlines.keys():
		if now_seconds < _host_state.pending_deadlines[peer_id]:
			continue

		_host_state.pending_deadlines.erase(peer_id)
		if _host_state.token_by_peer.has(peer_id):
			multiplayer.multiplayer_peer.disconnect_peer(peer_id)


## Delays rejection disconnect long enough for its reliable verdict to flush.
func _disconnect_rejected_peer(peer_id: int) -> void:
	await get_tree().create_timer(0.1).timeout
	if (
		_operation.kind == OPERATION_HOST
		and _operation.phase == PHASE_ACTIVE
		and _host_state.token_by_peer.has(peer_id)
	):
		multiplayer.multiplayer_peer.disconnect_peer(peer_id)


## Removes a registered provider's signal links before replacing it while idle.
func _disconnect_transport(transport: SessionTransport) -> void:
	if transport.peer_ready.is_connected(_on_peer_ready):
		transport.peer_ready.disconnect(_on_peer_ready)
	if transport.connected.is_connected(_on_transport_connected):
		transport.connected.disconnect(_on_transport_connected)
	if transport.disconnected.is_connected(_on_transport_disconnected):
		transport.disconnected.disconnect(_on_transport_disconnected)
	if transport.failed.is_connected(_on_transport_failed):
		transport.failed.disconnect(_on_transport_failed)
	if transport.closed.is_connected(_on_transport_closed):
		transport.closed.disconnect(_on_transport_closed)


## Replaces any native peer before provider cleanup can publish completion.
func _detach_peer() -> void:
	multiplayer.multiplayer_peer = OfflineMultiplayerPeer.new()


## Clears identities, roster, and connection mappings at the teardown boundary.
func _clear_session_state() -> void:
	_identity.session_id = ""
	_identity.local_participant_id = 0
	_host_state.capacity = 0
	_host_state.next_participant_id = 2
	_host_state.participant_by_peer.clear()
	_host_state.token_by_peer.clear()
	_host_state.pending_deadlines.clear()
	_host_state.roster_by_participant.clear()


## Checks provider registration, availability, and timeout reuse fences.
func _can_use_provider(provider_id: StringName) -> bool:
	return (
		_transport != null
		and _transport.provider_id() == provider_id
		and _transport.is_available()
		and _provider_reusable
	)


## Validates the host request fields owned by SessionService.
func _valid_host_request(request: Dictionary) -> bool:
	var provider_id: Variant = request.get("provider_id")
	var district_id: Variant = request.get("district_id")
	var capacity: Variant = request.get("capacity")
	return (
		provider_id is StringName
		and provider_id != &""
		and district_id is StringName
		and district_id != &""
		and (district_id as StringName).to_utf8_buffer().size() <= MAX_ID_BYTES
		and capacity is int
		and capacity >= 1
		and capacity <= 4
		and request.get("provider_options", {}) is Dictionary
	)


## Validates only common target identity before its provider interprets the opaque payload.
func _valid_join_target(target: Dictionary) -> bool:
	return (
		target.get("provider_id") is StringName
		and target.get("provider_id", &"") != &""
		and target.get("adapter_generation") is int
		and target.get("adapter_generation", -1) >= 0
		and target.get("kind") is StringName
		and target.get("kind", &"") == &"TRANSPORT_READY"
	)


## Validates the bounded primitive handshake shape before comparing identity.
func _valid_compatibility(candidate: Dictionary) -> bool:
	return (
		candidate.get("protocol_version") is int
		and candidate.get("protocol_version", 0) > 0
		and _valid_bounded_string(candidate.get("content_id"))
		and candidate.get("district_id") is StringName
		and candidate.get("district_id", &"") != &""
		and candidate.get("district_id", &"").to_utf8_buffer().size() <= MAX_ID_BYTES
		and candidate.get("topology_revision") is int
		and candidate.get("topology_revision", -1) >= 0
		and _valid_bounded_string(candidate.get("definition_set_id"))
	)


## Accepts one nonempty compatibility identifier within its UTF-8 byte bound.
func _valid_bounded_string(value: Variant) -> bool:
	return (
		value is String
		and not value.is_empty()
		and value.to_utf8_buffer().size() <= MAX_ID_BYTES
	)


## Normalizes an adapter's immediate failure into the session failure shape.
func _adapter_failure(adapter_result: Dictionary) -> Dictionary:
	var failure: Variant = adapter_result.get("failure", {})
	if failure is Dictionary and not failure.is_empty():
		return _normalize_failure(failure)

	return _make_failure(&"PROVIDER_FAILED", true)


## Adds current operation context to a provider-safe failure record.
func _normalize_failure(failure: Dictionary) -> Dictionary:
	var code: StringName = StringName(failure.get("code", &"PROVIDER_FAILED"))
	return {
		"code": code,
		"phase": _operation.phase,
		"operation_id": _operation.id,
		"retryable": failure.get("retryable", true),
		"message_key": StringName("session." + String(code).to_lower()),
	}


## Constructs one UI-safe normalized failure record.
func _make_failure(code: StringName, retryable: bool) -> Dictionary:
	return _normalize_failure({ "code": code, "retryable": retryable })


## Returns a synchronous accepted-operation result.
func _acceptance(accepted_operation_id: int) -> Dictionary:
	return { "ok": true, "operation_id": accepted_operation_id }


## Returns a synchronous rejection that allocated no operation.
func _rejection(code: StringName, retryable: bool) -> Dictionary:
	return { "ok": false, "failure": _make_failure(code, retryable) }


## Creates one admitted roster row owned by SessionService.
func _roster_row(participant_id: int, display_name: String) -> Dictionary:
	return {
		"participant_id": participant_id,
		"display_name": display_name,
		"phase": &"ADMITTED",
	}


## Returns admitted rows in stable participant order for presentation and tests.
func _roster_view() -> Array[Dictionary]:
	var participant_ids: Array = _host_state.roster_by_participant.keys()
	participant_ids.sort()
	var rows: Array[Dictionary] = []
	for participant_id: int in participant_ids:
		rows.append(_host_state.roster_by_participant[participant_id].duplicate(true))

	return rows


## Returns monotonic local seconds for connection and cleanup deadlines.
func _now_seconds() -> float:
	return Time.get_ticks_msec() / 1000.0


## Emits a copied view so presentation cannot mutate owned state.
func _emit_changed() -> void:
	changed.emit(view())
