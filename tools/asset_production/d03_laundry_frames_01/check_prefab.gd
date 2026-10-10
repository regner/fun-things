extends SceneTree

const PREFAB: String = "res://scenes/prefabs/environment/d03_laundry_frames_01.tscn"
const MODEL: String = "res://art/models/environment/d03_laundry_frames_01/d03_laundry_frames_01.glb"
const FIXTURE: String = "res://tools/asset_production/d03_laundry_frames_01/check_scene.tscn"
const OUTPUT: String = "C:/tmp/ft/assets/d03_laundry_frames_01/prefab-check.json"
const EXPECTED: AABB = AABB(Vector3(-1.95, 0, -0.66), Vector3(3.9, 2.24, 1.32))
const TOLERANCE_M: float = 0.001
const WALK_TICKS: int = 48

var _failures: Array[String] = []
var _report: Dictionary = {}


## Defer checks until resources and the isolated scene tree are ready.
func _initialize() -> void:
	_run.call_deferred()


## Preserve failed expectations in both diagnostics and the final receipt.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Pack linked instances without copying imported geometry into the owned wrapper.
func _save_scene(path: String) -> void:
	var uid: int = ResourceLoader.get_resource_uid(path)
	if uid == ResourceUID.INVALID_ID:
		uid = ResourceUID.create_id()
		ResourceUID.add_id(uid, path)

	var source: PackedScene = ResourceLoader.load(
		path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
	) as PackedScene
	_expect(source != null, "Dependencies load: " + path)
	if source == null:
		return

	var instance: Node = source.instantiate()
	var packed: PackedScene = PackedScene.new()
	_expect(packed.pack(instance) == OK, "Scene packs")
	_expect(ResourceSaver.save(packed, path) == OK, "Scene saves")
	_expect(ResourceSaver.set_uid(path, uid) == OK, "Scene UID preserved")
	instance.free()


## Normalize new scene identities then prove two byte-stable reload/save cycles.
func _roundtrip() -> void:
	for path: String in [PREFAB, FIXTURE]:
		_save_scene(path)
		var first: String = FileAccess.get_sha256(path)
		_save_scene(path)
		var second: String = FileAccess.get_sha256(path)
		_save_scene(path)
		var third: String = FileAccess.get_sha256(path)
		_expect(first == second and second == third, "Stable roundtrip: " + path)
		_report[path] = {"sha256": third, "byte_stable": first == second and second == third,
			"stable_reload_count": 2}


## Recursively require all saved dependencies and resource UIDs to resolve.
func _dependencies(path: String) -> void:
	_expect(ResourceLoader.load(path) != null, "Resource loads: " + path)
	var uid: int = ResourceLoader.get_resource_uid(path)
	_expect(uid != ResourceUID.INVALID_ID, "Resource UID: " + path)
	_expect(ResourceUID.has_id(uid), "UID registered: " + path)
	_expect(ResourceUID.get_id_path(uid) == path, "UID maps to path: " + path)
	for dependency: String in ResourceLoader.get_dependencies(path):
		var parts: PackedStringArray = dependency.split("::")
		_dependencies(parts[-1])


## Verify actual imported bounds, opaque materials and intentional three-box collision.
func _inspect() -> void:
	_dependencies(PREFAB)
	var instance: Node3D = (load(PREFAB) as PackedScene).instantiate() as Node3D
	var model: Node3D = instance.get_node("Visuals/Model") as Node3D
	_expect(model.scene_file_path == MODEL, "Linked imported instance")
	_expect(model.transform == Transform3D.IDENTITY, "Identity model transform")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 1, "One mesh")
	var visual: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = visual.transform * visual.get_aabb()
	_expect(bounds.position.distance_to(EXPECTED.position) < TOLERANCE_M, "AABB minimum")
	_expect(bounds.size.distance_to(EXPECTED.size) < TOLERANCE_M, "AABB dimensions")
	_expect(visual.mesh.resource_path.begins_with(MODEL), "Source-backed mesh resource")
	_expect(visual.mesh.get_surface_count() == 3, "Three surfaces")
	for index: int in range(3):
		var material: BaseMaterial3D = visual.mesh.surface_get_material(index) as BaseMaterial3D
		_expect(material != null, "Material dependency")
		_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque material")
		_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Backface culling")

	var bodies: Array[Node] = instance.find_children("*", "CollisionObject3D", true, false)
	_expect(bodies.size() == 1, "One static body")
	var body: StaticBody3D = instance.get_node("Collision/FrameBody") as StaticBody3D
	_expect(body.collision_layer == 1 and body.collision_mask == 0, "Static world filtering")
	_expect(body.get_child_count() == 3, "Three shape compound")
	_check_box(body, "WestPost", Vector3(-1.8, 1.04, 0), Vector3(0.3, 2.08, 0.3))
	_check_box(body, "EastPost", Vector3(1.8, 1.04, 0), Vector3(0.3, 2.08, 0.3))
	_check_box(body, "TopEnvelope", Vector3(0, 2.16, 0), Vector3(3.784, 0.16, 1.32))
	_report["bounds_min_m"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_report["bounds_size_m"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_report["linked_model_identity"] = true
	_report["collision"] = {"body_count": 1, "box_count": 3, "layer": 1, "mask": 0,
		"headroom_m": 2.08, "post_clear_span_m": 3.3}
	_report["prefab_uid"] = ResourceUID.id_to_text(ResourceLoader.get_resource_uid(PREFAB))
	_report["model_uid"] = ResourceUID.id_to_text(ResourceLoader.get_resource_uid(MODEL))
	instance.free()


## Check literal collider dimensions independently of the scene authoring recipe.
func _check_box(body: Node, child: String, position_m: Vector3, size_m: Vector3) -> void:
	var node: CollisionShape3D = body.get_node(child) as CollisionShape3D
	var box: BoxShape3D = node.shape as BoxShape3D
	_expect(box != null, "Box collider: " + child)
	_expect(node.position.is_equal_approx(position_m), "Collider centre: " + child)
	_expect(box.size.is_equal_approx(size_m), "Collider size: " + child)


## Verify physical post contact, under-frame passage and clear exterior bypass through ActorMotion.
func _physics() -> void:
	var fixture: Node3D = (load(FIXTURE) as PackedScene).instantiate() as Node3D
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	for x: float in [-1.8, 1.8]:
		_expect(_ray_hits(space, Vector3(x, 1, -2), Vector3(x, 1, 2)), "Post ray blocked")

	_expect(not _ray_hits(space, Vector3(0, 1.8, -2), Vector3(0, 1.8, 2)), "Headroom clear")
	_expect(_ray_hits(space, Vector3(0, 2.16, -2), Vector3(0, 2.16, 2)), "Top envelope hit")
	_expect(not _ray_hits(space, Vector3(0, 2.3, -2), Vector3(0, 2.3, 2)), "Above top clear")
	var results: Array[Vector3] = []
	for mode: ActorMotion.StepMode in [ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY]:
		for x: float in [-1.8, 1.8, 0, 2.5]:
			results.append(await _walk(fixture.get_node("Actor") as ActorMotion, x, mode))

	for index: int in range(4):
		_expect(results[index].is_equal_approx(results[index + 4]), "Authority/replay equivalence")

	_expect(results[0].distance_to(Vector3(-1.8, 0, -0.5)) < 0.015, "West post contact")
	_expect(results[1].distance_to(Vector3(1.8, 0, -0.5)) < 0.015, "East post contact")
	_expect(results[2].distance_to(Vector3(0, 0, 2)) < 0.015, "Under-frame passage")
	_expect(results[3].distance_to(Vector3(2.5, 0, 2)) < 0.015, "Outside bypass")
	_report["physics"] = {"actor_radius_m": 0.35, "actor_height_m": 1.8,
		"ticks_per_case": WALK_TICKS, "authority_replay_equal": true,
		"west_contact": var_to_str(results[0]), "east_contact": var_to_str(results[1]),
		"under_frame": var_to_str(results[2]), "outside_bypass": var_to_str(results[3]),
		"post_top_headroom_rays_pass": true}
	fixture.free()


## Query only static-world geometry so the test actor never supplies a false positive.
func _ray_hits(space: PhysicsDirectSpaceState3D, start: Vector3, end: Vector3) -> bool:
	return not space.intersect_ray(PhysicsRayQueryParameters3D.create(start, end, 1)).is_empty()


## Replay the same valid production commands against the saved capsule and flat test floor.
func _walk(actor: ActorMotion, x: float, mode: ActorMotion.StepMode) -> Vector3:
	actor.position = Vector3(x, 0.001, -2)
	actor.neutralize()
	actor.apply_floor_snap()
	for tick: int in range(WALK_TICKS):
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick + 1, tick, Vector2(0, 1), 0.0, false, false,
		)
		_expect(
			actor.step(command, 1.0 / Engine.physics_ticks_per_second, mode),
			"Command accepted",
		)

	return actor.position


## Separate headless UID-preserving normalization from runtime resource and physics checks.
func _run() -> void:
	_expect(Engine.get_version_info()["hash"].begins_with("c971f93e7"), "Pinned engine")
	var normalize: bool = OS.get_cmdline_user_args().has("--normalize")
	if normalize:
		_roundtrip()
	else:
		_inspect()
		await _physics()
		var roundtrip: String = FileAccess.get_file_as_string(OUTPUT + ".roundtrip")
		_report["roundtrip"] = JSON.parse_string(roundtrip)
		_expect(_report["roundtrip"]["ok"], "Roundtrip receipt passes")

	_report["engine"] = Engine.get_version_info()["string"]
	_report["failures"] = _failures
	_report["ok"] = _failures.is_empty()
	var file: FileAccess = FileAccess.open(
		OUTPUT + (".roundtrip" if normalize else ""),
		FileAccess.WRITE,
	)
	file.store_string(JSON.stringify(_report, "\t") + "\n")
	file.close()
	print(JSON.stringify(_report))
	quit(0 if _failures.is_empty() else 1)
