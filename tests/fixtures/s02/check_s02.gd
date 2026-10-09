extends SceneTree
## Exercises saved S02 movement, mouse aim, query, camera and focus contracts.

const FIXTURE: PackedScene = preload("res://tests/fixtures/s02/corner.tscn")
const STEP_SECONDS: float = 1.0 / 60.0
const EPSILON_M: float = 0.03
const CADENCE_SETTLE_TICKS: int = 16

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
	await _alias_checks()
	await _cadence_checks()
	_target_overlap_checks()
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


## Measures world-relative cardinal/diagonal travel, snap-facing, stop and collision.
func _motion_checks() -> void:
	await _place(Vector3(0, 0.001, 6), PI / 2.0)
	await _advance(60, Vector2(0.0, -1.0), 0.0)
	_expect(_fixture.actor.position.distance_to(Vector3(0, 0.001, 1)) < EPSILON_M,
		"W travels world north at five metres per second independent of facing")
	await _advance(60, Vector2(0.0, 1.0), 0.0)
	_expect(_fixture.actor.position.distance_to(Vector3(0, 0.001, 6)) < EPSILON_M,
		"S travels world south at the same speed")
	await _advance(60, Vector2(-1.0, 0.0), 0.0)
	_expect(_fixture.actor.position.distance_to(Vector3(-5, 0.001, 6)) < EPSILON_M,
		"A strafes world west without using facing")
	await _place(Vector3(0, 0.001, 6), 0.0)
	await _advance(60, Vector2(1.0, -1.0), -PI / 2.0)
	_expect(absf(_fixture.actor.position.distance_to(Vector3(0, 0.001, 6)) - 5.0) < EPSILON_M,
		"diagonal movement is normalized to five metres per second")
	_expect(absf(_fixture.actor.rotation.y + PI / 2.0) < 0.001,
		"facing snaps to command aim yaw")
	_fixture.actor.step(Vector2.ZERO, PI, STEP_SECONDS)
	_expect(_fixture.actor.velocity == Vector3.ZERO, "released movement stops immediately")
	_expect(absf(absf(_fixture.actor.rotation.y) - PI) < 0.001, "stationary aim still snaps")
	await _place(Vector3(6, 0.001, 3), 0.0)
	await _advance(90, Vector2(0.0, -1.0), 0.0)
	_expect(_fixture.actor.position.z >= 0.37 and _fixture.actor.position.z < 0.43,
		"solid east corner stops actor capsule")
	_observations["wall_stop"] = str(_fixture.actor.position)
	await _place(Vector3(0, 0.001, 3), 0.0)
	await _advance(144, Vector2(0.0, -1.0), 0.0)
	_expect(_fixture.actor.position.z < -8.9, "four-metre passage is traversable")
	await _advance(36, Vector2(1.0, 0.0), -PI / 2.0)
	_expect(_fixture.actor.position.x > 2.9, "world-relative movement rounds the north-east corner")
	_observations["corner_end"] = str(_fixture.actor.position)
	_fixture.actor.step(Vector2(NAN, 0.0), 0.0, STEP_SECONDS)
	_expect(_fixture.actor.velocity == Vector3.ZERO, "nonfinite movement neutralizes motion")
	var first: Dictionary = S02MotionRules.advance(
		{ "yaw": 0.4 }, Vector2(1.0, -1.0), -0.7)
	var second: Dictionary = S02MotionRules.advance(
		{ "yaw": 0.4 }, Vector2(1.0, -1.0), -0.7)
	_expect(first == second, "shared movement rule is deterministic for identical state and input")


## Confirms aimed hits, world obstruction and close-wall muzzle protection.
func _query_checks() -> void:
	await _place(Vector3(0, 0.001, 6), 0.0)
	_fixture.aim.clear()
	_step(Vector2.ZERO, 0.0, true)
	_expect(_fixture.aim.last_hit == _fixture.get_node("TargetClear"),
		"mouse-facing ray hits the intended clear target")
	await _place(Vector3(3.57, 0.001, 3), 0.0)
	await _advance(CADENCE_SETTLE_TICKS, Vector2.ZERO, 0.0)
	_fixture.aim.clear()
	_step(Vector2.ZERO, 0.0, true)
	_expect(_fixture.aim.last_hit == _fixture.get_node("EastCorner/Collision/Body"),
		"world blocks the target behind the building")
	await _place(Vector3(3.57, 0.001, -9), 0.0)
	await _advance(CADENCE_SETTLE_TICKS, Vector2.ZERO, 0.0)
	var target: Node3D = _fixture.get_node("TargetBlocked") as Node3D
	_step(Vector2.ZERO, 0.0, true)
	_expect(_fixture.aim.last_hit == target,
		"previously blocked target is hittable after moving around the corner")
	_observations["blocked_to_clear_end"] = str(_fixture.actor.position)
	await _place(Vector3(5.57, 0.001, 0.4), 0.0)
	await _advance(CADENCE_SETTLE_TICKS, Vector2.ZERO, 0.0)
	_fixture.aim.clear()
	_step(Vector2.ZERO, 0.0, true)
	_expect(_fixture.aim.last_hit == _fixture.get_node("EastCorner/Collision/Body"),
		"muzzle beyond the wall cannot fire through it")
	var shots: int = _fixture.aim.shot_count
	await _advance(60, Vector2.ZERO, 0.0, true)
	_expect(_fixture.aim.shot_count - shots <= 4, "held-fire probe remains bounded")
	_observations["shot_count"] = _fixture.aim.shot_count


## Exercises viewport event routing, mouse projection and focus cancellation.
func _input_checks() -> void:
	_fixture.input_collector.set_focused(true)
	_key(KEY_W, true)
	_mouse_button(true)
	await process_frame
	_expect(_fixture.input_collector.sample().move == Vector2(0.0, -1.0),
		"physical W maps to world north")
	_expect(_fixture.input_collector.sample().fire, "left mouse maps to fire")
	var right_screen: Vector2 = _fixture.get_viewport().get_visible_rect().size * 0.5 + (
		Vector2(200.0, 0.0))
	var right_yaw: float = _fixture.input_collector.aim_yaw_for_screen(right_screen)
	_expect(absf(right_yaw + PI / 2.0) < 0.01, "camera ray maps right screen aim to world east")
	_fixture.input_collector.set_focused(false)
	_expect(_fixture.input_collector.sample().move == Vector2.ZERO, "focus loss clears movement")
	_expect(not _fixture.input_collector.sample().fire, "focus loss clears fire")
	_fixture.input_collector.set_focused(true)
	_key(KEY_W, true, true)
	await process_frame
	_expect(_fixture.input_collector.sample().move == Vector2.ZERO,
		"focus regain rejects held echo")
	_key(KEY_W, false)
	_mouse_button(false)
	_key(KEY_SPACE, true)
	await process_frame
	_expect(_fixture.input_collector.sample().fire, "Space remains an alternate fire binding")
	_key(KEY_SPACE, false)
	_key(KEY_W, true)
	_key(KEY_ESCAPE, true)
	_key(KEY_ESCAPE, false)
	_expect(_fixture.input_collector.sample().move == Vector2.ZERO, "local menu cancels intent")
	_key(KEY_W, false)
	_key(KEY_ESCAPE, true)
	_key(KEY_ESCAPE, false)


## Checks every movement alias pair in both release orders through viewport routing.
func _alias_checks() -> void:
	for pair: Array in [
		[KEY_W, KEY_UP, Vector2(0.0, -1.0)], [KEY_S, KEY_DOWN, Vector2(0.0, 1.0)],
		[KEY_A, KEY_LEFT, Vector2(-1.0, 0.0)], [KEY_D, KEY_RIGHT, Vector2(1.0, 0.0)],
	]:
		for order: int in [0, 1]:
			# Each alias order includes actual movement while one binding remains.
			# gdstyle:ignore=quality/await-in-loop
			await _alias_order(pair[order], pair[1 - order], pair[2])
	_fixture.input_collector.set_focused(true)
	_key(KEY_W, true)
	_key(KEY_S, true)
	_expect(_fixture.input_collector.sample().move == Vector2.ZERO, "opposite directions cancel")
	_key(KEY_S, false)
	_expect(_fixture.input_collector.sample().move == Vector2(0.0, -1.0),
		"opposite release retains north movement")
	_key(KEY_W, false)


## Preserves the remaining alias, then verifies focus and menu clear both bindings.
func _alias_order(first: Key, second: Key, expected: Vector2) -> void:
	await _place(Vector3(0, 0.001, 6), 0.0)
	_fixture.input_collector.set_focused(true)
	_key(first, true)
	_key(second, true)
	_key(first, false)
	_expect(_fixture.input_collector.sample().move == expected, "remaining alias retains movement")
	var before: Vector3 = _fixture.actor.position
	await _collected_ticks(6)
	_expect(_fixture.actor.position.distance_to(before) > 0.25, "remaining alias moves actor")
	_key(second, false)
	_expect(_fixture.input_collector.sample().move == Vector2.ZERO,
		"last alias release neutralizes")
	_key(first, true)
	_key(second, true)
	_fixture.input_collector.set_focused(false)
	_fixture.input_collector.set_focused(true)
	_key(first, true, true)
	_key(second, true, true)
	_expect(_fixture.input_collector.sample().move == Vector2.ZERO,
		"focus rejects both stale aliases")
	_key(first, false)
	_key(second, false)
	_key(first, true)
	_key(second, true)
	_key(KEY_ESCAPE, true)
	_key(KEY_ESCAPE, false)
	_key(KEY_ESCAPE, true)
	_key(KEY_ESCAPE, false)
	_key(first, true, true)
	_key(second, true, true)
	_expect(_fixture.input_collector.sample().move == Vector2.ZERO,
		"menu rejects both stale aliases")
	_key(first, false)
	_key(second, false)


## Ensures menu/focus cancellation cannot grant an early fresh-input shot.
func _cadence_checks() -> void:
	for use_menu: bool in [true, false]:
		# Independent lifecycle cases advance only real engine physics callbacks.
		# gdstyle:ignore=quality/await-in-loop
		await _cadence_case(use_menu)


## Measures a fresh shot before and after input suspension inside the ray interval.
func _cadence_case(use_menu: bool) -> void:
	_fixture.input_collector.set_focused(true)
	await _collected_ticks(CADENCE_SETTLE_TICKS)
	var before: int = _fixture.aim.shot_count
	_mouse_button(true)
	await _collected_ticks(1)
	_expect(_fixture.aim.shot_count == before + 1, "fresh left click emits initial shot")
	_mouse_button(false)
	if use_menu:
		_key(KEY_ESCAPE, true)
		_key(KEY_ESCAPE, false)
		_key(KEY_ESCAPE, true)
		_key(KEY_ESCAPE, false)
	else:
		_fixture.input_collector.set_focused(false)
		_fixture.input_collector.set_focused(true)
	_expect(not _fixture.input_collector.sample().fire, "suspension immediately clears fire")
	_mouse_button(true)
	await _collected_ticks(2)
	_expect(_fixture.aim.shot_count == before + 1, "suspension cannot bypass ray interval")
	await _collected_ticks(14)
	_expect(_fixture.aim.shot_count == before + 2, "fresh fire resumes after ray interval")
	_mouse_button(false)


## Checks actual target shapes against solid world, excluding intentional ground contact.
func _target_overlap_checks() -> void:
	var ground: StaticBody3D = _fixture.get_node("Ground/Collision/Body") as StaticBody3D
	var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
	for target_name: String in ["TargetClear", "TargetBlocked"]:
		var target: StaticBody3D = _fixture.get_node(target_name) as StaticBody3D
		var shape: CollisionShape3D = target.get_node("Collision") as CollisionShape3D
		query.shape = shape.shape
		query.transform = shape.global_transform
		query.collision_mask = S02AimProbe.WORLD_LAYER
		query.exclude = [ground.get_rid()]
		var space: PhysicsDirectSpaceState3D = target.get_world_3d().direct_space_state
		var hits: Array[Dictionary] = space.intersect_shape(query)
		_expect(hits.is_empty(), target_name + " occupies free world space")
		_observations[target_name + "_world_overlaps"] = hits.size()


## Advances sampled routed input through the standalone coordinator.
func _collected_ticks(ticks: int) -> void:
	for tick: int in ticks:
		# Real physics ticks preserve collision and cadence behavior.
		# gdstyle:ignore=quality/await-in-loop
		await physics_frame
		_fixture.step_command(_fixture.input_collector.sample(), STEP_SECONDS)


## Verifies live camera orientation, import links and source-derived geometry.
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
		var building: Node3D = _fixture.get_node(entry[0]) as Node3D
		var identity: String = building.get_meta("world_id")
		_expect(not ids.has(identity), "distinct authored building identity")
		ids.append(identity)
		var bounds: AABB = _model_bounds(building.get_node("Visuals/Model"))
		_expect(absf(bounds.end.y - float(entry[1])) < 0.001, "imported building height")
		_expect(absf(bounds.position.y) < 0.001, "building ground datum")
		_observations[str(entry[0]) + "_bounds"] = str(bounds)


## Measures imported meshes in their linked model root's coordinates.
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
	_fixture.rig.bind(_fixture.actor)
	await physics_frame
	await physics_frame


## Steps the production command entrypoint once per real engine physics frame.
func _advance(ticks: int, move: Vector2, aim_yaw: float, fire: bool = false) -> void:
	for tick: int in ticks:
		# Real physics ticks are the behavior under test, not busy waiting.
		# gdstyle:ignore=quality/await-in-loop
		await physics_frame
		_step(move, aim_yaw, fire)


## Applies one explicit simulation command without collecting a device.
func _step(move: Vector2, aim_yaw: float, fire: bool = false) -> void:
	_fixture.step_command({
		"move": move, "aim_yaw": aim_yaw, "fire": fire,
	}, STEP_SECONDS)


## Pushes physical key events through normal viewport GUI/unhandled routing.
func _key(code: Key, pressed: bool, echo: bool = false) -> void:
	var event: InputEventKey = InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = pressed
	event.echo = echo
	root.push_input(event)


## Pushes the primary mouse binding through normal viewport routing.
func _mouse_button(pressed: bool) -> void:
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_LEFT
	event.pressed = pressed
	root.push_input(event)


## Accumulates independent contract failures without abandoning subsequent checks.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error("S02: " + message)
