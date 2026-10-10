extends GutTest
## Verifies bounded local car replay, correction smoothing, and lifecycle clearing.

const VEHICLE_SCENE: PackedScene = preload(
	"res://scenes/entities/vehicles/vehicle_latch.tscn"
)
const FIXED_DELTA: float = 1.0 / 60.0


## Restores authority then replays each unacknowledged command through VehicleMotion.
func test_reconciliation_replays_unacknowledged_drive_commands() -> void:
	var predicted: VehicleMotion = _add_vehicle()
	var authority: VehicleMotion = _add_vehicle()
	await get_tree().physics_frame
	var prediction := VehiclePrediction.new()
	assert_true(prediction.bind_vehicle(predicted))
	prediction.update_context(5, 1, 1, 1, 1)

	for sequence: int in range(1, 4):
		# Each frame intentionally owns immutable-by-convention replay input.
		# gdstyle:ignore=quality/allocation-in-loop
		var command := DriveCommand.new(sequence, sequence, 1.0, 0.25, 0.0, false)
		assert_true(prediction.predict(command, FIXED_DELTA))
		if sequence == 1:
			assert_true(
				authority.step(command, FIXED_DELTA, VehicleMotion.StepMode.AUTHORITY)
			)
	var before_position: Vector3 = predicted.global_position
	var result: Dictionary = prediction.reconcile(authority.motion_state(), 1)

	assert_true(result.ok)
	assert_eq(result.replayed, 2)
	assert_eq(prediction.diagnostics().history_size, 2)
	assert_almost_eq(predicted.global_position.z, before_position.z, 0.001)
	assert_eq(prediction.diagnostics().acknowledgement, 1)


## Keeps bounded corrections visual-only while the body adopts authority immediately.
func test_bounded_correction_smooths_presentation_separately() -> void:
	var vehicle: VehicleMotion = _add_vehicle()
	await get_tree().physics_frame
	var prediction := VehiclePrediction.new()
	prediction.bind_vehicle(vehicle)
	prediction.update_context(6, 1, 1, 1, 1)
	prediction.predict(DriveCommand.new(1, 1, 1.0, 0.0, 0.0, false), FIXED_DELTA)
	var display_before: Vector3 = (
		vehicle.get_node("PresentationAnchor") as Node3D
	).global_position
	var authority: Dictionary = vehicle.motion_state()
	authority.position.x -= 0.2

	var result: Dictionary = prediction.reconcile(authority, 1)
	var presentation: Node3D = vehicle.get_node("PresentationAnchor") as Node3D
	assert_true(result.ok)
	assert_almost_eq(result.correction_metres, 0.2, 0.001)
	assert_almost_eq(presentation.global_position.x, display_before.x, 0.001)
	assert_almost_eq(vehicle.global_position.x, display_before.x - 0.2, 0.001)
	for _tick: int in range(7):
		prediction.tick_visual(FIXED_DELTA)
	assert_lt(presentation.global_position.distance_to(vehicle.global_position), 0.07)


## Snaps to authority rather than replaying an overflowed history prefix.
func test_history_overflow_is_bounded_and_reports_snap() -> void:
	var vehicle: VehicleMotion = _add_vehicle()
	await get_tree().physics_frame
	var prediction := VehiclePrediction.new()
	prediction.bind_vehicle(vehicle)
	prediction.update_context(7, 1, 1, 1, 1)
	for sequence: int in range(1, VehiclePrediction.HISTORY_CAPACITY + 2):
		# Overflow coverage deliberately allocates one retained command per frame.
		# gdstyle:ignore=quality/allocation-in-loop
		var command := DriveCommand.new(sequence, sequence, 1.0, 0.0, 0.0, false)
		assert_true(
			prediction.predict(
				command,
				FIXED_DELTA,
			)
		)
	var authority: Dictionary = vehicle.motion_state()
	authority.position = Vector3.ZERO
	var result: Dictionary = prediction.reconcile(authority, 0)
	assert_true(result.ok)
	assert_true(result.history_exhausted)
	assert_eq(prediction.diagnostics().history_size, 0)
	assert_eq(vehicle.global_position, Vector3.ZERO)


## Instantiates an authored vehicle so correction uses the production visual anchor.
func _add_vehicle() -> VehicleMotion:
	var vehicle: VehicleMotion = VEHICLE_SCENE.instantiate() as VehicleMotion
	vehicle.collision_layer = 0
	vehicle.collision_mask = 0
	add_child_autofree(vehicle)
	return vehicle
