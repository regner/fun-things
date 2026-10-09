extends Node
## Drives production SessionService and ENetTransport APIs in one bounded test process.

const PREFIX: String = "M1-A1.2 "
const DEFAULT_PORT: int = 24_900
const PROCESS_TIMEOUT_SECONDS: float = 8.0

var _role: String = ""
var _behavior: String = "leave"
var _port: int = DEFAULT_PORT
var _capacity: int = 4
var _duration_seconds: float = 1.5
var _process_deadline_seconds: float = 0.0
var _active_started_seconds: float = 0.0
var _cancel_requested: bool = false
var _leave_requested: bool = false
var _completed_leaves: int = 0
var _finished: bool = false

@onready var _session: SessionService = $Session
@onready var _transport: ENetTransport = $Session/ENetTransport


## Configures one role from bounded command-line fields and starts its operation.
func _ready() -> void:
	Engine.max_fps = 60
	var options: Dictionary = _parse_arguments(OS.get_cmdline_user_args())
	_role = options.get("role", "")
	_behavior = options.get("behavior", "leave")
	_port = int(options.get("port", DEFAULT_PORT))
	_capacity = int(options.get("capacity", 4))
	_duration_seconds = float(options.get("duration_ms", 1500)) / 1000.0
	_process_deadline_seconds = _now_seconds() + PROCESS_TIMEOUT_SECONDS
	_session.connection_timeout_seconds = float(options.get("connection_timeout_ms", 700)) / 1000.0
	_session.handshake_timeout_seconds = float(options.get("handshake_timeout_ms", 700)) / 1000.0
	_session.changed.connect(_on_session_changed)
	_session.completed.connect(_on_session_completed)

	var compatibility: Dictionary = {
		"protocol_version": int(options.get("protocol", 1)),
		"content_id": String(options.get("content", "development")),
		"district_id": StringName(options.get("district", "brackett_island")),
		"topology_revision": int(options.get("topology", 0)),
		"definition_set_id": String(options.get("definitions", "development")),
	}
	var configured: Dictionary = _session.configure_compatibility(compatibility)
	var registered: Dictionary = _session.register_transport(_transport)
	if not configured.get("ok", false) or not registered.get("ok", false):
		_finish(false, &"HARNESS_SETUP_FAILED")
		return

	if _role == "host":
		_start_host()
	elif _role == "client":
		_start_client()
	else:
		_finish(false, &"INVALID_ROLE")


## Enforces a process deadline and role-specific bounded active duration.
func _process(_delta: float) -> void:
	if _finished:
		return

	var now_seconds: float = _now_seconds()
	if now_seconds >= _process_deadline_seconds:
		_finish(false, &"PROCESS_TIMEOUT")
		return
	if _active_started_seconds <= 0.0:
		return
	if now_seconds - _active_started_seconds < _duration_seconds:
		return

	if _role == "host" or _behavior == "hold":
		_finish(true, &"")


## Starts a listen session through the production host request.
func _start_host() -> void:
	var result: Dictionary = _session.host(
		{
			"provider_id": &"enet",
			"district_id": &"brackett_island",
			"capacity": _capacity,
			"provider_options": { "port": _port, "bind_address": "127.0.0.1" },
		}
	)
	if not result.get("ok", false):
		_finish(false, result.get("failure", {}).get("code", &"HOST_REJECTED"))


## Parses the endpoint inside ENet and starts the production join request.
func _start_client() -> void:
	var parsed: Dictionary = _transport.parse_endpoint("127.0.0.1", _port)
	if not parsed.get("ok", false):
		_finish(false, parsed.get("failure", {}).get("code", &"ENDPOINT_REJECTED"))
		return

	var result: Dictionary = _session.join(parsed.target)
	if not result.get("ok", false):
		_finish(false, result.get("failure", {}).get("code", &"JOIN_REJECTED"))
		return
	if _behavior == "cancel":
		_cancel_requested = true
		_session.cancel(result.operation_id)


## Emits structured state receipts and performs requested leave behavior.
func _on_session_changed(current: Dictionary) -> void:
	var failure_code: StringName = current.get("failure", {}).get("code", &"")
	_print_event(
		{
			"event": "view",
			"role": _role,
			"phase": String(current.phase),
			"failure": String(failure_code),
			"roster_size": current.get("roster", []).size(),
			"participant_id": current.get("local_participant_id", 0),
			"workaround": _transport.bandwidth_workaround_applied(),
		}
	)
	if (
		_role == "client"
		and _behavior == "wait_loss"
		and current.phase == SessionService.PHASE_IDLE
		and failure_code == &"HOST_LOST"
	):
		_finish(true, failure_code)
		return
	if current.phase != SessionService.PHASE_ACTIVE or _active_started_seconds > 0.0:
		return

	_active_started_seconds = _now_seconds()
	_print_event({ "event": "active", "role": _role, "view": current })
	if (
		_role == "client"
		and _behavior in ["leave", "leave_rejoin"]
		and not _leave_requested
	):
		_leave_requested = true
		_leave_after_delay.call_deferred()


## Leaves after ACTIVE was independently observable for at least one frame.
func _leave_after_delay() -> void:
	await get_tree().create_timer(0.1).timeout
	if _session.view().phase == SessionService.PHASE_ACTIVE:
		_session.leave()


## Reports terminal operation results and exits after cleanup restores IDLE.
func _on_session_completed(operation_id: int, result: Dictionary) -> void:
	_print_event(
		{
			"event": "completed",
			"role": _role,
			"operation_id": operation_id,
			"ok": result.get("ok", false),
			"failure": String(result.get("failure", {}).get("code", &"")),
		}
	)
	if _role != "client" or _session.view().phase != SessionService.PHASE_IDLE:
		return
	if _behavior == "hold":
		return
	if _behavior == "leave_rejoin" and _leave_requested and result.get("ok", false):
		_completed_leaves += 1
		if _completed_leaves == 1:
			_leave_requested = false
			_active_started_seconds = 0.0
			_start_client()
			return

	var failure_code: StringName = result.get("failure", {}).get("code", &"")
	var expected_terminal: bool = (
		_leave_requested
		or _cancel_requested
		or failure_code
		in [&"INCOMPATIBLE", &"CONTENT_INVALID", &"SESSION_FULL", &"HOST_LOST", &"UNREACHABLE_HOST"]
	)
	_finish(expected_terminal, failure_code)


## Emits one final receipt and exits with a truthful process status.
func _finish(ok: bool, failure_code: StringName) -> void:
	if _finished:
		return

	_finished = true
	_print_event(
		{
			"event": "finished",
			"role": _role,
			"ok": ok,
			"failure": String(failure_code),
			"phase": String(_session.view().phase),
		}
	)
	get_tree().quit(0 if ok else 1)


## Parses only key-value user arguments needed by the bounded process harness.
func _parse_arguments(arguments: PackedStringArray) -> Dictionary:
	var options: Dictionary = {}
	for argument: String in arguments:
		if not argument.begins_with("--") or "=" not in argument:
			continue

		var separator: int = argument.find("=")
		var key: String = argument.substr(2, separator - 2).replace("-", "_")
		options[key] = argument.substr(separator + 1)

	return options


## Prints one machine-readable receipt without a parallel test protocol.
func _print_event(event: Dictionary) -> void:
	print(PREFIX + JSON.stringify(event))


## Returns monotonic seconds for process-local deadlines.
func _now_seconds() -> float:
	return Time.get_ticks_msec() / 1000.0
