extends GutTest
## Verifies Boot creates and tears down the standalone Brackett first playable.

const BOOT_SCENE: PackedScene = preload("res://scenes/boot/boot.tscn")


## Transitions Play to Match at Spawn01 and returns to a clean menu on local leave.
func test_boot_match_boot_teardown() -> void:
	var boot: Boot = BOOT_SCENE.instantiate() as Boot
	add_child_autofree(boot)
	await get_tree().process_frame
	var service: SessionService = boot.get_node("Session") as SessionService
	var menu: MainMenu = boot.get_node("View/MainMenu") as MainMenu

	menu.standalone_requested.emit()
	await get_tree().process_frame
	await get_tree().process_frame
	assert_eq(service.view().phase, SessionService.PHASE_ACTIVE)
	var match: Node3D = boot.get_node_or_null("View/Match") as Node3D
	assert_not_null(match)
	assert_false(menu.visible)
	var actor: ActorMotion = match.get_node("RuntimeEntities/LocalPlayer") as ActorMotion
	var spawn: Marker3D = match.get_node("Anchors/PlayerSpawns/Spawn01") as Marker3D
	var rig: LocalRig = match.get_node("LocalRig") as LocalRig
	assert_eq(rig.controlled_actor(), actor)
	var actor_planar := Vector2(actor.global_position.x, actor.global_position.z)
	var spawn_planar := Vector2(spawn.global_position.x, spawn.global_position.z)
	assert_true(actor_planar.is_equal_approx(spawn_planar))
	assert_true(is_equal_approx(actor.global_rotation.y, spawn.global_rotation.y))
	assert_lte(absf(actor.global_position.y - spawn.global_position.y), 0.05)
	var match_reference: WeakRef = weakref(match)

	rig.leave_requested.emit()
	await get_tree().process_frame
	await get_tree().process_frame
	assert_eq(service.view().phase, SessionService.PHASE_IDLE)
	assert_null(boot.get_node_or_null("View/Match"))
	assert_null(match_reference.get_ref())
	assert_true(menu.visible)
