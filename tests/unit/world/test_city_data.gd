extends GutTest
## Verifies the saved Brackett Match identity, anchors, and representative traversal envelopes.

const MATCH_SCENE: PackedScene = preload("res://scenes/match/match.tscn")
const PROBE_SCENE: PackedScene = preload(
	"res://tests/unit/world/fixtures/traversal_probes.tscn"
)
const CITY_PATH: String = "res://scenes/world/brackett_greybox/city.tscn"
const DIGEST_FIXTURE_DIRECTORY: String = "user://c21_content_digest"
const DIGEST_FIXTURE_WORLD_PATH: String = DIGEST_FIXTURE_DIRECTORY + "/world.tscn"
const DIGEST_FIXTURE_SECTOR_PATH: String = DIGEST_FIXTURE_DIRECTORY + "/sector.tscn"
const DIGEST_FIXTURE_MANIFEST_PATH: String = DIGEST_FIXTURE_DIRECTORY + "/manifest.json"
const DIGEST_FIXTURE_WORLD_SOURCE: String = """[gd_scene load_steps=3 format=3]

[ext_resource type="Script" path="res://scenes/world/brackett_greybox/placement.gd" id="1"]
[ext_resource type="PackedScene" path="user://c21_content_digest/sector.tscn" id="2"]

[node name="FixtureWorld" type="Node3D"]
script = ExtResource("1")
world_id = &"brackett"

[node name="Sector" parent="." instance=ExtResource("2")]
"""
const DIGEST_FIXTURE_SECTOR_V1: String = """[gd_scene load_steps=2 format=3]

[sub_resource type="BoxShape3D" id="1"]
size = Vector3(2, 1, 2)

[node name="Sector" type="Node3D"]

[node name="Body" type="StaticBody3D" parent="."]

[node name="Collision" type="CollisionShape3D" parent="Body"]
shape = SubResource("1")
"""
const DIGEST_FIXTURE_SECTOR_V2: String = """[gd_scene load_steps=2 format=3]

[sub_resource type="BoxShape3D" id="1"]
size = Vector3(3, 1, 2)

[node name="Sector" type="Node3D"]

[node name="Body" type="StaticBody3D" parent="."]

[node name="Collision" type="CollisionShape3D" parent="Body"]
shape = SubResource("1")
"""
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
	assert_eq(city_data.content_signature, city_data.calculate_content_signature())
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


## Proves an anchor transform edit invalidates both composition and peer admission.
func test_changed_anchor_is_rejected_as_content_invalid() -> void:
	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match)
	var city_data: CityData = match.get_node("CityData") as CityData
	var anchor: WorldAnchor = match.get_node("Anchors/PlayerSpawns/Spawn01") as WorldAnchor
	assert_true(city_data.validate_composition().ok)

	anchor.position.x += 1.0
	var rejected: Dictionary = city_data.validate_admission(city_data.admission_identity())
	assert_false(rejected.ok)
	assert_eq(rejected.failure.code, CityData.FAILURE_CONTENT_INVALID)


## Proves a transitive sector collision edit invalidates the composed content identity.
func test_changed_dependent_sector_is_rejected_as_content_invalid() -> void:
	_remove_digest_fixture()
	_write_fixture_file(DIGEST_FIXTURE_SECTOR_PATH, DIGEST_FIXTURE_SECTOR_V1)
	_write_fixture_file(DIGEST_FIXTURE_WORLD_PATH, DIGEST_FIXTURE_WORLD_SOURCE)
	var fixture_match: Node3D = _create_digest_fixture_match()
	add_child_autofree(fixture_match)
	var city_data: CityData = fixture_match.get_node("CityData") as CityData
	_write_fixture_file(
		DIGEST_FIXTURE_MANIFEST_PATH,
		JSON.stringify(city_data.build_content_manifest(), "\t") + "\n",
	)
	city_data.content_signature = city_data.calculate_content_signature()
	assert_true(city_data.validate_composition().ok)

	_write_fixture_file(DIGEST_FIXTURE_SECTOR_PATH, DIGEST_FIXTURE_SECTOR_V2)
	var rejected: Dictionary = city_data.validate_admission(city_data.admission_identity())
	assert_false(rejected.ok)
	assert_eq(rejected.failure.code, CityData.FAILURE_CONTENT_INVALID)
	_remove_digest_fixture()


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


## Proves the manifest row bound admits 2048 canonical rows and rejects one more.
func test_content_manifest_accepts_2048_rows_and_rejects_more() -> void:
	var city_data: CityData = autofree(CityData.new()) as CityData

	assert_true(city_data._valid_manifest_resources(_canonical_manifest_rows(2048)))
	assert_false(city_data._valid_manifest_resources(_canonical_manifest_rows(2049)))


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


## Builds strictly sorted, well-formed manifest rows without touching the filesystem.
func _canonical_manifest_rows(count: int) -> Array:
	var rows: Array = []
	for index: int in count:
		rows.append({ "path": "res://bound/%05d.tres" % index, "sha256": "0".repeat(64) })
	return rows


## Builds a small saved world whose collision sector is a transitive dependency.
func _create_digest_fixture_match() -> Node3D:
	var fixture_match := Node3D.new()
	fixture_match.name = "FixtureMatch"
	var world_scene: PackedScene = ResourceLoader.load(
		DIGEST_FIXTURE_WORLD_PATH, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
	) as PackedScene
	var world: Node3D = world_scene.instantiate() as Node3D
	world.name = "World"
	fixture_match.add_child(world)

	var anchors := Node3D.new()
	anchors.name = "Anchors"
	fixture_match.add_child(anchors)
	_add_fixture_anchor_container(anchors, "PlayerSpawns", WorldAnchor.KIND_PLAYER_SPAWN)
	_add_fixture_anchor_container(anchors, "ParkedCars", WorldAnchor.KIND_PARKED_CAR)

	var city_data := CityData.new()
	city_data.name = "CityData"
	fixture_match.add_child(city_data)
	city_data.district_id = &"brackett"
	city_data.content_manifest_path = DIGEST_FIXTURE_MANIFEST_PATH
	city_data.world_path = NodePath("../World")
	city_data.player_spawns_path = NodePath("../Anchors/PlayerSpawns")
	city_data.parked_cars_path = NodePath("../Anchors/ParkedCars")
	return fixture_match


## Adds one minimum valid saved-anchor group to a content-digest fixture.
func _add_fixture_anchor_container(
	parent: Node3D, label: String, kind: StringName
) -> void:
	var container := Node3D.new()
	container.name = label
	parent.add_child(container)
	var anchor := WorldAnchor.new()
	anchor.name = "Anchor"
	anchor.world_id = StringName("brackett/fixture/" + label.to_snake_case())
	anchor.anchor_kind = kind
	container.add_child(anchor)


## Writes one deterministic test resource without mutating the checkout.
func _write_fixture_file(path: String, content: String) -> void:
	DirAccess.make_dir_recursive_absolute(
		ProjectSettings.globalize_path(DIGEST_FIXTURE_DIRECTORY)
	)
	var file: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	assert_not_null(file, "fixture resource opens for writing")
	file.store_string(content)
	file.close()


## Removes generated digest fixtures from the isolated GUT user directory.
func _remove_digest_fixture() -> void:
	for path: String in [
		DIGEST_FIXTURE_WORLD_PATH,
		DIGEST_FIXTURE_SECTOR_PATH,
		DIGEST_FIXTURE_MANIFEST_PATH,
	]:
		if FileAccess.file_exists(path):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	var directory_path: String = ProjectSettings.globalize_path(DIGEST_FIXTURE_DIRECTORY)
	if DirAccess.dir_exists_absolute(directory_path):
		DirAccess.remove_absolute(directory_path)


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
