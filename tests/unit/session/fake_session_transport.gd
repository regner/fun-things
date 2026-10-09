class_name FakeSessionTransport
extends SessionTransport
## Correlated controllable transport used only by session contract tests.

const PROVIDER_ID: StringName = &"fake"

var auto_ready: bool = true
var auto_close: bool = true
var ready_delay_seconds: float = 0.01
var close_delay_seconds: float = 0.01
var opened_operations: Array[int] = []
var closed_operations: Array[int] = []
var disposed_operations: Array[int] = []
var disposed_peer_count: int = 0
var available: bool = true
var _adapter_generation: int = 1
var _current_operation_id: int = 0


## Returns the stable fake provider identifier.
func provider_id() -> StringName:
	return PROVIDER_ID


## Reports whether tests have left this fake reusable.
func is_available() -> bool:
	return available


## Reports the production-shaped four-stream capability profile.
func capabilities() -> Dictionary:
	return {
		"available": available,
		"identity_assurance": &"NONE",
		"streams": [
			_stream(0, &"RELIABLE_ORDERED", &"DURABLE", 4096),
			_stream(1, &"RELIABLE_ORDERED", &"DURABLE", 16 * 1024),
			_stream(2, &"UNRELIABLE_ORDERED", &"REPLACEABLE_LOSSY", 1200),
			_stream(3, &"UNRELIABLE_ORDERED", &"REPLACEABLE_LOSSY", 1200),
		],
	}


## Confirms callback identity against the fake's active operation and generation.
func is_current_connection_token(
	operation_id: int,
	connection_token: int,
	native_peer_id: int,
) -> bool:
	return (
		operation_id == _current_operation_id
		and connection_token == connection_token_for(native_peer_id)
	)


## Accepts a host operation and optionally schedules its correlated peer callback.
func open_host(operation_id: int, _options: Dictionary) -> Dictionary:
	return _open(operation_id)


## Accepts a matching fake target and optionally schedules its correlated peer callback.
func open_client(operation_id: int, target: Dictionary) -> Dictionary:
	if target.get("provider_id", &"") != PROVIDER_ID:
		return _failure(&"TARGET_EXPIRED")

	return _open(operation_id)


## Schedules a correlated close result unless the test is exercising timeout.
func close(operation_id: int) -> Dictionary:
	closed_operations.append(operation_id)
	_current_operation_id = 0
	_adapter_generation += 1
	if auto_close:
		_deliver_closed(operation_id)

	return _success()


## Records disposal so tests can prove obsolete native results never attach.
func dispose_obsolete(operation_id: int, peer: MultiplayerPeer) -> void:
	peer.close()
	disposed_operations.append(operation_id)
	disposed_peer_count += 1


## Emits a peer callback on demand, including deliberately obsolete operations.
func emit_peer(operation_id: int) -> void:
	peer_ready.emit(operation_id, OfflineMultiplayerPeer.new())


## Emits one provider connection callback, including deliberately obsolete tokens.
func emit_connected(operation_id: int, connection_token: int, native_peer_id: int) -> void:
	connected.emit(operation_id, connection_token, native_peer_id)


## Emits one provider disconnection callback with explicit correlation identity.
func emit_disconnected(operation_id: int, connection_token: int, native_peer_id: int) -> void:
	disconnected.emit(
		operation_id,
		connection_token,
		native_peer_id,
		{ "code": &"CONNECT_FAILED", "retryable": true },
	)


## Returns the token for one native peer in the fake's current generation.
func connection_token_for(native_peer_id: int) -> int:
	return (_adapter_generation << 32) | native_peer_id


## Emits a provider failure on demand for the named operation.
func emit_failure(operation_id: int, code: StringName = &"CONNECT_FAILED") -> void:
	failed.emit(operation_id, { "code": code, "retryable": true })


## Emits a close callback on demand with an explicit reuse disposition.
func emit_closed(operation_id: int, reuse_status: StringName = REUSE_SAFE) -> void:
	closed.emit(operation_id, { "reuse_status": reuse_status })


## Accepts and records one provider operation.
func _open(operation_id: int) -> Dictionary:
	if not available:
		return _failure(&"SERVICE_UNAVAILABLE")

	_current_operation_id = operation_id
	opened_operations.append(operation_id)
	if auto_ready:
		_deliver_peer(operation_id)

	return _success()


## Delivers a peer after the configured fake delay.
func _deliver_peer(operation_id: int) -> void:
	await get_tree().create_timer(ready_delay_seconds).timeout
	emit_peer(operation_id)


## Delivers a close result after the configured fake delay.
func _deliver_closed(operation_id: int) -> void:
	await get_tree().create_timer(close_delay_seconds).timeout
	emit_closed(operation_id)


## Builds one capability row without duplicating stream policy literals.
func _stream(
	channel: int,
	delivery: StringName,
	queue_policy: StringName,
	max_payload_bytes: int,
) -> Dictionary:
	return {
		"channel": channel,
		"delivery": delivery,
		"queue_policy": queue_policy,
		"max_logical_payload_bytes": max_payload_bytes,
	}
