extends GutTest
## Verifies the production session operation and cleanup contracts through public APIs.

const WAIT_SECONDS: float = 0.08

var _service: SessionService
var _transport: FakeSessionTransport
var _completions: Dictionary[int, Array] = {}


## Creates a fresh process-lifetime service and correlated fake for each test.
func before_each() -> void:
	_completions.clear()
	_service = SessionService.new()
	_transport = FakeSessionTransport.new()
	add_child_autofree(_service)
	add_child_autofree(_transport)
	_service.completed.connect(_on_completed)
	var registration: Dictionary = _service.register_transport(_transport)
	assert_true(registration.ok, "the fixed fake provider registers while idle")


## Proves standalone accepts once, rejects busy work, and leaves through cleanup.
func test_standalone_reaches_active_and_completes_once() -> void:
	var accepted: Dictionary = _service.start_standalone(&"brackett_island")
	assert_true(accepted.ok)
	var busy: Dictionary = _service.start_standalone(&"brackett_island")
	assert_false(busy.ok)
	assert_eq(busy.failure.code, &"BUSY")
	await get_tree().process_frame
	assert_eq(_service.view().phase, SessionService.PHASE_ACTIVE)
	assert_eq(_completion_count(accepted.operation_id), 1)

	var leave_result: Dictionary = _service.leave()
	var duplicate_leave: Dictionary = _service.leave()
	assert_eq(duplicate_leave.operation_id, leave_result.operation_id)
	await get_tree().process_frame
	assert_eq(_service.view().phase, SessionService.PHASE_IDLE)
	assert_eq(_completion_count(leave_result.operation_id), 1)


## Proves cancel is idempotent and a stale peer is cleaned before retry attaches.
func test_cancel_late_callback_and_retry_are_correlated() -> void:
	_transport.auto_ready = false
	var first: Dictionary = _service.host(_host_request())
	assert_true(first.ok)
	assert_eq(_service.host(_host_request()).failure.code, &"BUSY")
	assert_true(_service.cancel(first.operation_id).ok)
	assert_true(_service.cancel(first.operation_id).ok)
	await get_tree().create_timer(WAIT_SECONDS).timeout
	assert_eq(_service.view().phase, SessionService.PHASE_IDLE)
	assert_eq(_completion_count(first.operation_id), 1)
	assert_eq(_completions[first.operation_id][0].failure.code, &"CANCELED")

	_transport.emit_peer(first.operation_id)
	await get_tree().process_frame
	assert_eq(_transport.disposed_peer_count, 1)
	assert_eq(_completion_count(first.operation_id), 1)

	var retry_result: Dictionary = _service.retry()
	assert_true(retry_result.ok)
	assert_gt(retry_result.operation_id, first.operation_id)
	_transport.emit_peer(retry_result.operation_id)
	await get_tree().process_frame
	assert_eq(_service.view().phase, SessionService.PHASE_ACTIVE)
	assert_eq(_completion_count(retry_result.operation_id), 1)


## Proves a silent provider cannot extend close beyond the shared local deadline.
func test_close_timeout_forces_unavailable_without_double_completion() -> void:
	_transport.auto_ready = false
	_transport.auto_close = false
	_service.close_timeout_seconds = 0.02
	var host_result: Dictionary = _service.host(_host_request())
	_transport.emit_peer(host_result.operation_id)
	await get_tree().process_frame
	assert_eq(_service.view().phase, SessionService.PHASE_ACTIVE)

	var leave_result: Dictionary = _service.leave()
	await get_tree().create_timer(WAIT_SECONDS).timeout
	assert_eq(_service.view().phase, SessionService.PHASE_IDLE)
	assert_eq(_completion_count(leave_result.operation_id), 1)
	var close_result: Dictionary = _completions[leave_result.operation_id][0].close
	assert_eq(close_result.reuse_status, SessionTransport.REUSE_UNAVAILABLE)
	assert_eq(close_result.failure.code, &"CLEANUP_TIMEOUT")

	var registration: Dictionary = _service.register_transport(_transport)
	assert_true(registration.ok, "re-registering the fixed instance is idempotent")
	var retry_result: Dictionary = _service.retry()
	assert_false(retry_result.ok)
	assert_eq(retry_result.failure.code, &"SERVICE_UNAVAILABLE")
	assert_eq(_transport.opened_operations.size(), 1)

	_transport.emit_closed(leave_result.operation_id)
	await get_tree().process_frame
	assert_eq(_completion_count(leave_result.operation_id), 1)
	assert_gt(_service.ignored_callback_count(), 0)


## Proves a valid join waits for admission and a provider failure cleans it once.
func test_join_accepts_provider_target_and_waits_for_admission() -> void:
	_transport.auto_ready = false
	var invalid: Dictionary = _service.join({ "provider_id": &"fake" })
	assert_false(invalid.ok)
	assert_eq(invalid.failure.code, &"INVALID_REQUEST")

	var target: Dictionary = {
		"provider_id": &"fake",
		"adapter_generation": 1,
		"kind": &"TRANSPORT_READY",
		"local_handle": 44,
	}
	var accepted: Dictionary = _service.join(target)
	assert_true(accepted.ok)
	_transport.emit_peer(accepted.operation_id)
	await get_tree().process_frame
	assert_eq(_service.view().phase, SessionService.PHASE_CONNECTING)
	assert_eq(_completion_count(accepted.operation_id), 0)

	_transport.emit_failure(accepted.operation_id)
	await get_tree().create_timer(WAIT_SECONDS).timeout
	assert_eq(_service.view().phase, SessionService.PHASE_IDLE)
	assert_eq(_completion_count(accepted.operation_id), 1)
	assert_eq(_completions[accepted.operation_id][0].failure.code, &"CONNECT_FAILED")


## Rejects directory-owned targets until SessionDirectory resolves them for transport.
func test_join_rejects_directory_target_without_opening_transport() -> void:
	var target: Dictionary = {
		"provider_id": &"fake",
		"adapter_generation": 1,
		"kind": &"DIRECTORY",
		"opaque_lobby": "not-transport-ready",
	}
	var result: Dictionary = _service.join(target)
	assert_false(result.ok)
	assert_eq(result.failure.code, &"INVALID_REQUEST")
	assert_true(_transport.opened_operations.is_empty())
	assert_eq(_service.view().phase, SessionService.PHASE_IDLE)


## Publishes capacity and a roster array in idle, standalone, and host views.
func test_view_shape_retains_capacity_for_current_session_kind() -> void:
	var idle_view: Dictionary = _service.view()
	assert_eq(idle_view.capacity, 0)
	assert_true(idle_view.roster is Array)
	assert_true(idle_view.roster.is_empty())

	var standalone: Dictionary = _service.start_standalone(&"brackett_island")
	assert_true(standalone.ok)
	var standalone_starting: Dictionary = _service.view()
	assert_eq(standalone_starting.capacity, 1)
	assert_true(standalone_starting.roster.is_empty())
	await get_tree().process_frame
	assert_eq(_service.view().capacity, 1)
	assert_true(_service.leave().ok)
	await get_tree().process_frame
	assert_eq(_service.view().capacity, 0)

	_transport.auto_ready = false
	var host_result: Dictionary = _service.host(_host_request())
	assert_true(host_result.ok)
	var host_view: Dictionary = _service.view()
	assert_eq(host_view.capacity, 4)
	assert_true(host_view.roster is Array)
	assert_true(host_view.roster.is_empty())


## Distinguishes protocol incompatibility from saved-content identity mismatch.
func test_compatibility_validation_returns_normalized_failures() -> void:
	var exact: Dictionary = {
		"protocol_version": 1,
		"content_id": "development",
		"district_id": &"brackett_island",
		"topology_revision": 0,
		"definition_set_id": "development",
	}
	assert_true(_service.validate_compatibility(exact).ok)

	var wrong_protocol: Dictionary = exact.duplicate(true)
	wrong_protocol.protocol_version = 2
	assert_eq(_service.validate_compatibility(wrong_protocol).failure.code, &"INCOMPATIBLE")

	var wrong_content: Dictionary = exact.duplicate(true)
	wrong_content.content_id = "other"
	assert_eq(_service.validate_compatibility(wrong_content).failure.code, &"CONTENT_INVALID")


## Records terminal signals independently so duplicate emissions stay observable.
func _on_completed(operation_id: int, result: Dictionary) -> void:
	if not _completions.has(operation_id):
		_completions[operation_id] = []

	_completions[operation_id].append(result)


## Returns the observed completion count for one operation.
func _completion_count(operation_id: int) -> int:
	return _completions.get(operation_id, []).size()


## Builds the smallest valid provider-neutral host request.
func _host_request() -> Dictionary:
	return {
		"provider_id": &"fake",
		"district_id": &"brackett_island",
		"capacity": 4,
		"provider_options": { "port": 24_900 },
	}
