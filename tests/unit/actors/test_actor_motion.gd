extends GutTest
## Verifies shared production foot motion, collision, scene composition, and presentation.

const FIXED_DELTA: float = 1.0 / 60.0
const PLAYER_SCENE: PackedScene = preload("res://scenes/entities/player.tscn")


## Keeps cardinal and diagonal travel at one immediate five-metre-per-second speed.
func test_motion_normalizes_speed_and_stops_immediately() -> void:
	var actor: ActorMotion = _add_actor()
	await get_tree().physics_frame

	var cardinal := FootCommand.new(1, 1, Vector2.RIGHT, 0.0, false, false)
	assert_true(actor.step(cardinal, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
	assert_true(is_equal_approx(actor.velocity.length(), 5.0))

	var diagonal := FootCommand.new(
		2, 2, Vector2(0.70710677, -0.70710677), 0.0, false, false
	)
	assert_true(actor.step(diagonal, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
	assert_true(is_equal_approx(actor.velocity.length(), 5.0))

	actor.neutralize()
	assert_eq(actor.velocity, Vector3.ZERO)


## Produces equivalent state for standalone, host authority, and permitted replay.
func test_standalone_authority_and_replay_are_equivalent() -> void:
	var standalone: ActorMotion = _add_actor()
	var authority: ActorMotion = _add_actor()
	var replay: ActorMotion = _add_actor()
	await get_tree().physics_frame
	var commands: Array[FootCommand] = [
		FootCommand.new(1, 10, Vector2(0.0, -1.0), 0.25, false, false),
		FootCommand.new(2, 11, Vector2(0.6, 0.8), -1.0, true, false),
		FootCommand.new(3, 12, Vector2.ZERO, PI, false, true),
	]

	for command: FootCommand in commands:
		assert_true(standalone.step(command, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
		assert_true(authority.step(command, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
		assert_true(replay.step(command, FIXED_DELTA, ActorMotion.StepMode.REPLAY))

	assert_eq(standalone.motion_state(), authority.motion_state())
	assert_eq(authority.motion_state(), replay.motion_state())


## Snaps facing to canonical command yaw even while the actor is stationary.
func test_aim_yaw_is_independent_of_movement() -> void:
	var actor: ActorMotion = _add_actor()
	await get_tree().physics_frame
	var command := FootCommand.new(1, 1, Vector2.ZERO, -1.35, false, false)

	assert_true(actor.step(command, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
	assert_true(is_equal_approx(actor.rotation.y, -1.35))
	assert_eq(actor.velocity, Vector3.ZERO)


## Rejects invalid commands without retaining movement from the previous frame.
func test_invalid_command_is_rejected_and_neutralized() -> void:
	var actor: ActorMotion = _add_actor()
	await get_tree().physics_frame
	var valid := FootCommand.new(1, 1, Vector2.RIGHT, 0.0, false, false)
	var invalid := FootCommand.new(2, 2, Vector2(2.0, 0.0), 0.0, false, false)

	assert_true(actor.step(valid, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
	assert_false(actor.step(invalid, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
	assert_eq(actor.velocity, Vector3.ZERO)


## Uses CharacterBody collision to stop the production capsule at a static world wall.
func test_character_body_collides_with_static_world() -> void:
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	add_child_autofree(actor)
	var wall: StaticBody3D = _add_wall(Vector3(2.0, 0.9, 0.0), Vector3(0.2, 1.8, 4.0))
	assert_not_null(wall)
	await get_tree().physics_frame
	var command := FootCommand.new(1, 1, Vector2.RIGHT, -PI * 0.5, false, false)

	for _tick: int in range(45):
		assert_true(actor.step(command, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
		# Actual CharacterBody collision requires one bounded solver frame per step.
		await get_tree().physics_frame  # gdstyle:ignore=quality/await-in-loop

	assert_gt(actor.global_position.x, 1.0)
	assert_lt(actor.global_position.x, 1.7)


## Preserves the authored player paths, capsule dimensions, and Courier presentation link.
func test_player_scene_has_required_authored_composition() -> void:
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	add_child_autofree(actor)
	await get_tree().process_frame

	var collision: CollisionShape3D = actor.get_node("Collision") as CollisionShape3D
	var capsule: CapsuleShape3D = collision.shape as CapsuleShape3D
	assert_not_null(actor.get_node_or_null("PresentationAnchor/Visuals/Model"))
	assert_not_null(capsule)
	assert_true(is_equal_approx(capsule.radius, 0.35))
	assert_true(is_equal_approx(capsule.height, 1.8))


## Drives the delivered Courier locomotion clip from solved motion state only.
func test_motion_state_drives_courier_locomotion() -> void:
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	add_child_autofree(actor)
	await get_tree().process_frame
	var command := FootCommand.new(1, 1, Vector2.RIGHT, 0.0, false, false)

	assert_true(actor.step(command, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
	var animation: AnimationPlayer = actor.get_node(
		"PresentationAnchor/Visuals/Model/AnimationPlayer"
	) as AnimationPlayer
	assert_eq(animation.current_animation, &"player/run_right")


## Adds a bare ActorMotion for pure shared-rule outcomes without presentation dependencies.
func _add_actor() -> ActorMotion:
	var actor := ActorMotion.new()
	actor.collision_layer = 2
	actor.collision_mask = 1
	actor.motion_mode = CharacterBody3D.MOTION_MODE_FLOATING
	add_child_autofree(actor)
	return actor


## Adds synthetic World-layer collision used only by the component test.
func _add_wall(position: Vector3, size: Vector3) -> StaticBody3D:
	var wall := StaticBody3D.new()
	wall.collision_layer = 1
	wall.collision_mask = 0
	wall.position = position
	var collision := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = size
	collision.shape = shape
	wall.add_child(collision)
	add_child_autofree(wall)
	return wall
