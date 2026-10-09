extends GutTest
## Verifies the saved Brackett Match identity, anchors, and representative traversal envelopes.

const MATCH_SCENE: PackedScene = preload("res://scenes/match/match.tscn")
const PROBE_SCENE: PackedScene = preload(
	"res://tests/unit/world/fixtures/traversal_probes.tscn"
)
const CITY_PATH: String = "res://scenes/world/brackett_greybox/city.tscn"
const FOOT_SPEED_MPS: float = 5.0
const CAR_SPEED_MPS: float = 24.0
const ROUTE_TOLERANCE_M: float = 0.6
const MAX_ROUTE_SECONDS: float = 30.0
const PHYSICS_DELTA: float = 1.0 / 60.0


## Proves Match uses the saved city, its source fingerprint, and provisional saved anchors.
func test_match_publishes_saved_world_identity_and_anchors() -> void:
	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match)
	var city_data: CityData = match.get_node("CityData") as CityData
	var world: Node3D = match.get_node("World") as Node3D

	assert_eq(world.scene_file_path, CITY_PATH)
	assert_false(world.scene_file_path.ends_with("preview.tscn"))
	assert_eq(city_data.content_signature, FileAccess.get_sha256(CITY_PATH))
	var composition: Dictionary = city_data.validate_composition()
	assert_true(composition.ok)
	assert_eq(composition.anchor_count, 7)

	var players: Array[Dictionary] = city_data.anchor_descriptors(
		WorldAnchor.KIND_PLAYER_SPAWN
	)
	var cars: Array[Dictionary] = city_data.anchor_descriptors(WorldAnchor.KIND_PARKED_CAR)
	assert_eq(players.size(), 4)
	assert_eq(cars.size(), 3)
	for descriptor: Dictionary in players + cars:
		assert_true(descriptor.provisional_owner_answer)
		assert_true(String(descriptor.world_id).begins_with("brackett/district_06/"))

	var identity: Dictionary = city_data.admission_identity()
	assert_true(city_data.validate_admission(identity).ok)
	var mismatched: Dictionary = identity.duplicate(true)
	mismatched.content_id = "other-build"
	var rejected: Dictionary = city_data.validate_admission(mismatched)
	assert_false(rejected.ok)
	assert_eq(rejected.failure.code, CityData.FAILURE_CONTENT_INVALID)
	assert_eq(city_data.admission_identity(), identity, "rejection does not mutate identity")


## Proves local stale content cannot advertise or admit a matching stale peer identity.
func test_stale_saved_world_signature_is_rejected() -> void:
	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match)
	var city_data: CityData = match.get_node("CityData") as CityData
	city_data.content_signature = "0".repeat(64)

	var stale_composition: Dictionary = city_data.validate_composition()
	assert_false(stale_composition.ok)
	assert_eq(stale_composition.failure.code, CityData.FAILURE_CONTENT_INVALID)
	var stale_admission: Dictionary = city_data.validate_admission(
		city_data.admission_identity()
	)
	assert_false(stale_admission.ok)


## Moves S02 and S04-class probe bodies across sector seams and the saved harbour bridge.
func test_saved_ground_supports_actor_and_car_traversal() -> void:
	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match)
	var probes: Node3D = PROBE_SCENE.instantiate() as Node3D
	add_child_autofree(probes)
	await _wait_for_physics(3)
	var foot: CharacterBody3D = probes.get_node("Foot") as CharacterBody3D
	var car: CharacterBody3D = probes.get_node("Car") as CharacterBody3D

	await _assert_pair_route(
		foot,
		car,
		_route(
			Vector3(0, 0.95, -110),
			Vector3(20, 0.95, -110),
			Vector3(0, 0.80, -110),
			Vector3(20, 0.80, -110),
		),
		"east-west ground-sector seam",
	)
	await _assert_pair_route(
		foot,
		car,
		_route(
			Vector3(20, 0.95, -110),
			Vector3(20, 0.95, -90),
			Vector3(20, 0.80, -110),
			Vector3(20, 0.80, -90),
		),
		"north-south ground-sector seam",
	)
	await _assert_pair_route(
		foot,
		car,
		_route(
			Vector3(-325, 0.95, 235),
			Vector3(-225, 0.95, 235),
			Vector3(-325, 0.80, 235),
			Vector3(-225, 0.80, 235),
		),
		"harbour bridge",
	)


## Proves both representative envelopes slide past an authored building edge and corner.
func test_actor_and_car_slide_along_building_edge_without_snagging() -> void:
	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match)
	var probes: Node3D = PROBE_SCENE.instantiate() as Node3D
	add_child_autofree(probes)
	await _wait_for_physics(3)
	var foot: CharacterBody3D = probes.get_node("Foot") as CharacterBody3D
	var car: CharacterBody3D = probes.get_node("Car") as CharacterBody3D

	var result: Dictionary = await _drive_pair(
		foot,
		car,
		_route(
			Vector3(-118, 0.95, 100),
			Vector3(-115.5, 0.95, 130),
			Vector3(-119, 0.80, 100),
			Vector3(-116.0, 0.80, 130),
		),
	)
	assert_true(result.foot_reached, "foot clears the building corner")
	assert_true(result.car_reached, "car clears the building corner")
	assert_true(result.foot_wall_contact, "foot route exercises a building edge")
	assert_true(result.car_wall_contact, "car route exercises a building edge")


## Runs one route for both probe classes and asserts grounded progress to each endpoint.
func _assert_pair_route(
	foot: CharacterBody3D,
	car: CharacterBody3D,
	route: Dictionary,
	label: String,
) -> void:
	var result: Dictionary = await _drive_pair(foot, car, route)
	assert_true(result.foot_reached, "%s supports the foot capsule" % label)
	assert_true(result.car_reached, "%s supports the car envelope" % label)
	assert_gt(float(result.foot_min_y), 0.5, "%s does not drop the foot probe" % label)
	assert_gt(float(result.car_min_y), 0.3, "%s does not drop the car probe" % label)


## Advances actual CharacterBody collision for a bounded pair of saved-envelope probes.
func _drive_pair(
	foot: CharacterBody3D,
	car: CharacterBody3D,
	route: Dictionary,
) -> Dictionary:
	foot.position = route.foot_start
	car.position = route.car_start
	foot.velocity = Vector3.ZERO
	car.velocity = Vector3.ZERO
	await _wait_for_physics(3)
	var foot_reached: bool = false
	var car_reached: bool = false
	var foot_wall_contact: bool = false
	var car_wall_contact: bool = false
	var foot_min_y: float = foot.position.y
	var car_min_y: float = car.position.y
	var steps: int = int(MAX_ROUTE_SECONDS / PHYSICS_DELTA)
	for _step: int in range(steps):
		await get_tree().physics_frame  # gdstyle:ignore=quality/await-in-loop
		if not foot_reached:
			foot_reached = _step_probe(foot, route.foot_end, FOOT_SPEED_MPS)
			foot_wall_contact = foot_wall_contact or _has_wall_contact(foot)
		if not car_reached:
			car_reached = _step_probe(car, route.car_end, CAR_SPEED_MPS)
			car_wall_contact = car_wall_contact or _has_wall_contact(car)
		foot_min_y = minf(foot_min_y, foot.position.y)
		car_min_y = minf(car_min_y, car.position.y)
		if foot_reached and car_reached:
			break

	return {
		"foot_reached": foot_reached,
		"car_reached": car_reached,
		"foot_wall_contact": foot_wall_contact,
		"car_wall_contact": car_wall_contact,
		"foot_min_y": foot_min_y,
		"car_min_y": car_min_y,
	}


## Packs pair endpoints so route helpers stay within the project parameter bound.
func _route(
	foot_start: Vector3,
	foot_end: Vector3,
	car_start: Vector3,
	car_end: Vector3,
) -> Dictionary:
	return {
		"foot_start": foot_start,
		"foot_end": foot_end,
		"car_start": car_start,
		"car_end": car_end,
	}


## Applies one gravity-aware planar movement step and reports endpoint arrival.
func _step_probe(body: CharacterBody3D, target: Vector3, speed_mps: float) -> bool:
	var planar_delta: Vector3 = target - body.position
	planar_delta.y = 0.0
	if planar_delta.length() <= ROUTE_TOLERANCE_M:
		body.velocity = Vector3.ZERO
		return true

	var direction: Vector3 = planar_delta.normalized()
	body.velocity = direction * speed_mps
	body.velocity.y = -4.0
	body.move_and_slide()
	return false


## Detects a non-floor collision so edge coverage cannot pass by merely staying clear.
func _has_wall_contact(body: CharacterBody3D) -> bool:
	for index: int in body.get_slide_collision_count():
		var collision: KinematicCollision3D = body.get_slide_collision(index)
		if absf(collision.get_normal().y) < 0.5:
			return true
	return false


## Waits a finite number of physics ticks so saved static bodies enter the space.
func _wait_for_physics(frames: int) -> void:
	for _frame: int in range(frames):
		await get_tree().physics_frame  # gdstyle:ignore=quality/await-in-loop
