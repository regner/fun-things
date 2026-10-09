extends GutTest
## Verifies desktop collection, mouse-facing projection, and focus-loss neutralization.


## Collects normalized world-relative WASD plus independent fire and alternate intent.
func test_collects_desktop_command_without_applying_gameplay() -> void:
	var collector: DesktopFootInput = _add_collector()
	collector.set_focused(true)
	collector._unhandled_input(_key(KEY_W, true))
	collector._unhandled_input(_key(KEY_D, true))
	collector._unhandled_input(_mouse(MOUSE_BUTTON_LEFT, true))
	collector._unhandled_input(_mouse(MOUSE_BUTTON_RIGHT, true))

	var command: FootCommand = collector.sample(24)
	assert_true(command.is_valid())
	assert_true(is_equal_approx(command.move.length(), 1.0))
	assert_gt(command.move.x, 0.0)
	assert_lt(command.move.y, 0.0)
	assert_true(command.fire_held)
	assert_true(command.alt_held)
	assert_eq(command.client_tick, 24)
	assert_eq(command.sequence, 1)


## Clears held movement and fire across focus loss and requires a fresh press afterward.
func test_focus_loss_stays_neutral_after_focus_regain() -> void:
	var collector: DesktopFootInput = _add_collector()
	collector.set_focused(true)
	collector._unhandled_input(_key(KEY_W, true))
	collector._unhandled_input(_mouse(MOUSE_BUTTON_LEFT, true))
	assert_lt(collector.sample(1).move.y, 0.0)

	collector.set_focused(false)
	var unfocused: FootCommand = collector.sample(2)
	assert_eq(unfocused.move, Vector2.ZERO)
	assert_false(unfocused.fire_held)

	collector.set_focused(true)
	var restored: FootCommand = collector.sample(3)
	assert_eq(restored.move, Vector2.ZERO)
	assert_false(restored.fire_held)

	collector._unhandled_input(_key(KEY_W, true))
	assert_lt(collector.sample(4).move.y, 0.0)


## Projects the viewport mouse ray onto the controlled actor's horizontal plane.
func test_mouse_right_of_actor_faces_world_positive_x() -> void:
	var collector: DesktopFootInput = _add_collector()
	var actor := ActorMotion.new()
	var camera := Camera3D.new()
	camera.position = Vector3(0.0, 10.0, 0.0)
	camera.rotation.x = -PI * 0.5
	camera.current = true
	add_child_autofree(actor)
	add_child_autofree(camera)
	await get_tree().process_frame
	collector.bind_aim(camera, actor)
	var centre: Vector2 = get_viewport().get_visible_rect().size * 0.5

	var yaw: float = collector.aim_yaw_for_screen(centre + Vector2(100.0, 0.0))
	assert_true(is_equal_approx(yaw, -PI * 0.5))


## Adds a collector to the active test viewport so InputMap actions resolve normally.
func _add_collector() -> DesktopFootInput:
	var collector := DesktopFootInput.new()
	add_child_autofree(collector)
	return collector


## Creates one physical keyboard event resolved through production InputMap actions.
func _key(physical_keycode: Key, pressed: bool) -> InputEventKey:
	var event := InputEventKey.new()
	event.physical_keycode = physical_keycode
	event.pressed = pressed
	return event


## Creates one physical mouse-button event for fire-intent collection.
func _mouse(button: MouseButton, pressed: bool) -> InputEventMouseButton:
	var event := InputEventMouseButton.new()
	event.button_index = button
	event.pressed = pressed
	return event
