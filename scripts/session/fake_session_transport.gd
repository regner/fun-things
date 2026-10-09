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
