class_name Boot
extends Node
## Coordinates process-lifetime services and authored views from the saved Boot scene.

const DISTRICT_ID: StringName = &"brackett_island"
const ENET_PROVIDER_ID: StringName = &"enet"
const SMOKE_ARGUMENT: String = "--m1-a1-1-smoke"
const EXPORT_SMOKE_ARGUMENT: String = "--s08-x-export-smoke"
const EXPORT_SMOKE_FRAMES: int = 30
const MATCH_SCENE: PackedScene = preload("res://scenes/match/match.tscn")
const PLAYER_SCENE: PackedScene = preload("res://scenes/entities/player.tscn")

var _smoke_failures: Array[String] = []
var _last_join_address: String = ""
var _last_join_port: int = 0
var _match: Node3D

@onready var _session: SessionService = $Session
@onready var _enet_transport: ENetTransport = $Session/ENetTransport
@onready var _local_settings: LocalSettings = $LocalSettings
@onready var _main_menu: MainMenu = $View/MainMenu
@onready var _session_status: SessionStatus = $View/SessionStatus
@onready var _settings_menu: SettingsMenu = $View/SettingsMenu


## Binds authored children and optionally starts a bounded shell smoke.
func _ready() -> void:
	var registration: Dictionary = _session.register_transport(_enet_transport)
	if not registration.get("ok", false):
		_smoke_failures.append("ENet transport registration failed")

	var settings_error: Error = _local_settings.load_settings()
	if not _settings_menu.configure(_local_settings):
		_smoke_failures.append("Settings owner injection failed")

	_session.changed.connect(_on_session_changed)
	_session.completed.connect(_on_session_completed)
	_session.standalone_started.connect(_on_standalone_started)
	_session.participant_admitted.connect(_on_participant_admitted)
	_session.participant_disconnected.connect(_on_participant_disconnected)
	_main_menu.standalone_requested.connect(_on_standalone_requested)
	_main_menu.host_requested.connect(_on_host_requested)
	_main_menu.join_requested.connect(_on_join_requested)
	_main_menu.settings_requested.connect(_on_settings_requested)
	_main_menu.quit_requested.connect(_on_quit_requested)
	_session_status.primary_requested.connect(_on_status_primary_requested)
	_session_status.back_requested.connect(_on_status_back_requested)
	_settings_menu.closed.connect(_on_settings_closed)
	_main_menu.show_main()
	if settings_error != OK:
		_main_menu.show_feedback("Could not load settings. Safe defaults are active.")
	_session_status.present(_session.view())
	_print_export_boot()
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	if SMOKE_ARGUMENT in arguments or EXPORT_SMOKE_ARGUMENT in arguments:
		_run_smoke.call_deferred(EXPORT_SMOKE_ARGUMENT in arguments)


## Starts the shared no-network session path from the main menu.
func _on_standalone_requested() -> void:
	_clear_join_retry()
	_handle_acceptance(_session.start_standalone(DISTRICT_ID))


## Sends host intent to the provider-neutral session boundary.
func _on_host_requested(port: int) -> void:
	_clear_join_retry()
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


## Parses direct endpoint text inside ENet before starting the shared join flow.
func _on_join_requested(address: String, port: int) -> void:
	_last_join_address = address
	_last_join_port = port
	var parsed: Dictionary = _enet_transport.parse_endpoint(address, port)
	if not parsed.get("ok", false):
		_handle_acceptance(parsed)
		return

	_handle_acceptance(_session.join(parsed.target))


## Routes cancel, leave, or retry according to the service-owned phase.
func _on_status_primary_requested() -> void:
	var current: Dictionary = _session.view()
	var phase: StringName = current.phase
	var result: Dictionary
	if phase == SessionService.PHASE_ACTIVE:
		_teardown_match()
		result = _session.leave()
	elif phase == SessionService.PHASE_IDLE and not _last_join_address.is_empty():
		var parsed: Dictionary = _enet_transport.parse_endpoint(
			_last_join_address, _last_join_port
		)
		result = _session.join(parsed.target) if parsed.get("ok", false) else parsed
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


## Creates the saved standalone match, local actor, and one process-local rig binding.
func _on_standalone_started(_operation_id: int, district_id: StringName) -> void:
	if district_id != DISTRICT_ID or is_instance_valid(_match):
		return

	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	var runtime_entities: Node3D = match.get_node("RuntimeEntities") as Node3D
	var spawn: Marker3D = match.get_node("Anchors/PlayerSpawns/Spawn01") as Marker3D
	var rig: LocalRig = match.get_node("LocalRig") as LocalRig
	actor.name = "LocalPlayer"
	# Both saved containers are identity transforms under Match; retain the authored spawn pose.
	actor.transform = spawn.transform
	runtime_entities.add_child(actor)
	$View.add_child(match)
	_match = match
	rig.leave_requested.connect(_on_local_match_leave_requested)
	if not rig.bind_actor(actor):
		push_error("Standalone LocalRig could not bind its saved local player")
		_teardown_match()
		_session.leave()
		return

	_main_menu.visible = false
	_session_status.visible = false


## Creates the saved Match and hands one admitted ENet identity to its replication root.
func _start_network_match(current: Dictionary) -> void:
	if is_instance_valid(_match):
		return
	if current.provider_id != ENET_PROVIDER_ID or current.operation_kind not in [
		SessionService.OPERATION_HOST,
		SessionService.OPERATION_JOIN,
	]:
		return

	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	$View.add_child(match)
	_match = match
	var replication: MatchReplication = match.get_node("Replication") as MatchReplication
	replication.name = "Replication"
	var configured: bool = replication.configure_network(
		current.session_id,
		current.local_participant_id,
		current.operation_kind == SessionService.OPERATION_HOST,
	)
	if not configured:
		push_error("Network Match replication could not accept Session identity")
		_teardown_match()
		_session.leave()
		return

	var rig: LocalRig = match.get_node("LocalRig") as LocalRig
	rig.leave_requested.connect(_on_local_match_leave_requested)
	_main_menu.visible = false
	_session_status.visible = false


## Hands a Session-owned sender mapping down to the current host Match.
func _on_participant_admitted(native_peer_id: int, participant_id: int) -> void:
	if not is_instance_valid(_match):
		return
	var replication: MatchReplication = _match.get_node("Replication") as MatchReplication
	if not replication.admit_peer(native_peer_id, participant_id):
		push_error("Match replication rejected current Session participant mapping")


## Retires one disconnected sender and its authoritative player from Match.
func _on_participant_disconnected(native_peer_id: int, participant_id: int) -> void:
	if not is_instance_valid(_match):
		return
	var replication: MatchReplication = _match.get_node("Replication") as MatchReplication
	replication.remove_peer(native_peer_id, participant_id)


## Closes local input and asks the process session owner to leave active play.
func _on_local_match_leave_requested() -> void:
	if _session.view().phase != SessionService.PHASE_ACTIVE:
		return

	_teardown_match()
	_handle_acceptance(_session.leave())


## Removes match-owned actors and rig state before returning to process-lifetime menus.
func _teardown_match() -> void:
	if not is_instance_valid(_match):
		_match = null
		return

	var rig: LocalRig = _match.get_node_or_null("LocalRig") as LocalRig
	if rig != null:
		rig.unbind_actor()
	_match.queue_free()
	_match = null


## Applies immutable session views to the authored menu and status scenes.
func _on_session_changed(current: Dictionary) -> void:
	_session_status.present(current)
	var phase: StringName = current.phase
	if phase != SessionService.PHASE_ACTIVE:
		_teardown_match()
	else:
		_start_network_match(current)

	var playing_standalone: bool = phase == SessionService.PHASE_ACTIVE and (
		is_instance_valid(_match)
	)
	_main_menu.visible = (
		phase == SessionService.PHASE_IDLE and current.failure.is_empty()
	)
	_session_status.visible = _session_status.visible and not playing_standalone
	if phase == SessionService.PHASE_IDLE and current.failure.is_empty():
		_main_menu.show_main()


## Restores the menu after normal cancel/leave while retaining actionable failures.
func _on_session_completed(_operation_id: int, result: Dictionary) -> void:
	var failure: Dictionary = result.get("failure", {})
	if failure.get("code", &"") == &"CANCELED":
		_session_status.visible = false
		_main_menu.show_main()


## Opens the injected settings view while Boot remains the only sibling coordinator.
func _on_settings_requested() -> void:
	_main_menu.visible = false
	_session_status.visible = false
	if not _settings_menu.open():
		_main_menu.show_main()
		_main_menu.show_feedback("Settings are unavailable.")


## Restores the main menu after save or cancellation closes settings.
func _on_settings_closed() -> void:
	_main_menu.show_main()


## Exits through the Boot lifetime owner rather than from a reusable menu child.
func _on_quit_requested() -> void:
	get_tree().quit()


## Clears raw endpoint text when the accepted operation is not a direct join.
func _clear_join_retry() -> void:
	_last_join_address = ""
	_last_join_port = 0


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
