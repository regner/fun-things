extends GutTest
## Verifies the saved local camera, binding, and menu-return intent contract.

const LOCAL_RIG_SCENE: PackedScene = preload("res://scenes/local/local_rig.tscn")
const PLAYER_SCENE: PackedScene = preload("res://scenes/entities/player.tscn")


## Preserves the ratified vertical 47-metre, 42-degree, north-up camera framing.
func test_saved_camera_framing_and_follow_contract() -> void:
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	var rig: LocalRig = LOCAL_RIG_SCENE.instantiate() as LocalRig
	add_child_autofree(actor)
	add_child_autofree(rig)
	await get_tree().process_frame
	assert_true(rig.bind_actor(actor))
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
