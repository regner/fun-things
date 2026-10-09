extends GutTest
## Verifies shared production foot motion, collision, scene composition, and presentation.

const FIXED_DELTA: float = 1.0 / 60.0
const RAMP_ANGLE_DEGREES: float = 28.0
const PLAYER_SCENE: PackedScene = preload("res://scenes/entities/player.tscn")
const MATCH_SCENE: PackedScene = preload("res://scenes/match/match.tscn")


## Keeps cardinal and diagonal travel at one immediate five-metre-per-second speed.
func test_motion_normalizes_speed_and_stops_immediately() -> void:
	var actor: ActorMotion = _add_actor()
	await get_tree().physics_frame

	var cardinal := FootCommand.new(1, 1, Vector2.RIGHT, 0.0, false, false)
	assert_true(actor.step(cardinal, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
	assert_true(is_equal_approx(_planar_speed(actor), 5.0))

	var diagonal := FootCommand.new(
		2, 2, Vector2(0.70710677, -0.70710677), 0.0, false, false
	)
	assert_true(actor.step(diagonal, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
	assert_true(is_equal_approx(_planar_speed(actor), 5.0))

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
	assert_true(is_zero_approx(_planar_speed(actor)))
	assert_lt(actor.velocity.y, 0.0)


## Rejects invalid commands without retaining movement from the previous frame.
func test_invalid_command_is_rejected_and_neutralized() -> void:
	var actor: ActorMotion = _add_actor()
	await get_tree().physics_frame
	var valid := FootCommand.new(1, 1, Vector2.RIGHT, 0.0, false, false)
	var invalid := FootCommand.new(2, 2, Vector2(2.0, 0.0), 0.0, false, false)

	assert_true(actor.step(valid, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
	assert_false(actor.step(invalid, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
	assert_eq(actor.velocity, Vector3.ZERO)


## Rejects a mismatched delta and moves only for the active fixed physics step.
func test_delta_must_match_active_fixed_physics_step() -> void:
	var actor: ActorMotion = _add_actor()
	await get_tree().physics_frame
	var command := FootCommand.new(1, 1, Vector2.RIGHT, 0.0, false, false)
	var starting_position := actor.global_position
	var active_fixed_delta := 1.0 / float(Engine.physics_ticks_per_second)

	assert_true(actor.step(command, active_fixed_delta, ActorMotion.StepMode.AUTHORITY))
	assert_true(is_equal_approx(_planar_speed(actor), 5.0))
	assert_gt(actor.global_position.x, starting_position.x)
	var moved_position := actor.global_position

	assert_false(actor.step(command, active_fixed_delta * 0.5, ActorMotion.StepMode.AUTHORITY))
	assert_eq(actor.velocity, Vector3.ZERO)
	assert_eq(actor.global_position, moved_position)


## Uses CharacterBody collision to stop the production capsule at a static world wall.
func test_character_body_collides_with_static_world() -> void:
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	add_child_autofree(actor)
	_add_floor(Vector3.ZERO, Vector3(8.0, 0.2, 8.0))
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


## Walks the production capsule up and down a collision ramp below the 45-degree limit.
func test_actor_follows_twenty_eight_degree_ramp_both_directions() -> void:
	_add_ramp(RAMP_ANGLE_DEGREES, 8.0, 4.0)
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	actor.position = Vector3(-3.5, 0.8, 0.0)
	add_child_autofree(actor)
	await _step_actor(actor, Vector2.ZERO, 20)
	var low_position: Vector3 = actor.position

	await _step_actor(actor, Vector2.RIGHT, 100)
	var high_position: Vector3 = actor.position
	assert_gt(high_position.x, low_position.x + 5.0)
	assert_gt(high_position.y, low_position.y + 2.5)
	assert_true(actor.is_on_floor())

	await _step_actor(actor, Vector2.LEFT, 85)
	assert_lt(actor.position.x, high_position.x - 4.5)
	assert_lt(actor.position.y, high_position.y - 2.2)
	assert_true(actor.is_on_floor())


## Crosses the complete saved harbour bridge through the production ActorMotion API.
func test_actor_crosses_saved_harbour_bridge() -> void:
	var match_root: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match_root)
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	actor.position = Vector3(-325.0, 0.05, 235.0)
	match_root.get_node("RuntimeEntities").add_child(actor)
	await _step_actor(actor, Vector2.ZERO, 8)
	var minimum_y: float = actor.position.y
	var unsupported_ticks: int = 0
	var reached_end: bool = false

	for tick: int in range(1, 1501):
		await get_tree().physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick, tick, Vector2.RIGHT, -PI * 0.5, false, false
		)
		assert_true(actor.step(command, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
		minimum_y = minf(minimum_y, actor.position.y)
		unsupported_ticks += int(not actor.is_on_floor())
		if actor.position.x >= -226.0:
			reached_end = true
			break

	assert_true(reached_end)
	assert_gt(minimum_y, -0.1)
	assert_lt(unsupported_ticks, 5)
	assert_true(actor.is_on_floor())


## Falls from an upper platform and lands on a surface one metre below it.
func test_actor_falls_off_one_metre_ledge() -> void:
	_add_floor(Vector3.ZERO, Vector3(3.0, 0.2, 4.0))
	_add_floor(Vector3(5.0, -1.0, 0.0), Vector3(7.0, 0.2, 4.0))
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	actor.position = Vector3.ZERO
	add_child_autofree(actor)
	await _step_actor(actor, Vector2.ZERO, 5)
	var left_floor: bool = false

	for tick: int in range(1, 91):
		await get_tree().physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick, tick, Vector2.RIGHT, -PI * 0.5, false, false
		)
		assert_true(actor.step(command, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
		left_floor = left_floor or not actor.is_on_floor()

	assert_true(left_floor)
	assert_gt(actor.position.x, 5.0)
	assert_almost_eq(actor.position.y, -1.0, 0.08)
	assert_true(actor.is_on_floor())


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
	assert_eq(actor.motion_mode, CharacterBody3D.MOTION_MODE_GROUNDED)
	assert_true(is_equal_approx(actor.floor_snap_length, 0.25))
	assert_true(is_equal_approx(actor.floor_max_angle, deg_to_rad(45.0)))


## Drives the delivered Courier locomotion clip from solved motion state only.
func test_motion_state_drives_courier_locomotion() -> void:
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	add_child_autofree(actor)
	await get_tree().process_frame
	var command := FootCommand.new(1, 1, Vector2.RIGHT, 0.0, false, false)

	assert_true(actor.step(command, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
	var animation: AnimationPlayer = actor.get_node(
		"PresentationAnchor/Visuals/Model/LowerBodyPlayer"
	) as AnimationPlayer
	assert_eq(animation.current_animation, &"run_right")


## Returns horizontal speed without conflating the gravity component.
func _planar_speed(actor: ActorMotion) -> float:
	return Vector2(actor.velocity.x, actor.velocity.z).length()


## Advances production movement against physics collision for a bounded number of ticks.
func _step_actor(actor: ActorMotion, move: Vector2, ticks: int) -> void:
	for tick: int in range(1, ticks + 1):
		await get_tree().physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick, tick, move, 0.0, false, false
		)
		assert_true(actor.step(command, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))


## Adds a bare ActorMotion for pure shared-rule outcomes without presentation dependencies.
func _add_actor() -> ActorMotion:
	var actor := ActorMotion.new()
	actor.collision_layer = 2
	actor.collision_mask = 1
	add_child_autofree(actor)
	return actor


## Adds a box whose upper face is at the supplied surface position.
func _add_floor(surface_position: Vector3, size: Vector3) -> StaticBody3D:
	return _add_wall(surface_position - Vector3.UP * size.y * 0.5, size)


## Adds a wedge with a walkable planar top at the requested grade.
func _add_ramp(angle_degrees: float, length: float, width: float) -> StaticBody3D:
	var half_length: float = length * 0.5
	var half_width: float = width * 0.5
	var rise: float = tan(deg_to_rad(angle_degrees)) * length
	var points := PackedVector3Array(
		[
			Vector3(-half_length, 0.0, -half_width),
			Vector3(-half_length, 0.0, half_width),
			Vector3(half_length, rise, -half_width),
			Vector3(half_length, rise, half_width),
			Vector3(-half_length, -0.5, -half_width),
			Vector3(-half_length, -0.5, half_width),
			Vector3(half_length, -0.5, -half_width),
			Vector3(half_length, -0.5, half_width),
		]
	)
	var ramp := StaticBody3D.new()
	ramp.collision_layer = 1
	ramp.collision_mask = 0
	var collision := CollisionShape3D.new()
	var shape := ConvexPolygonShape3D.new()
	shape.points = points
	collision.shape = shape
	ramp.add_child(collision)
	add_child_autofree(ramp)
	return ramp


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
