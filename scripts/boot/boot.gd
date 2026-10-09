class_name Boot
extends Node
## Coordinates process-lifetime services and authored views from the saved Boot scene.

const DISTRICT_ID: StringName = &"brackett_island"
const ENET_PROVIDER_ID: StringName = &"enet"
const SMOKE_ARGUMENT: String = "--m1-a1-1-smoke"
const EXPORT_SMOKE_ARGUMENT: String = "--s08-x-export-smoke"
const EXPORT_SMOKE_FRAMES: int = 30

var _smoke_failures: Array[String] = []

@onready var _session: SessionService = $Session
@onready var _main_menu: MainMenu = $View/MainMenu
@onready var _session_status: SessionStatus = $View/SessionStatus


## Binds authored children and optionally starts a bounded shell smoke.
func _ready() -> void:
	_session.changed.connect(_on_session_changed)
	_session.completed.connect(_on_session_completed)
	_main_menu.standalone_requested.connect(_on_standalone_requested)
	_main_menu.host_requested.connect(_on_host_requested)
	_main_menu.join_requested.connect(_on_join_requested)
	_main_menu.quit_requested.connect(_on_quit_requested)
	_session_status.primary_requested.connect(_on_status_primary_requested)
	_session_status.back_requested.connect(_on_status_back_requested)
	_main_menu.show_main()
	_session_status.present(_session.view())
	_print_export_boot()
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	if SMOKE_ARGUMENT in arguments or EXPORT_SMOKE_ARGUMENT in arguments:
		_run_smoke.call_deferred(EXPORT_SMOKE_ARGUMENT in arguments)


## Starts the shared no-network session path from the main menu.
func _on_standalone_requested() -> void:
	_handle_acceptance(_session.start_standalone(DISTRICT_ID))


## Sends host intent to the provider-neutral session boundary.
func _on_host_requested(port: int) -> void:
	_handle_acceptance(
		_session.host(
			{
				"provider_id": ENET_PROVIDER_ID,
				"district_id": DISTRICT_ID,
				"capacity": 4,
				"provider_options": { "port": port },
			}
		)
	)


## Rejects raw endpoint text until M1-A1.2 supplies ENet target parsing.
func _on_join_requested(_address: String, _port: int) -> void:
	_main_menu.show_feedback("Direct ENet joining arrives with the transport in M1-A1.2.")


## Routes cancel, leave, or retry according to the service-owned phase.
func _on_status_primary_requested() -> void:
	var current: Dictionary = _session.view()
	var phase: StringName = current.phase
	var result: Dictionary
	if phase == SessionService.PHASE_ACTIVE:
		result = _session.leave()
	elif phase == SessionService.PHASE_IDLE:
		result = _session.retry()
	else:
		result = _session.cancel(current.operation_id)

	_handle_acceptance(result)


## Dismisses status only after cleanup has restored idle.
func _on_status_back_requested() -> void:
	if _session.view().phase == SessionService.PHASE_IDLE:
		_session_status.visible = false
		_main_menu.show_main()


## Applies immutable session views to the authored menu and status scenes.
func _on_session_changed(current: Dictionary) -> void:
	_session_status.present(current)
	var phase: StringName = current.phase
	_main_menu.visible = phase == SessionService.PHASE_IDLE and current.failure.is_empty()
	if phase == SessionService.PHASE_IDLE and current.failure.is_empty():
		_main_menu.show_main()


## Restores the menu after normal cancel/leave while retaining actionable failures.
func _on_session_completed(_operation_id: int, result: Dictionary) -> void:
	var failure: Dictionary = result.get("failure", {})
	if failure.get("code", &"") == &"CANCELED":
		_session_status.visible = false
		_main_menu.show_main()


## Exits through the Boot lifetime owner rather than from a reusable menu child.
func _on_quit_requested() -> void:
	get_tree().quit()


## Displays a synchronous rejection that allocated no operation.
func _handle_acceptance(result: Dictionary) -> void:
	if result.get("ok", false):
		return

	var failure: Dictionary = result.get("failure", {})
	_main_menu.show_feedback(String(failure.get("code", &"REQUEST_REJECTED")).capitalize())


## Exercises saved composition, standalone start, bounded leave, and clean exit.
func _run_smoke(export_compatibility: bool) -> void:
	Engine.max_fps = 60
	_check(_main_menu.visible, "main menu is initially visible")
	_check(_session_status != null, "session status scene is composed")
	var start: Dictionary = _session.start_standalone(DISTRICT_ID)
	_check(start.get("ok", false), "standalone operation is accepted")
	await get_tree().process_frame
	_check(_session.view().phase == SessionService.PHASE_ACTIVE, "standalone reaches ACTIVE")
	var leave_result: Dictionary = _session.leave()
	_check(leave_result.get("ok", false), "leave operation is accepted")
	await get_tree().process_frame
	_check(_session.view().phase == SessionService.PHASE_IDLE, "leave returns to IDLE")
	_check(_main_menu.visible, "main menu is restored")
	for _frame: int in range(EXPORT_SMOKE_FRAMES):
		await get_tree().process_frame  # gdstyle:ignore=quality/await-in-loop

	var receipt: Dictionary = {
		"event": "smoke_complete",
		"ok": _smoke_failures.is_empty(),
		"failures": _smoke_failures,
		"frames": EXPORT_SMOKE_FRAMES,
		"max_fps": Engine.max_fps,
		"phase": _session.view().phase,
	}
	print("M1-A1.1 " + JSON.stringify(receipt))
	if export_compatibility:
		print("S08-X " + JSON.stringify(receipt))

	get_tree().quit(0 if _smoke_failures.is_empty() else 1)


## Retains S08-X exclusion observations after replacing its temporary main scene.
func _print_export_boot() -> void:
	if OS.has_feature("editor"):
		return

	_check(
		get_tree().root.get_node_or_null("MCPRuntimeServer") == null,
		"MCP runtime autoload node is absent in exports",
	)
	_check(
		not ProjectSettings.has_setting("autoload/MCPRuntimeServer"),
		"MCP runtime autoload setting is absent in exports",
	)
	_check(not ClassDB.class_exists("Steam"), "GodotSteam class is absent")
	_check(not Engine.has_singleton("Steam"), "GodotSteam singleton is absent")
	print(
		"S08-X "
		+ JSON.stringify(
			{
				"event": "boot",
				"ok": _smoke_failures.is_empty(),
				"failures": _smoke_failures,
				"main_scene": "res://scenes/boot/boot.tscn",
				"max_fps": Engine.max_fps,
			}
		)
	)


## Records one independently named smoke contract.
func _check(condition: bool, contract: String) -> void:
	if not condition:
		_smoke_failures.append(contract)
