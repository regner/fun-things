class_name SessionService
extends Node
## Owns process-lifetime session operations, phase, provider selection, and cleanup.

signal changed(view: Dictionary)
signal completed(operation_id: int, result: Dictionary)
signal standalone_started(operation_id: int, district_id: StringName)

const CLOSE_TIMEOUT_SECONDS: float = 5.0
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
var _phase: StringName = PHASE_IDLE
var _operation_id: int = 0
var _next_operation_id: int = 1
var _operation_kind: StringName = OPERATION_NONE
var _provider_id: StringName = &""
var _session_id: String = ""
var _failure: Dictionary = {}
var _transport: SessionTransport
var _close_deadline_seconds: float = 0.0
var _close_result: Dictionary = {}
var _last_request: Dictionary = {}
var _completed_operations: Dictionary[int, bool] = {}
var _provider_reusable: bool = true
var _ignored_callback_count: int = 0


## Enforces the shared monotonic close deadline without extending it per component.
func _process(_delta: float) -> void:
	if _phase != PHASE_CLOSING:
		return

	if Time.get_ticks_msec() / 1000.0 < _close_deadline_seconds:
		return

	_provider_reusable = false
	_close_result = {
		"reuse_status": SessionTransport.REUSE_UNAVAILABLE,
		"failure": _make_failure(&"CLEANUP_TIMEOUT", false),
	}
	_finish_close()


## Registers the one fixed provider binding while the service is idle.
func register_transport(transport: SessionTransport) -> Dictionary:
	if _phase != PHASE_IDLE:
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
	_transport.failed.connect(_on_transport_failed)
	_transport.closed.connect(_on_transport_closed)
	_provider_reusable = transport.is_available()
	return _acceptance(0)


## Accepts a host request for the registered provider or rejects it synchronously.
func host(request: Dictionary) -> Dictionary:
	if _phase != PHASE_IDLE:
		return _rejection(&"BUSY", true)
	if not _valid_host_request(request):
		return _rejection(&"INVALID_REQUEST", false)
	if not _can_use_provider(request.provider_id):
		return _rejection(&"SERVICE_UNAVAILABLE", true)

	_last_request = { "kind": OPERATION_HOST, "payload": request.duplicate(true) }
	_begin_operation(OPERATION_HOST, PHASE_STARTING, request.provider_id)
	var adapter_result: Dictionary = _transport.open_host(
		_operation_id, request.get("provider_options", {})
	)
	if not adapter_result.get("ok", false):
		_begin_close(_adapter_failure(adapter_result))

	return _acceptance(_operation_id)


## Accepts an opaque provider-owned join target or rejects it synchronously.
func join(target: Dictionary) -> Dictionary:
	if _phase != PHASE_IDLE:
		return _rejection(&"BUSY", true)
	if not _valid_join_target(target):
		return _rejection(&"INVALID_REQUEST", false)
	if not _can_use_provider(target.provider_id):
		return _rejection(&"SERVICE_UNAVAILABLE", true)

	_last_request = { "kind": OPERATION_JOIN, "payload": target.duplicate(true) }
	_begin_operation(OPERATION_JOIN, PHASE_CONNECTING, target.provider_id)
	var adapter_result: Dictionary = _transport.open_client(_operation_id, target)
	if not adapter_result.get("ok", false):
		_begin_close(_adapter_failure(adapter_result))

	return _acceptance(_operation_id)


## Starts the no-network authority path without creating a fake remote peer.
func start_standalone(district_id: StringName) -> Dictionary:
	if _phase != PHASE_IDLE:
		return _rejection(&"BUSY", true)
	if district_id == &"" or district_id.to_utf8_buffer().size() > 128:
		return _rejection(&"INVALID_REQUEST", false)

	_last_request = { "kind": OPERATION_STANDALONE, "payload": district_id }
	_begin_operation(OPERATION_STANDALONE, PHASE_STARTING, PROVIDER_STANDALONE)
	_activate_standalone.call_deferred(_operation_id, district_id)
	return _acceptance(_operation_id)


## Cancels only the accepted in-flight operation and shares its cleanup completion.
func cancel(requested_operation_id: int) -> Dictionary:
	if requested_operation_id != _operation_id:
		return _rejection(&"STALE_OPERATION", false)
	if _phase == PHASE_CLOSING:
		return _acceptance(_operation_id)
	if _phase in [PHASE_IDLE, PHASE_ACTIVE]:
		return _rejection(&"NOT_CANCELABLE", false)

	_begin_close(_make_failure(&"CANCELED", true))
	return _acceptance(_operation_id)


## Leaves an active session or returns the already-running close operation.
func leave() -> Dictionary:
	if _phase == PHASE_CLOSING:
		return _acceptance(_operation_id)
	if _phase != PHASE_ACTIVE:
		return _rejection(&"NOT_ACTIVE", false)

	_begin_operation(OPERATION_LEAVE, PHASE_CLOSING, _provider_id)
	_close_deadline_seconds = Time.get_ticks_msec() / 1000.0 + close_timeout_seconds
	_close_result = { "reuse_status": SessionTransport.REUSE_SAFE }
	_detach_peer()
	if _provider_id == PROVIDER_STANDALONE:
		_finish_close.call_deferred()
	else:
		_request_transport_close()

	_emit_changed()
	return _acceptance(_operation_id)


## Repeats the last accepted start request only after cleanup has restored idle.
func retry() -> Dictionary:
	if _phase != PHASE_IDLE:
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
		"phase": _phase,
		"operation_id": _operation_id if _phase != PHASE_IDLE else 0,
		"operation_kind": _operation_kind,
		"provider_id": _provider_id,
		"session_id": _session_id,
		"capacity": _current_capacity(),
		"roster": [],
		"failure": _failure.duplicate(true),
		"provider_reusable": _provider_reusable,
	}


## Exposes ignored callback count for lifecycle diagnostics and focused tests.
func ignored_callback_count() -> int:
	return _ignored_callback_count


## Completes a still-current standalone start after callers can observe STARTING.
func _activate_standalone(source_operation_id: int, district_id: StringName) -> void:
	if source_operation_id != _operation_id or _phase != PHASE_STARTING:
		_ignored_callback_count += 1
		return

	_session_id = Crypto.new().generate_random_bytes(16).hex_encode()
	_phase = PHASE_ACTIVE
	standalone_started.emit(source_operation_id, district_id)
	_complete(source_operation_id, { "ok": true, "view": view() })
	_emit_changed()


## Begins one accepted operation with a process-unique positive identifier.
func _begin_operation(kind: StringName, phase: StringName, provider_id: StringName) -> void:
	_operation_id = _next_operation_id
	_next_operation_id += 1
	_operation_kind = kind
	_phase = phase
	_provider_id = provider_id
	_failure = {}
	_close_result = {}
	_emit_changed()


## Invalidates producers and enters the one bounded cleanup path.
func _begin_close(failure: Dictionary) -> void:
	if _phase == PHASE_CLOSING:
		return

	_phase = PHASE_CLOSING
	_failure = failure.duplicate(true)
	_close_deadline_seconds = Time.get_ticks_msec() / 1000.0 + close_timeout_seconds
	_close_result = { "reuse_status": SessionTransport.REUSE_SAFE }
	_detach_peer()
	if _provider_id == PROVIDER_STANDALONE:
		_finish_close.call_deferred()
	else:
		_request_transport_close()

	_emit_changed()


## Requests provider cleanup after session state and peer access are invalidated.
func _request_transport_close() -> void:
	if _transport == null:
		_finish_close.call_deferred()
		return

	var close_acceptance: Dictionary = _transport.close(_operation_id)
	if not close_acceptance.get("ok", false):
		_provider_reusable = false
		_close_result = {
			"reuse_status": SessionTransport.REUSE_UNAVAILABLE,
			"failure": _adapter_failure(close_acceptance),
		}
		_finish_close.call_deferred()


## Restores idle once and emits the accepted operation's terminal result.
func _finish_close() -> void:
	if _phase != PHASE_CLOSING:
		return

	var finished_operation: int = _operation_id
	var terminal_failure: Dictionary = _failure.duplicate(true)
	var result: Dictionary = {
		"ok": terminal_failure.is_empty(),
		"failure": terminal_failure,
		"close": _close_result.duplicate(true),
	}
	_session_id = ""
	_phase = PHASE_IDLE
	_operation_kind = OPERATION_NONE
	_provider_id = &""
	_operation_id = 0
	_close_deadline_seconds = 0.0
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


## Accepts only the current provider callback and cleans every obsolete peer.
func _on_peer_ready(source_operation_id: int, peer: MultiplayerPeer) -> void:
	if source_operation_id != _operation_id or _phase not in [PHASE_STARTING, PHASE_CONNECTING]:
		_ignored_callback_count += 1
		if _transport != null:
			_transport.dispose_obsolete(source_operation_id, peer)
		else:
			peer.close()

		return

	multiplayer.multiplayer_peer = peer
	_phase = PHASE_ACTIVE
	_session_id = Crypto.new().generate_random_bytes(16).hex_encode()
	_complete(source_operation_id, { "ok": true, "view": view() })
	_emit_changed()


## Converts a current provider failure into bounded cleanup without double completion.
func _on_transport_failed(source_operation_id: int, failure: Dictionary) -> void:
	if source_operation_id != _operation_id or _phase in [PHASE_IDLE, PHASE_CLOSING]:
		_ignored_callback_count += 1
		return

	_begin_close(failure)


## Applies only the current close result; late results remain cleanup-only.
func _on_transport_closed(source_operation_id: int, result: Dictionary) -> void:
	if source_operation_id != _operation_id or _phase != PHASE_CLOSING:
		_ignored_callback_count += 1
		return

	_close_result = result.duplicate(true)
	_provider_reusable = result.get("reuse_status", SessionTransport.REUSE_UNAVAILABLE) == (
		SessionTransport.REUSE_SAFE
	)
	_finish_close()


## Removes a registered provider's signal links before replacing it while idle.
func _disconnect_transport(transport: SessionTransport) -> void:
	if transport.peer_ready.is_connected(_on_peer_ready):
		transport.peer_ready.disconnect(_on_peer_ready)
	if transport.failed.is_connected(_on_transport_failed):
		transport.failed.disconnect(_on_transport_failed)
	if transport.closed.is_connected(_on_transport_closed):
		transport.closed.disconnect(_on_transport_closed)


## Replaces any native peer before provider cleanup can publish completion.
func _detach_peer() -> void:
	multiplayer.multiplayer_peer = OfflineMultiplayerPeer.new()


## Checks provider registration, availability, and timeout reuse fences.
func _can_use_provider(provider_id: StringName) -> bool:
	return (
		_transport != null
		and _transport.provider_id() == provider_id
		and _transport.is_available()
		and _provider_reusable
	)


## Returns capacity for the current accepted session kind.
func _current_capacity() -> int:
	if _operation_kind == OPERATION_STANDALONE:
		return 1
	if _operation_kind == OPERATION_HOST and _last_request.payload is Dictionary:
		return _last_request.payload.get("capacity", 0)

	return 0


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
		and (district_id as StringName).to_utf8_buffer().size() <= 128
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


## Normalizes an adapter's immediate failure into the session failure shape.
func _adapter_failure(adapter_result: Dictionary) -> Dictionary:
	var failure: Variant = adapter_result.get("failure", {})
	if failure is Dictionary and not failure.is_empty():
		return (failure as Dictionary).duplicate(true)

	return _make_failure(&"PROVIDER_FAILED", true)


## Constructs one UI-safe normalized failure record.
func _make_failure(code: StringName, retryable: bool) -> Dictionary:
	return {
		"code": code,
		"phase": _phase,
		"operation_id": _operation_id,
		"retryable": retryable,
		"message_key": StringName("session." + String(code).to_lower()),
	}


## Returns a synchronous accepted-operation result.
func _acceptance(accepted_operation_id: int) -> Dictionary:
	return { "ok": true, "operation_id": accepted_operation_id }


## Returns a synchronous rejection that allocated no operation.
func _rejection(code: StringName, retryable: bool) -> Dictionary:
	return { "ok": false, "failure": _make_failure(code, retryable) }


## Emits a copied view so presentation cannot mutate owned state.
func _emit_changed() -> void:
	changed.emit(view())
