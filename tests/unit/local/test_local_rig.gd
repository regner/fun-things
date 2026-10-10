extends GutTest
## Verifies the saved local camera, binding, and menu-return intent contract.

const LOCAL_RIG_SCENE: PackedScene = preload("res://scenes/local/local_rig.tscn")
const PLAYER_SCENE: PackedScene = preload("res://scenes/entities/player.tscn")
const VEHICLE_SCENE: PackedScene = preload("res://scenes/entities/vehicles/vehicle_latch.tscn")


## Preserves the ratified vertical 47-metre, 42-degree, north-up camera framing.
func test_saved_camera_framing_and_follow_contract() -> void:
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	var rig: LocalRig = LOCAL_RIG_SCENE.instantiate() as LocalRig
	add_child_autofree(actor)
	add_child_autofree(rig)
	await get_tree().process_frame
	assert_true(rig.bind_actor(actor))
	assert_false(rig.get_node("UI/HUD/PlayerCard").visible)
	var camera_anchor: Node3D = rig.get_node("CameraAnchor") as Node3D
	var camera: Camera3D = rig.get_node("CameraAnchor/Camera3D") as Camera3D

	assert_true(is_equal_approx(camera.position.y, 47.0))
	assert_true(is_equal_approx(camera.fov, 42.0))
	assert_true(is_equal_approx(camera.near, 0.1))
	assert_true(is_equal_approx(camera.far, 160.0))
	assert_true(camera.global_basis.z.is_equal_approx(Vector3.UP))

	actor.global_position = Vector3(18.0, 0.25, -31.0)
	await get_tree().physics_frame
	await get_tree().process_frame
	assert_true(camera_anchor.global_position.is_equal_approx(actor.global_position))
	assert_true(camera.global_position.is_equal_approx(actor.global_position + Vector3.UP * 47.0))


## Follows only an accepted vehicle and restores the retained foot actor on exit.
func test_vehicle_binding_retains_hud_actor_and_restores_foot_follow() -> void:
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	var vehicle: VehicleMotion = VEHICLE_SCENE.instantiate() as VehicleMotion
	var rig: LocalRig = LOCAL_RIG_SCENE.instantiate() as LocalRig
	add_child_autofree(actor)
	add_child_autofree(vehicle)
	add_child_autofree(rig)
	await get_tree().process_frame
	assert_true(rig.bind_actor(actor))
	vehicle.global_position = Vector3(30.0, 0.0, -12.0)

	assert_true(rig.bind_vehicle(vehicle))
	assert_same(rig.controlled_actor(), actor)
	assert_same(rig.controlled_vehicle(), vehicle)
	assert_true(
		(rig.get_node("CameraAnchor") as Node3D).global_position.is_equal_approx(
			vehicle.get_node("PresentationAnchor").global_position
		)
	)

	actor.global_position = Vector3(-4.0, 0.0, 9.0)
	assert_true(rig.bind_actor(actor))
	assert_null(rig.controlled_vehicle())
	assert_same(rig.controlled_actor(), actor)
	assert_true(
		(rig.get_node("CameraAnchor") as Node3D).global_position.is_equal_approx(
			actor.global_position
		)
	)


## Emits one leave request for Escape without deciding session or scene teardown.
func test_escape_emits_leave_request() -> void:
	var rig: LocalRig = LOCAL_RIG_SCENE.instantiate() as LocalRig
	add_child_autofree(rig)
	await get_tree().process_frame
	watch_signals(rig)
	var event := InputEventAction.new()
	event.action = &"ui_cancel"
	event.pressed = true

	rig._unhandled_input(event)
	assert_signal_emitted(rig, "leave_requested")


## Proves the noninteractive help overlay does not consume aim or fire GUI dispatch.
func test_controls_overlay_ignores_gameplay_mouse_dispatch() -> void:
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	var rig: LocalRig = LOCAL_RIG_SCENE.instantiate() as LocalRig
	add_child_autofree(actor)
	add_child_autofree(rig)
	await get_tree().process_frame
	assert_true(rig.bind_actor(actor))
	rig.set_physics_process(false)
	var foot_input: DesktopFootInput = rig.get_node("Input") as DesktopFootInput
	var controls: Label = rig.get_node("UI/HUD/ControlsCard/Controls") as Label
	foot_input.set_focused(true)
	assert_eq(controls.mouse_filter, Control.MOUSE_FILTER_IGNORE)
	assert_eq((rig.get_node("UI/HUD") as Control).mouse_filter, Control.MOUSE_FILTER_IGNORE)
	for node: Node in rig.get_node("UI/HUD").find_children("*", "Control", true, false):
		assert_eq((node as Control).mouse_filter, Control.MOUSE_FILTER_IGNORE)
	var pointer_position: Vector2 = controls.global_position + controls.size * 0.5
	var initial_yaw: float = foot_input.sample(1).aim_yaw
	var motion := InputEventMouseMotion.new()
	motion.position = pointer_position
	motion.global_position = pointer_position

	Input.parse_input_event(motion)
	await get_tree().process_frame
	assert_false(is_equal_approx(foot_input.sample(2).aim_yaw, initial_yaw))

	var press := InputEventMouseButton.new()
	press.position = pointer_position
	press.global_position = pointer_position
	press.button_index = MOUSE_BUTTON_LEFT
	press.pressed = true
	Input.parse_input_event(press)
	await get_tree().process_frame
	assert_true(foot_input.sample(3).fire_held)

	press.pressed = false
	Input.parse_input_event(press)
	await get_tree().process_frame
	assert_false(foot_input.sample(4).fire_held)
