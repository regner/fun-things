extends SceneTree
## Check three source-linked supports and their fit to the unchanged panel prefab.

const ASSET := "city_barriers_06"
const PREFIX := "res://scenes/prefabs/environment/"
const FIXTURE := "res://tools/asset_production/city_barriers_06/check_scene.tscn"
const EVIDENCE := "res://docs/assets/production/city_barriers_06-evidence/validation.json"
const VARIANTS: Array[String] = ["line", "terminal", "corner"]
const BOUNDS: Array[AABB] = [
	AABB(Vector3(-.105, 0, -.048), Vector3(.21, 2.16, .096)),
	AABB(Vector3(-.048, 0, -.11), Vector3(.998, 2.16, .158)),
	AABB(Vector3(-.048, 0, -.95), Vector3(.998, 2.16, .998)),
]
const SHAPE_SIZES: Array[Vector3] = [
	Vector3(.21, 2.16, .21), Vector3(.95, 1.76, .09), Vector3(.09, 1.6, .95),
]
const SHAPE_POSITIONS: Array[Vector3] = [
	Vector3(0, 1.08, 0), Vector3(.475, .88, -.065), Vector3(.065, .8, -.475),
]
const WALK_TICKS := 48
const VARIANT_SPACING_M := 3.0

var _failed := false
var _report: Dictionary = { "resource_uids": {}, "variants": {} }


## Wait for the tree before opening resources or issuing physics queries.
func _initialize() -> void:
	_run.call_deferred()


## Check every saved wrapper and fixture; retain results only when all assertions pass.
func _run() -> void:
	_require(Engine.get_version_info()["hash"].begins_with("c971f93e7"), "Engine pin")
	if "--normalize" in OS.get_cmdline_user_args():
		var paths: Array[String] = [FIXTURE]
		for variant: String in VARIANTS:
			paths.append(_prefab(variant))
		for path: String in paths:
			_save_scene(path)
			var first: String = FileAccess.get_sha256(path)
			_save_scene(path)
			_require(first == FileAccess.get_sha256(path), "Save/reload drift: " + path)
		_report["save_reload_byte_stable"] = true

	_check_dependencies(FIXTURE)
	for index: int in VARIANTS.size():
		_check_model(index)
	await _check_physics()
	_require(_report.has("physics"), "Physics checks did not complete")
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
	print("CITY_BARRIERS_06_CHECK_PASS ", JSON.stringify(_report))
	quit(0)


## Resolve the default line wrapper and the two explicitly named braced variants.
func _prefab(variant: String) -> String:
	return PREFIX + ASSET + ("" if variant == "line" else "_" + variant) + ".tscn"


## Surface every failed assertion in the log and process result.
func _require(condition: bool, message: String) -> void:
	if not condition:
		_failed = true
		push_error(message)


## Pack the saved hierarchy without replacing imported linked children.
func _save_scene(path: String) -> void:
	# A standalone process may have a stale UID cache after an earlier headless save.
	# The committed scene header, not that cache, owns an existing scene's identity.
	var header: String = FileAccess.get_file_as_string(path).get_slice("\n", 0)
	var uid: int = ResourceUID.INVALID_ID
	if header.contains("uid=\""):
		uid = ResourceUID.text_to_id(header.get_slice("uid=\"", 1).get_slice("\"", 0))
	if uid == ResourceUID.INVALID_ID:
		uid = ResourceUID.create_id()
	if not ResourceUID.has_id(uid):
		ResourceUID.add_id(uid, path)

	var source: PackedScene = ResourceLoader.load(
		path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE,
	)
	var instance: Node = source.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var packed := PackedScene.new()
	_require(packed.pack(instance) == OK, "Pack failed")
	_require(ResourceSaver.save(packed, path) == OK, "Save failed")
	_require(ResourceSaver.set_uid(path, uid) == OK, "Scene UID save failed")
	instance.free()


## Recursively load dependencies and prove every scene/script/import UID resolves.
func _check_dependencies(path: String) -> void:
	if _report["resource_uids"].has(path):
		return

	_require(ResourceLoader.load(path) != null, "Missing dependency: " + path)
	var uid: int = ResourceLoader.get_resource_uid(path)
	_require(uid != ResourceUID.INVALID_ID, "No resource UID: " + path)
	_require(ResourceUID.has_id(uid), "Unregistered UID: " + path)
	_require(ResourceUID.get_id_path(uid) == path, "UID mismatch: " + path)
	_report["resource_uids"][path] = ResourceUID.id_to_text(uid)
	for dependency: String in ResourceLoader.get_dependencies(path):
		var parts: PackedStringArray = dependency.split("::")
		_check_dependencies(parts[-1])


## Assert imported bounds/materials and one minimal compound body per support.
func _check_model(index: int) -> void:
	var variant: String = VARIANTS[index]
	var packed: PackedScene = load(_prefab(variant))
	var instance: Node3D = packed.instantiate()
	var model: Node3D = instance.get_node("Visuals/Model")
	_require(model.transform == Transform3D.IDENTITY, "Corrective model transform")
	_require(model.scene_file_path == "res://art/models/environment/%s/%s_%s.glb" % [
		ASSET, ASSET, variant,
	], "Unlinked model")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_require(meshes.size() == 1, "Mesh count")
	var mesh: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = mesh.transform * mesh.mesh.get_aabb()
	_require(bounds.position.distance_to(BOUNDS[index].position) < .001, "Bounds minimum")
	_require(bounds.size.distance_to(BOUNDS[index].size) < .001, "Bounds size")
	_require(mesh.mesh.get_surface_count() == 3, "Surface count")
	for surface: int in mesh.mesh.get_surface_count():
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(surface)
		_require(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Transparency")
		_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Backface culling")

	_check_collision(instance, index + 1)
	_report["variants"][variant] = {
		"linked_model_identity": true,
		"bounds_min_m": [bounds.position.x, bounds.position.y, bounds.position.z],
		"bounds_size_m": [bounds.size.x, bounds.size.y, bounds.size.z],
		"static_body_count": 1, "simple_box_count": index + 1,
	}
	instance.free()


## Keep collision separate, static-world filtered and confined to thin support planes.
func _check_collision(instance: Node3D, count: int) -> void:
	var bodies: Array[Node] = instance.find_children("*", "CollisionObject3D", true, false)
	_require(bodies.size() == 1, "One static body required")
	var body: StaticBody3D = instance.get_node("Collision/PostBody")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Static-world filtering")
	var shapes: Array[Node] = body.find_children("*", "CollisionShape3D", true, false)
	_require(shapes.size() == count, "Compound shape count")
	for index: int in shapes.size():
		var node: CollisionShape3D = shapes[index] as CollisionShape3D
		var shape: BoxShape3D = node.shape as BoxShape3D
		_require(shape != null, "Expected simple box")
		_require(shape.size.is_equal_approx(SHAPE_SIZES[index]), "Collider envelope")
		_require(node.position.is_equal_approx(SHAPE_POSITIONS[index]), "Collider position")


## Test physical posts/braces, preserved corner void and supported panel seams.
func _check_physics() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	var outcomes: Dictionary = {}
	for index: int in VARIANTS.size():
		var x: float = index * VARIANT_SPACING_M
		_require(_ray_hits(space, Vector3(x, .5, -2), Vector3(x, .5, 2)), "Post ray missed")
		_require(not _ray_hits(space, Vector3(x, 2.2, -2), Vector3(x, 2.2, 2)), "Above cap")
		var contact: Array[Vector3] = []
		var bypass: Array[Vector3] = []
		for mode: ActorMotion.StepMode in [
			ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY,
		]:
			contact.append(await _walk(fixture.get_node("Actor"), x, mode))
			bypass.append(await _walk(fixture.get_node("Actor"), x - .8, mode))
		_require(contact[0].distance_to(Vector3(x, 0, .456)) < .015, "Wrong contact stop")
		_require(bypass[0].distance_to(Vector3(x - .8, 0, -2)) < .015, "Bypass blocked")
		_require(contact[0].is_equal_approx(contact[1]), "Contact authority/replay mismatch")
		_require(bypass[0].is_equal_approx(bypass[1]), "Bypass authority/replay mismatch")
		outcomes[VARIANTS[index]] = {
			"contact_stop_m": [contact[0].x, contact[0].y, contact[0].z],
			"bypass_end_m": [bypass[0].x, bypass[0].y, bypass[0].z],
		}
	_check_fit(space, fixture)
	_report["physics"] = {
		"authority_replay_equal": true, "capsule_radius_m": .35, "capsule_height_m": 1.8,
		"ticks_per_case_per_mode": WALK_TICKS, "outcomes": outcomes,
		"post_rays_blocked": true, "above_cap_rays_clear": true,
		"brace_rays_blocked": true, "corner_interior_clear": true,
		"panel_seams_blocked": true, "panel_frame_clamp_alignment": true,
		"vehicle_network_transport_and_placement": "not tested",
	}
	fixture.free()


## Check explicit installed panel locations and thin collision instead of a filled corner box.
func _check_fit(space: PhysicsDirectSpaceState3D, fixture: Node3D) -> void:
	_require(_ray_hits(space, Vector3(3.6, .5, -1), Vector3(3.6, .5, 1)), "Terminal brace")
	_require(_ray_hits(space, Vector3(5, .5, -.6), Vector3(7, .5, -.6)), "Corner return brace")
	_require(not _ray_hits(space, Vector3(6.55, .5, -.6), Vector3(6.85, .5, -.6)),
		"Corner interior filled by collider")
	for x: float in [-3.1, -3.05, -1.55, -.05, 0, .05, 1.55, 3.05, 3.1]:
		_require(_ray_hits(space, Vector3(x, .5, 5), Vector3(x, .5, 7)), "Straight seam gap")
	for offset: float in [.05, 1.55, 3.05]:
		_require(_ray_hits(space, Vector3(6 + offset, .5, 5), Vector3(6 + offset, .5, 7)),
			"Corner X seam gap")
		_require(_ray_hits(space, Vector3(5, .5, 6 - offset), Vector3(7, .5, 6 - offset)),
			"Corner Z seam gap")

	var panel: Node3D = fixture.get_node("Run/RightPanel")
	_require(panel.to_global(Vector3(-1.475, 1.1, 0)).distance_to(Vector3(.075, 1.1, 6))
		< .00001, "Panel frame does not align with line clamp")
	panel = fixture.get_node("CornerFit/PanelZ")
	_require(panel.to_global(Vector3(-1.475, 1.1, 0)).distance_to(Vector3(6, 1.1, 5.925))
		< .00001, "Panel frame does not align with corner clamp")


## Exercise the production physics query API with the authored static-world mask.
func _ray_hits(space: PhysicsDirectSpaceState3D, start: Vector3, end: Vector3) -> bool:
	return not space.intersect_ray(PhysicsRayQueryParameters3D.create(start, end, 1)).is_empty()


## Step the real production actor capsule toward the support and along a clear bypass.
func _walk(actor: ActorMotion, x: float, mode: ActorMotion.StepMode) -> Vector3:
	actor.position = Vector3(x, .001, 2)
	actor.neutralize()
	actor.apply_floor_snap()
	for tick: int in WALK_TICKS:
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick + 1, tick, Vector2(0, -1), 0.0, false, false,
		)
		_require(actor.step(command, 1.0 / Engine.physics_ticks_per_second, mode), "Step rejected")

	return actor.position
