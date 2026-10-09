extends GutTest
## Verifies the production vehicle rule, body envelopes, collision, and wheel presentation.

const FIXED_DELTA: float = 1.0 / 60.0
const DEFAULT_TUNING: VehicleTuning = preload(
	"res://resources/vehicles/default_vehicle_tuning.tres"
)
const VEHICLE_SCENES: Array[PackedScene] = [
	preload("res://scenes/entities/vehicles/vehicle_latch.tscn"),
	preload("res://scenes/entities/vehicles/vehicle_crate.tscn"),
	preload("res://scenes/entities/vehicles/vehicle_sable.tscn"),
]


## Keeps the resource defaults equal to the owner-ratified decision-30 values.
func test_tuning_defaults_match_decision_30() -> void:
	var tuning := VehicleTuning.new()
	assert_eq(tuning.acceleration_mps2, 12.0)
	assert_eq(tuning.brake_mps2, 12.0)
	assert_eq(tuning.coast_mps2, 9.25)
	assert_eq(tuning.max_forward_mps, 24.0)
	assert_eq(tuning.max_reverse_mps, 6.0)
	assert_eq(tuning.grip_per_second, 8.0)
	assert_eq(tuning.handbrake_side_grip_per_second, 3.0)
	assert_eq(tuning.turn_rate_rad_per_second, 1.5)
	assert_eq(tuning.full_steer_speed_mps, 4.0)
	assert_eq(tuning.handbrake_brake_mps2, 10.0)
	assert_true(tuning.is_valid())


## Produces identical states for standalone, host, replay, and AI callers.
func test_command_stream_is_equivalent_for_every_caller() -> void:
	var standalone: VehicleMotion = _add_motion()
	var host: VehicleMotion = _add_motion()
	var replay: VehicleMotion = _add_motion()
	var ai: VehicleMotion = _add_motion()
	await get_tree().physics_frame

	var commands: Array[DriveCommand] = [
		DriveCommand.new(1, 1, 1.0, 0.0, 0.0, false),
		DriveCommand.new(2, 2, 1.0, 0.65, 0.0, false),
		DriveCommand.new(3, 3, 0.0, 0.65, 0.0, true),
	]
	for command: DriveCommand in commands:
		for _tick: int in range(30):
			assert_true(
				standalone.step(command, FIXED_DELTA, VehicleMotion.StepMode.AUTHORITY)
			)
			assert_true(host.step(command, FIXED_DELTA, VehicleMotion.StepMode.AUTHORITY))
			assert_true(replay.step(command, FIXED_DELTA, VehicleMotion.StepMode.REPLAY))
			assert_true(ai.step(command, FIXED_DELTA, VehicleMotion.StepMode.AUTHORITY))

	assert_eq(standalone.motion_state(), host.motion_state())
	assert_eq(host.motion_state(), replay.motion_state())
	assert_eq(replay.motion_state(), ai.motion_state())


## Brakes from ten metres per second and accelerates backward only after stopping.
func test_service_brake_and_reverse() -> void:
	var car: VehicleMotion = _add_motion()
	await get_tree().physics_frame
	car.velocity = Vector3(0.0, 0.0, -10.0)

	var brake := DriveCommand.new(1, 1, 0.0, 0.0, 1.0, false)
	for _tick: int in range(60):
		assert_true(car.step(brake, FIXED_DELTA, VehicleMotion.StepMode.AUTHORITY))
	assert_lt(car.velocity.length(), 0.2)

	var reverse := DriveCommand.new(2, 2, -1.0, 0.0, 0.0, false)
	for _tick: int in range(60):
		assert_true(car.step(reverse, FIXED_DELTA, VehicleMotion.StepMode.AUTHORITY))
	assert_gt(car.velocity.z, 5.0)
	assert_lte(car.velocity.length(), DEFAULT_TUNING.max_reverse_mps + 0.01)


## Treats any fractional brake as full service braking, including with the handbrake.
func test_fractional_service_brake_uses_full_threshold() -> void:
	var service_car: VehicleMotion = _add_motion()
	var handbrake_car: VehicleMotion = _add_motion()
	await get_tree().physics_frame
	service_car.velocity = Vector3(0.0, 0.0, -15.0)
	handbrake_car.velocity = Vector3(9.0, 0.0, -12.0)
	var service_command := DriveCommand.new(1, 1, 0.0, 0.0, 0.5, false)
	var handbrake_command := DriveCommand.new(1, 1, 0.0, 0.0, 0.5, true)

	for _tick: int in range(60):
		assert_true(
			service_car.step(service_command, FIXED_DELTA, VehicleMotion.StepMode.AUTHORITY)
		)
		assert_true(
			handbrake_car.step(
				handbrake_command, FIXED_DELTA, VehicleMotion.StepMode.AUTHORITY
			)
		)

	assert_almost_eq(service_car.velocity.length(), 3.0, 0.05)
	assert_almost_eq(handbrake_car.velocity.length(), 3.0, 0.05)


## Applies decision-29 braking and planar-speed steering to a sideways handbrake slide.
func test_handbrake_brakes_full_planar_velocity_and_keeps_yaw_authority() -> void:
	var car: VehicleMotion = _add_motion()
	await get_tree().physics_frame
	car.velocity = Vector3(15.0, 0.0, 0.0)

	var command := DriveCommand.new(1, 1, 0.0, 1.0, 0.0, true)
	for _tick: int in range(60):
		assert_true(car.step(command, FIXED_DELTA, VehicleMotion.StepMode.AUTHORITY))

	assert_almost_eq(car.velocity.length(), 5.0, 0.05)
	assert_almost_eq(float(car.motion_state().yaw_rate), -1.5, 0.001)


## Retains the accepted relative slide margin under the decision-30 tuning.
func test_handbrake_retains_relative_lateral_slide() -> void:
	var ordinary: VehicleMotion = _add_motion()
	var handbrake: VehicleMotion = _add_motion()
	await get_tree().physics_frame
	# Decision-30 coast/grip needs a pronounced entry slide for the relative S04 criterion.
	ordinary.velocity = Vector3(15.0, 0.0, -7.0)
	handbrake.velocity = ordinary.velocity

	var ordinary_command := DriveCommand.neutral(1, 1)
	var slide_command := DriveCommand.new(1, 1, 0.0, 0.0, 0.0, true)
	for _tick: int in range(30):
		assert_true(
			ordinary.step(ordinary_command, FIXED_DELTA, VehicleMotion.StepMode.AUTHORITY)
		)
		assert_true(
			handbrake.step(slide_command, FIXED_DELTA, VehicleMotion.StepMode.AUTHORITY)
		)

	var ordinary_lateral: float = absf(ordinary.velocity.x)
	var slide_lateral: float = absf(handbrake.velocity.x)
	var ordinary_share: float = ordinary_lateral / ordinary.velocity.length()
	var slide_share: float = slide_lateral / handbrake.velocity.length()
	assert_gte(slide_lateral, ordinary_lateral * 4.0)
	assert_gte(slide_share, ordinary_share + 0.25)


## Stops at static World collision and can reverse away without penetrating the wall.
func test_wall_contact_and_reverse_recovery() -> void:
	var car: VehicleMotion = _add_motion()
	car.configure_simulation(true)
	var wall: StaticBody3D = _add_wall(Vector3(0.0, 0.75, -4.0), Vector3(8.0, 1.5, 0.2))
	assert_not_null(wall)
	await get_tree().physics_frame

	var forward := DriveCommand.new(1, 1, 1.0, 0.0, 0.0, false)
	for _tick: int in range(120):
		assert_true(car.step(forward, FIXED_DELTA, VehicleMotion.StepMode.AUTHORITY))
		await get_tree().physics_frame  # gdstyle:ignore=quality/await-in-loop
	assert_gt(car.global_position.z, -3.1)
	var contact_z: float = car.global_position.z

	var reverse := DriveCommand.new(2, 2, -1.0, 0.0, 0.0, false)
	for _tick: int in range(60):
		assert_true(car.step(reverse, FIXED_DELTA, VehicleMotion.StepMode.AUTHORITY))
		await get_tree().physics_frame  # gdstyle:ignore=quality/await-in-loop
	assert_gt(car.global_position.z, contact_z + 1.0)


## Rejects malformed commands and mismatched deltas without retaining motion.
func test_invalid_step_neutralizes_motion() -> void:
	var car: VehicleMotion = _add_motion()
	await get_tree().physics_frame
	car.velocity = Vector3(0.0, 0.0, -4.0)
	var invalid := DriveCommand.new(0, 1, 1.0, 0.0, 0.0, false)
	assert_false(car.step(invalid, FIXED_DELTA, VehicleMotion.StepMode.AUTHORITY))
	assert_eq(car.velocity, Vector3.ZERO)

	var valid := DriveCommand.new(1, 1, 1.0, 0.0, 0.0, false)
	assert_false(car.step(valid, FIXED_DELTA * 0.5, VehicleMotion.StepMode.AUTHORITY))
	assert_eq(car.velocity, Vector3.ZERO)


## Preserves three distinct body envelopes and source-linked imported models.
func test_vehicle_scenes_have_envelopes_models_sockets_and_wheel_rigs() -> void:
	var expected_sizes: Array[Vector3] = [
		Vector3(1.8, 1.35, 3.25),
		Vector3(1.82, 1.45, 3.5),
		Vector3(1.84, 1.3, 4.1),
	]
	for index: int in VEHICLE_SCENES.size():
		var car: VehicleMotion = VEHICLE_SCENES[index].instantiate() as VehicleMotion
		add_child_autofree(car)
		await get_tree().process_frame  # gdstyle:ignore=quality/await-in-loop
		var collision: CollisionShape3D = car.get_node("Collision") as CollisionShape3D
		var shape: BoxShape3D = collision.shape as BoxShape3D
		assert_eq(shape.size, expected_sizes[index])
		assert_not_null(car.get_node_or_null("PresentationAnchor/Visuals/Model/Visuals/Model"))
		assert_not_null(car.get_node_or_null("Sockets/DriverSeat"))
		var presentation: VehiclePresentation = car.get_node(
			"PresentationAnchor"
		) as VehiclePresentation
		assert_true(presentation.has_complete_wheel_rig())


## Points wheels with vehicle yaw and rolls them with forward travel direction.
func test_motion_state_drives_wheels_in_vehicle_travel_direction() -> void:
	var car: VehicleMotion = VEHICLE_SCENES[0].instantiate() as VehicleMotion
	add_child_autofree(car)
	await get_tree().process_frame
	var command := DriveCommand.new(1, 1, 1.0, 0.75, 0.0, false)
	assert_true(car.step(command, FIXED_DELTA, VehicleMotion.StepMode.AUTHORITY))
	var steer: Node3D = car.find_child("SteerFrontLeft", true, false) as Node3D
	var spin: Node3D = car.find_child("SpinFrontLeft", true, false) as Node3D
	var state: Dictionary = car.motion_state()
	assert_lt(float(state.yaw_rate), 0.0)
	assert_gt(steer.rotation.y * float(state.yaw_rate), 0.0)
	assert_gt(float(state.forward_speed_mps), 0.0)
	assert_lt(spin.rotation.x * float(state.forward_speed_mps), 0.0)


## Adds a source-independent body for shared-rule outcomes.
func _add_motion() -> VehicleMotion:
	var car := VehicleMotion.new()
	car.tuning = DEFAULT_TUNING.duplicate(true) as VehicleTuning
	car.collision_layer = 0
	car.collision_mask = 0
	car.motion_mode = CharacterBody3D.MOTION_MODE_FLOATING
	var collision := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = Vector3(1.8, 1.35, 3.25)
	collision.position.y = 0.675
	collision.shape = shape
	car.add_child(collision)
	add_child_autofree(car)
	return car


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
