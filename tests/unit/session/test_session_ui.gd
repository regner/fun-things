extends GutTest
## Verifies saved Boot and status scenes honor session visibility and focus contracts.

const BOOT_SCENE: PackedScene = preload("res://scenes/boot/boot.tscn")
const STATUS_SCENE: PackedScene = preload("res://scenes/ui/session_status.tscn")
const ASYNC_TIMEOUT_SECONDS: float = 5.0


## Proves cancellation settles on the main menu rather than a stale failure card.
func test_boot_cancel_restores_main_menu() -> void:
	var boot: Boot = BOOT_SCENE.instantiate()
	add_child_autofree(boot)
	var service: SessionService = boot.get_node("Session")
	var main_menu: MainMenu = boot.get_node("View/MainMenu")
	var status: SessionStatus = boot.get_node("View/SessionStatus")
	var transport := FakeSessionTransport.new()
	transport.auto_ready = false
	add_child_autofree(transport)
	assert_true(service.register_transport(transport).ok)

	var host_result: Dictionary = service.host(_host_request())
	assert_true(host_result.ok)
	assert_true(service.cancel(host_result.operation_id).ok)
	await _assert_phase(service, SessionService.PHASE_IDLE, "Boot host cancellation")

	assert_eq(service.view().phase, SessionService.PHASE_IDLE)
	assert_true(service.view().failure.is_empty())
	assert_true(main_menu.visible)
	assert_false(status.visible)


## Proves Boot parses menu endpoint text and starts the real ENet join lifecycle.
func test_boot_routes_join_form_through_enet_transport() -> void:
	var boot: Boot = BOOT_SCENE.instantiate()
	add_child_autofree(boot)
	var service: SessionService = boot.get_node("Session")
	var main_menu: MainMenu = boot.get_node("View/MainMenu")
	main_menu.join_requested.emit("127.0.0.1", 9)
	assert_eq(service.view().phase, SessionService.PHASE_CONNECTING)
	assert_true(service.cancel(service.view().operation_id).ok)
	await _assert_phase(service, SessionService.PHASE_IDLE, "Boot join cancellation")
	assert_eq(service.view().phase, SessionService.PHASE_IDLE)


## Proves the newly shown status card focuses its applicable primary action once.
func test_status_focuses_initial_action_when_shown() -> void:
	var status: SessionStatus = STATUS_SCENE.instantiate()
	add_child_autofree(status)
	status.present(
		{
			"phase": SessionService.PHASE_STARTING,
			"failure": {},
		}
	)
	await get_tree().process_frame

	var primary_button: Button = status.get_node("%PrimaryButton")
	assert_true(status.visible)
	assert_eq(get_viewport().gui_get_focus_owner(), primary_button)


## Polls one Boot session phase with a load-independent bound and clear failure context.
func _assert_phase(
	service: SessionService,
	expected_phase: StringName,
	context: String,
) -> void:
	var reached_phase: bool = await wait_until(
		func() -> bool: return service.view().phase == expected_phase,
		ASYNC_TIMEOUT_SECONDS,
		context,
	)
	assert_true(
		reached_phase,
		"%s did not reach %s within %.1f seconds; current phase is %s"
		% [context, expected_phase, ASYNC_TIMEOUT_SECONDS, service.view().phase],
	)


## Builds a valid provider-neutral request for the saved Boot service.
func _host_request() -> Dictionary:
	return {
		"provider_id": &"fake",
		"district_id": &"brackett_island",
		"capacity": 4,
		"provider_options": { "port": 24_900 },
	}
