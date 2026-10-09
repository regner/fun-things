extends GutTest
## Verifies saved Boot and status scenes honor session visibility and focus contracts.

const BOOT_SCENE: PackedScene = preload("res://scenes/boot/boot.tscn")
const STATUS_SCENE: PackedScene = preload("res://scenes/ui/session_status.tscn")
const WAIT_SECONDS: float = 0.08


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
	await get_tree().create_timer(WAIT_SECONDS).timeout

	assert_eq(service.view().phase, SessionService.PHASE_IDLE)
	assert_true(service.view().failure.is_empty())
	assert_true(main_menu.visible)
	assert_false(status.visible)


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


## Builds a valid provider-neutral request for the saved Boot service.
func _host_request() -> Dictionary:
	return {
		"provider_id": &"fake",
		"district_id": &"brackett_island",
		"capacity": 4,
		"provider_options": { "port": 24_900 },
	}
