extends SceneTree
## Validate the modular rail's linked wrappers, saved identities and capsule blocking.

const ASSET := "city_quay_furniture_02"
const DIRECTORY := "res://scenes/prefabs/environment/"
const MODELS := "res://art/models/environment/city_quay_furniture_02/"
const FIXTURE := "res://tools/asset_production/city_quay_furniture_02/check_scene.tscn"
const EVIDENCE := "res://docs/assets/production/city_quay_furniture_02-evidence/validation.json"
const OPENING := "res://tools/asset_production/city_quay_furniture_02/opening_scene.tscn"
const FORMS := ["straight", "corner", "end", "post"]
const MOUNTS := { "quay": Vector2(.30, .30), "deck": Vector2(.22, .34),
	"landward": Vector2(.32, .32) }
const POST_POSITIONS := {
	"straight": [Vector3(-1.5, 0, 0), Vector3(1.5, 0, 0)],
	"corner": [Vector3(-.75, 0, .75), Vector3(.691_421_356, 0, .691_421_356),
		Vector3(.75, 0, -.75)],
	"end": [Vector3.ZERO], "post": [],
}
const WALK_TICKS := 48
const CONTACT_GAP_LIMIT_M := .03
const CONTACT_NUMERIC_TOLERANCE_M := .00001

var _failed := false
var _report: Dictionary = { "resource_uids": {}, "prefabs": {} }


## Start after the main loop exists so physics and saved resources can initialize.
func _initialize() -> void:
	_run.call_deferred()


## Normalize fresh wrappers and check each mounting/form combination independently.
func _run() -> void:
	_require(Engine.get_version_info()["hash"].begins_with("c971f93e7"), "Engine pin")
	if "--normalize" in OS.get_cmdline_user_args():
		for mount: String in MOUNTS:
			for form: String in FORMS:
				_roundtrip(_path(form, mount))

		_roundtrip(FIXTURE)
		_roundtrip(OPENING)
		_report["save_reload_byte_stable"] = true

	_check_dependencies(FIXTURE)
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	for mount: String in MOUNTS:
		for form: String in FORMS:
			var path: String = _path(form, mount)
			_check_dependencies(path)
			var scene: PackedScene = load(path)
			var instance: Node3D = scene.instantiate()
			var receipt: Dictionary = _check_model(instance, form, mount)
			fixture.add_child(instance)
			# Each instance gets an isolated bounded physics run, not frame-loop work.
			receipt["physics"] = await _check_physics(  # gdstyle:ignore=quality/await-in-loop
				fixture, instance, form, mount,
			)
			_report["prefabs"][path] = receipt
			instance.free()

	fixture.free()
	_check_dependencies(OPENING)
	await _check_opening()
	if _failed:
		quit(1)
		return

	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(EVIDENCE))
	if data.has("godot") and not _report.has("save_reload_byte_stable"):
		_report["save_reload_byte_stable"] = data["godot"].get("save_reload_byte_stable", false)

	_report["engine"] = Engine.get_version_info()["string"]
	data["godot"] = _report
	var file: FileAccess = FileAccess.open(EVIDENCE, FileAccess.WRITE)
	file.store_string(JSON.stringify(data, "\t") + "\n")
	file.close()
	print("CITY_QUAY_FURNITURE_02_CHECK_PASS ", JSON.stringify(_report))
	quit(0)


## Resolve the default quay straight name without adding a duplicate wrapper.
func _path(form: String, mount: String) -> String:
	if form == "straight" and mount == "quay":
		return DIRECTORY + ASSET + ".tscn"

	return DIRECTORY + ASSET + "_" + form + "_" + mount + ".tscn"


## Retain all failures in process diagnostics rather than silently accepting partial checks.
func _require(condition: bool, message: String) -> void:
	if not condition:
		_failed = true
		push_error(message)


## Pack/resave twice and prove registered scene IDs and serialized bytes stabilize.
func _roundtrip(path: String) -> void:
	var uid: int = ResourceLoader.get_resource_uid(path)
	if uid == ResourceUID.INVALID_ID:
		uid = ResourceUID.create_id()
		ResourceUID.add_id(uid, path)

	var first_hash := ""
	for iteration: int in 2:
		var source: PackedScene = ResourceLoader.load(
			path,
			"PackedScene",
			ResourceLoader.CACHE_MODE_IGNORE,
		)
		var instance: Node = source.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
		var packed := PackedScene.new()  # gdstyle:ignore=quality/allocation-in-loop
		_require(packed.pack(instance) == OK, "Scene packing failed: " + path)
		_require(ResourceSaver.save(packed, path) == OK, "Scene save failed: " + path)
		_require(ResourceSaver.set_uid(path, uid) == OK, "UID save failed: " + path)
		instance.free()
		var current: String = FileAccess.get_sha256(path)
		if iteration == 1:
			_require(current == first_hash, "Save/reload drift: " + path)

		first_hash = current


## Load every dependency and prove all serialized resource identities resolve correctly.
func _check_dependencies(path: String) -> void:
	if _report["resource_uids"].has(path):
		return

	_require(ResourceLoader.load(path) != null, "Missing dependency: " + path)
	var uid: int = ResourceLoader.get_resource_uid(path)
	_require(uid != ResourceUID.INVALID_ID and ResourceUID.has_id(uid), "Unregistered UID: " + path)
	_require(ResourceUID.get_id_path(uid) == path, "UID path mismatch: " + path)
	_report["resource_uids"][path] = ResourceUID.id_to_text(uid)
	for dependency: String in ResourceLoader.get_dependencies(path):
		var fields: PackedStringArray = dependency.split("::")
		var child: String = fields[-1]
		if fields[0].begins_with("uid://"):
			_require(ResourceUID.get_id_path(ResourceUID.text_to_id(fields[0])) == child,
				"Serialized dependency UID mismatch: " + dependency)

		_check_dependencies(child)


## Measure the assembled imported visuals against independent provisional envelopes.
func _check_model(instance: Node3D, form: String, mount: String) -> Dictionary:
	var model: Node3D = instance.get_node("Visuals/Model")
	var component: String = "post_" + mount if form == "post" else form
	_require(model.transform == Transform3D.IDENTITY, "Corrective Visuals/Model transform")
	_require(model.scene_file_path == MODELS + ASSET + "_" + component + ".glb", "Unlinked model")
	var positions: Array = POST_POSITIONS[form]
	var visuals: Node3D = instance.get_node("Visuals")
	_require(visuals.get_child_count() == 1 + positions.size(), "Unexpected visual component count")
	for index: int in positions.size():
		var post: Node3D = visuals.get_node("Post%d" % index)
		_require(post.position.is_equal_approx(positions[index]), "Post connector mismatch")
		_require(post.basis == Basis.IDENTITY, "Post corrective rotation/scale")
		_require(
			post.scene_file_path == MODELS + ASSET + "_post_" + mount + ".glb",
			"Unlinked post",
		)

	var measured: Dictionary = _measure_meshes(visuals)
	var bounds: AABB = measured["bounds"]
	var expected: AABB = _expected_bounds(form, mount)
	_require(measured["mesh_count"] == 1 + positions.size(), "Unexpected mesh count")
	_require(
		bounds.position.distance_to(expected.position) < .001,
		"Bounds minimum: " + form + mount,
	)
	_require(bounds.size.distance_to(expected.size) < .001, "Bounds size: " + form + mount)
	_require(measured["surface_count"] == (3 if form == "post" else 1 + positions.size() * 3),
		"Surface count")
	_check_collision(instance, form, expected)
	return { "linked_model_identity": true, "mesh_count": measured["mesh_count"],
		"surface_count": measured["surface_count"], "bounds_min_m": _xyz(bounds.position),
		"bounds_size_m": _xyz(bounds.size) }


## Accumulate imported hierarchy transforms without requiring an active world tree.
func _relative_transform(node: Node3D, ancestor: Node3D) -> Transform3D:
	var result := Transform3D.IDENTITY
	var current: Node3D = node
	while current != ancestor:
		result = current.transform * result
		current = current.get_parent() as Node3D

	return result


## Inspect all source-linked surfaces and return their actual aggregate envelope.
func _measure_meshes(visuals: Node3D) -> Dictionary:
	var bounds := AABB()
	var first := true
	var surfaces := 0
	var meshes: Array[Node] = visuals.find_children("*", "MeshInstance3D", true, false)
	for node: Node in meshes:
		var mesh: MeshInstance3D = node as MeshInstance3D
		var local: AABB = _relative_transform(mesh, visuals) * mesh.mesh.get_aabb()
		bounds = local if first else bounds.merge(local)
		first = false
		surfaces += mesh.mesh.get_surface_count()
		for surface: int in mesh.mesh.get_surface_count():
			var material: BaseMaterial3D = mesh.mesh.surface_get_material(surface)
			_require(
				material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED,
				"Transparent rail",
			)
			_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Two-sided rail")

	return { "bounds": bounds, "mesh_count": meshes.size(), "surface_count": surfaces }


## State complete wrapper envelopes independently of the geometry authoring recipe.
func _expected_bounds(form: String, mount: String) -> AABB:
	var foot: Vector2 = MOUNTS[mount]
	if form == "straight":
		return AABB(Vector3(-1.5 - foot.x / 2, 0, -foot.y / 2), Vector3(3 + foot.x, 1.06, foot.y))

	if form == "corner":
		return AABB(Vector3(-.75 - foot.x / 2, 0, -.75 - foot.y / 2),
			Vector3(1.5 + foot.x, 1.06, 1.5 + foot.y))

	if form == "end":
		return AABB(Vector3(-foot.x / 2, 0, -foot.y / 2), Vector3(.535 + foot.x / 2, 1.06, foot.y))

	return AABB(Vector3(-foot.x / 2, 0, -foot.y / 2), Vector3(foot.x, 1.06, foot.y))


## Require one separate static body; the corner keeps an open inside rather than a solid square.
func _check_collision(instance: Node3D, form: String, bounds: AABB) -> void:
	_require(instance.find_children("*", "CollisionObject3D", true, false).size() == 1,
		"Expected one simple body")
	var body: StaticBody3D = instance.get_node("Collision/RailBody")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Static-world filtering")
	var shapes: Array[Node] = body.find_children("*", "CollisionShape3D", true, false)
	_require(shapes.size() == (2 if form == "corner" else 1), "Simple shape count")
	for node: Node in shapes:
		var shape: CollisionShape3D = node as CollisionShape3D
		var box: BoxShape3D = shape.shape as BoxShape3D
		_require(box != null, "Non-box collision")
		_require(is_equal_approx(box.size.y, 1.06) and is_equal_approx(shape.position.y, .53),
			"Collision height/datum")
		if form != "corner":
			_require(box.size.is_equal_approx(bounds.size), "Collision size")
			_require(shape.position.is_equal_approx(bounds.get_center()), "Collision centre")


## Probe low/high rays, corner interior and the production capsule in authority/replay modes.
func _check_physics(fixture: Node3D, instance: Node3D, form: String, mount: String) -> Dictionary:
	await physics_frame
	await physics_frame
	var x := .2 if form == "end" else 0.0
	_check_rays(fixture, instance, form, mount, x)
	var contacts: Array[Vector3] = []
	var bypasses: Array[Vector3] = []
	for mode: ActorMotion.StepMode in [ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY]:
		contacts.append(await _walk(fixture.get_node("Actor"), x, mode))
		bypasses.append(await _walk(fixture.get_node("Actor"), 2.5, mode))

	var depth: float = MOUNTS[mount].y
	var contact_plane: float = (.75 if form == "corner" else 0.0) - depth / 2 - .35
	_require(
		contacts[0].z <= contact_plane + CONTACT_NUMERIC_TOLERANCE_M,
		"Capsule penetrates rail: " + form + mount,
	)
	_require(contacts[0].z >= contact_plane - CONTACT_GAP_LIMIT_M, "Excess capsule gap")
	_require(absf(contacts[0].x - x) < .005 and absf(contacts[0].y) < .005, "Contact drift")
	_require(bypasses[0].distance_to(Vector3(2.5, 0, 2)) < .015, "Bypass failed")
	_require(contacts[0].is_equal_approx(contacts[1]), "Authority/replay contact differs")
	_require(bypasses[0].is_equal_approx(bypasses[1]), "Authority/replay bypass differs")
	print("RAIL_PHYSICS ", form, " ", mount, " ", contacts[0], " bypass=", bypasses[0])
	return { "low_ray_blocked": true, "above_rail_ray_clear": true,
		"corner_interior_clear": form == "corner", "authority_replay_equal": true,
		"contact_stop_m": _xyz(contacts[0]), "contact_plane_z_m": contact_plane,
		"bypass_end_m": _xyz(bypasses[0]), "actor_capsule_radius_m": .35,
		"actor_capsule_height_m": 1.8, "ticks_per_case_per_mode": WALK_TICKS,
		"allowed_precontact_gap_m": CONTACT_GAP_LIMIT_M,
		"contact_numeric_tolerance_m": CONTACT_NUMERIC_TOLERANCE_M }


## Verify both corner arms, open interior and the rail's finite blocking height.
func _check_rays(fixture: Node3D, instance: Node3D, form: String, mount: String, x: float) -> void:
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	var low := PhysicsRayQueryParameters3D.create(Vector3(x, .5, -2), Vector3(x, .5, 2), 1)
	var hit: Dictionary = space.intersect_ray(low)
	_require(not hit.is_empty(), "Low ray missed " + form + mount)
	if not hit.is_empty():
		_require(hit["collider"] == instance.get_node("Collision/RailBody"), "Wrong ray body")

	var high := PhysicsRayQueryParameters3D.create(Vector3(x, 1.2, -2), Vector3(x, 1.2, 2), 1)
	_require(space.intersect_ray(high).is_empty(), "Collision above rail")
	if form == "corner":
		var inside := PhysicsRayQueryParameters3D.create(
			Vector3(-.4, 1.2, -.4),
			Vector3(-.4, .1, -.4),
			1,
		)
		_require(space.intersect_ray(inside).is_empty(), "Corner interior is filled")
		var side := PhysicsRayQueryParameters3D.create(Vector3(0, .5, 0), Vector3(2, .5, 0), 1)
		_require(not space.intersect_ray(side).is_empty(), "Second corner arm has no collision")


## Prove a saved 1.4 m terminal opening passes the capsule while both returns block.
func _check_opening() -> void:
	var packed: PackedScene = load(OPENING)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var outcomes: Array[Vector3] = []
	for mode: ActorMotion.StepMode in [ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY]:
		for x: float in [0.0, -.9, .9]:
			outcomes.append(await _walk(fixture.get_node("Actor"), x, mode))

	_require(outcomes[0].distance_to(Vector3(0, 0, 2)) < .015, "Clear access opening failed")
	_require(absf(outcomes[1].z + .5) < .002, "Left terminal did not block")
	_require(absf(outcomes[2].z + .5) < .002, "Right terminal did not block")
	for index: int in 3:
		_require(outcomes[index].is_equal_approx(outcomes[index + 3]), "Opening replay mismatch")

	_report["access_opening"] = { "clear_width_m": 1.4, "authority_replay_equal": true,
		"passage_end_m": _xyz(outcomes[0]), "left_contact_m": _xyz(outcomes[1]),
		"right_contact_m": _xyz(outcomes[2]), "fixture_not_world_placement": true }
	fixture.free()


## Exercise ActorMotion.step rather than a test-specific movement implementation.
func _walk(actor: ActorMotion, x: float, mode: ActorMotion.StepMode) -> Vector3:
	actor.position = Vector3(x, .001, -2)
	actor.neutralize()
	actor.apply_floor_snap()
	for tick: int in WALK_TICKS:
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick + 1, tick, Vector2(0, 1), 0.0, false, false,
		)
		_require(actor.step(command, 1.0 / Engine.physics_ticks_per_second, mode), "Step rejected")

	return actor.position


## Keep numeric vectors machine-readable in the lean evidence JSON.
func _xyz(value: Vector3) -> Array[float]:
	return [value.x, value.y, value.z]
