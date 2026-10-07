extends SceneTree
## Exercises saved S02 motion, query, camera and focus contracts through their owners.

const FIXTURE: PackedScene = preload("res://tests/fixtures/s02/corner.tscn")
const STEP_SECONDS: float = 1.0 / 60.0
const EPSILON_M: float = 0.03

var _fixture: S02Fixture
var _failures: Array[String] = []
var _observations: Dictionary = {}


## Defers the bounded asynchronous checks until the scene tree can accept children.
func _initialize() -> void:
	_run.call_deferred()


## Runs independent expectations and returns a failing exit code for any contract break.
func _run() -> void:
	_fixture = FIXTURE.instantiate() as S02Fixture
	_fixture.manual_mode = true
	root.add_child(_fixture)
	await physics_frame
	await physics_frame
	await _motion_checks()
	await _query_checks()
	await _input_checks()
	_resource_checks()
	var visited: Array[String] = []
	_dependencies("res://tests/fixtures/s02/corner_wide.tscn", visited)
	_dependencies("res://tests/fixtures/s02/weapon_studies.tscn", visited)
	print("S02_RESULT ", JSON.stringify({
		"failures": _failures, "observations": _observations,
		"engine": Engine.get_version_info().string,
	}))
	_fixture.queue_free()
	await process_frame
	quit(0 if _failures.is_empty() else 1)


## Measures straight travel, facing-relative reversal, wall stop, and corner traversal.
func _motion_checks() -> void:
	await _place(Vector3(0, 0.001, 6), 0.0)
	await _advance(60, 1.0, 0.0)
	_expect(_fixture.actor.position.distance_to(Vector3(0, 0.001, 1)) < EPSILON_M,
		"forward travels five metres in one second")
	await _advance(60, -1.0, 0.0)
	_expect(absf(_fixture.actor.position.z - 4.0) < EPSILON_M,
		"backward travels three metres without reversing facing")
	var before: Vector3 = _fixture.actor.position
	await _advance(30, 0.0, 1.0)
	_expect(_fixture.actor.position.distance_to(before) < EPSILON_M, "turn does not strafe")
	_expect(absf(_fixture.actor.rotation.y + PI / 2.0) < 0.001, "right turn faces east")
	await _advance(60, 1.0, 0.0)
	_expect(absf(_fixture.actor.position.x - 5.0) < EPSILON_M,
		"forward follows turned facing instead of world north")
	await _place(Vector3(6, 0.001, 3), 0.0)
	await _advance(90, 1.0, 0.0)
	_expect(_fixture.actor.position.z >= 0.37 and _fixture.actor.position.z < 0.43,
		"solid east corner stops actor capsule")
	_observations["wall_stop"] = str(_fixture.actor.position)
	await _place(Vector3(0, 0.001, 3), 0.0)
	await _advance(144, 1.0, 0.0)
	_expect(_fixture.actor.position.z < -8.9, "four-metre passage is traversable")
	await _advance(30, 0.0, 1.0)
	await _advance(36, 1.0, 0.0)
	_expect(_fixture.actor.position.x > 2.9, "actor rounds the north-east corner")
	_observations["corner_end"] = str(_fixture.actor.position)
	_fixture.actor.step(NAN, 0.0, STEP_SECONDS)
	_expect(_fixture.actor.velocity == Vector3.ZERO, "nonfinite intent neutralizes motion")


## Confirms clear hits, world obstruction and close-wall muzzle protection.
func _query_checks() -> void:
	await _place(Vector3(0, 0.001, 6), 0.0)
	_fixture.aim.clear()
	_fixture.step_intent(0.0, 0.0, true, STEP_SECONDS)
	_expect(_fixture.aim.last_hit == _fixture.get_node("TargetClear"),
		"facing ray hits the intended clear target")
	await _place(Vector3(5.57, 0.001, 3), 0.0)
	_fixture.aim.clear()
	_fixture.step_intent(0.0, 0.0, true, STEP_SECONDS)
	_expect(_fixture.aim.last_hit == _fixture.get_node("EastCorner/Collision/Body"),
		"world blocks the target behind the building")
	await _place(Vector3(5.57, 0.001, 0.4), 0.0)
	_fixture.aim.clear()
	_fixture.step_intent(0.0, 0.0, true, STEP_SECONDS)
	_expect(_fixture.aim.last_hit == _fixture.get_node("EastCorner/Collision/Body"),
		"muzzle beyond the wall cannot fire through it")
	var shots: int = _fixture.aim.shot_count
	await _advance(60, 0.0, 0.0, true)
	_expect(_fixture.aim.shot_count - shots <= 4, "held-fire probe remains bounded")
	_observations["shot_count"] = _fixture.aim.shot_count


## Exercises actual viewport event routing and the focus transition used by OS notifications.
func _input_checks() -> void:
	_fixture.input_collector.set_focused(true)
	_key(KEY_W, true)
	_key(KEY_SPACE, true)
	await process_frame
	_expect(_fixture.input_collector.sample().move == 1.0, "physical W maps to forward")
	_expect(_fixture.input_collector.sample().fire, "physical Space maps to fire")
	_fixture.input_collector.set_focused(false)
	_expect(_fixture.input_collector.sample().move == 0.0, "focus loss clears movement")
	_expect(not _fixture.input_collector.sample().fire, "focus loss clears fire")
	_fixture.input_collector.set_focused(true)
	_key(KEY_W, true, true)
	await process_frame
	_expect(_fixture.input_collector.sample().move == 0.0, "focus regain rejects held echo")
	_key(KEY_W, false)
	_key(KEY_SPACE, false)
	_key(KEY_W, true)
	await process_frame
	_expect(_fixture.input_collector.sample().move == 1.0, "fresh press resumes movement")
	_key(KEY_ESCAPE, true)
	_key(KEY_ESCAPE, false)
	_expect(_fixture.input_collector.sample().move == 0.0, "local menu cancels intent")
	_key(KEY_W, false)


## Verifies live camera orientation, import links and source-derived muzzle geometry.
func _resource_checks() -> void:
	var camera: Camera3D = _fixture.rig.camera()
	_expect(camera.projection == Camera3D.PROJECTION_PERSPECTIVE, "perspective camera")
	_expect((-camera.global_basis.z).dot(Vector3.DOWN) > 0.9999, "camera points vertically down")
	_expect(absf(camera.global_rotation.y) < 0.0001, "camera fixed world yaw")
	_expect(absf(camera.position.y - 47.0) < 0.001, "camera height retained")
	var model: Node = _fixture.actor.get_node("PresentationAnchor/Visuals/Model")
	_expect(model.scene_file_path == "res://art/models/spikes/s02_actor.glb", "linked actor import")
	var muzzle: Vector3 = _fixture.actor.to_local(_fixture.actor.muzzle_position())
	_expect(muzzle.distance_to(Vector3(0.43, 1.2, -1.02)) < 0.0001,
		"Blender-derived pistol muzzle retained")
	_observations["muzzle_local"] = str(muzzle)
	_observations["camera_fov"] = camera.fov
	var ids: Array[String] = []
	for entry: Array in [["WestCorner", 6.0], ["NearTower", 46.0], ["TallTower", 60.0]]:
		var building: S02BuildingView = _fixture.get_node(entry[0]) as S02BuildingView
		var identity: String = building.get_meta("world_id")
		_expect(not ids.has(identity), "distinct authored building identity")
		ids.append(identity)
		var bounds: AABB = _model_bounds(building.get_node("Visuals/Model"))
		_expect(absf(bounds.end.y - float(entry[1])) < 0.001, "imported building height")
		_expect(absf(bounds.position.y) < 0.001, "building ground datum")
		_observations[str(entry[0]) + "_bounds"] = str(bounds)


## Measures the actual imported meshes in their linked model root's coordinates.
func _model_bounds(model: Node3D) -> AABB:
	var combined: AABB
	var first: bool = true
	for node: Node in model.find_children("*", "MeshInstance3D", true, false):
		var mesh: MeshInstance3D = node as MeshInstance3D
		var local: Transform3D = model.global_transform.affine_inverse() * mesh.global_transform
		var bounds: AABB = local * mesh.get_aabb()
		combined = bounds if first else combined.merge(bounds)
		first = false
	return combined


## Resolves saved dependency identities so fallback paths cannot hide UID mismatches.
func _dependencies(path: String, visited: Array[String]) -> void:
	if visited.has(path):
		return

	visited.append(path)
	_expect(ResourceLoader.exists(path), "resource exists: " + path)
	_expect(ResourceLoader.load(path) != null, "resource loads: " + path)
	for dependency: String in ResourceLoader.get_dependencies(path):
		var parts: PackedStringArray = dependency.split("::")
		var fallback: String = parts[parts.size() - 1]
		if dependency.begins_with("uid://"):
			var identity: int = ResourceUID.text_to_id(parts[0])
			_expect(ResourceUID.has_id(identity), "registered UID: " + dependency)
			if ResourceUID.has_id(identity):
				_expect(ResourceUID.get_id_path(identity) == fallback, "UID/path: " + dependency)
		_dependencies(fallback, visited)


## Places only the dynamic test actor, then waits for physics query synchronization.
func _place(position: Vector3, yaw: float) -> void:
	_fixture.actor.position = position
	_fixture.actor.rotation.y = yaw
	_fixture.actor.neutralize()
	await physics_frame
	await physics_frame


## Steps the production entrypoint once per real engine physics frame.
func _advance(ticks: int, move_axis: float, turn_axis: float, fire: bool = false) -> void:
	for tick: int in ticks:
		# Real physics ticks are the behavior under test, not busy waiting.
		# gdstyle:ignore=quality/await-in-loop
		await physics_frame
		_fixture.step_intent(move_axis, turn_axis, fire, STEP_SECONDS)


## Pushes physical key events through normal viewport GUI/unhandled routing.
func _key(code: Key, pressed: bool, echo: bool = false) -> void:
	var event: InputEventKey = InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = pressed
	event.echo = echo
	root.push_input(event)


## Accumulates independent contract failures without abandoning subsequent checks.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error("S02: " + message)
