extends SceneTree
## Validate saved gate components, static open/closed assemblies and full-kit clearance.

const ASSET := "city_barriers_07"
const PREFIX := "res://scenes/prefabs/environment/"
const FIXTURE := "res://tools/asset_production/city_barriers_07/check_scene.tscn"
const EVIDENCE := "res://docs/assets/production/city_barriers_07-evidence/validation.json"
const VARIANTS: Array[String] = ["left", "right", "mount"]
const BOUNDS: Array[AABB] = [
	AABB(Vector3(-.027, .1, -.11), Vector3(3.262, 2, .177)),
	AABB(Vector3(-3.1325, .1, -.09), Vector3(3.1595, 2, .157)),
	AABB(Vector3(-.162, .585, -.047), Vector3(.182, 1.03, .094)),
]
const SHAPE_SIZES: Array[Vector3] = [
	Vector3(3.262, 2.1, .177), Vector3(3.1595, 2.1, .157), Vector3(.182, 1.03, .094),
]
const SHAPE_POSITIONS: Array[Vector3] = [
	Vector3(1.604, 1.05, -.0215), Vector3(-1.55275, 1.05, -.0115), Vector3(-.071, 1.1, 0),
]
const WALK_TICKS := 48
const CLOSED_OFFSET_M := 8.0

var _failed := false
var _report: Dictionary = { "resource_uids": {}, "variants": {} }


## Wait for the tree before opening dependencies and testing physics.
func _initialize() -> void:
	_run.call_deferred()


## Normalize only owned scenes, check production APIs and retain an explicit receipt.
func _run() -> void:
	_require(Engine.get_version_info()["hash"].begins_with("c971f93e7"), "Engine pin")
	if "--normalize" in OS.get_cmdline_user_args():
		var paths: Array[String] = []
		for variant: String in VARIANTS:
			paths.append(_prefab(variant))
		paths.append(_prefab(""))
		paths.append(_prefab("closed"))
		paths.append(FIXTURE)
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
	print("CITY_BARRIERS_07_CHECK_PASS ", JSON.stringify(_report))
	quit(0)


## Resolve the default open assembly or a named component/static closed assembly.
func _prefab(variant: String) -> String:
	return PREFIX + ASSET + ("" if variant.is_empty() else "_" + variant) + ".tscn"


## Surface every failed assertion in both logs and process status.
func _require(condition: bool, message: String) -> void:
	if not condition:
		_failed = true
		push_error(message)


## Preserve saved scene-header UIDs rather than stale standalone-process cache identities.
func _save_scene(path: String) -> void:
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


## Recursively load actual dependencies and verify their registered saved resource identities.
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


## Compare imported geometry and each separate collider against independent literal envelopes.
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

	_check_collision(instance, index)
	_report["variants"][variant] = {
		"linked_model_identity": true,
		"bounds_min_m": [bounds.position.x, bounds.position.y, bounds.position.z],
		"bounds_size_m": [bounds.size.x, bounds.size.y, bounds.size.z],
		"static_body_count": 1, "simple_box_count": 1,
	}
	instance.free()


## Keep static collision separate from each linked visual component.
func _check_collision(instance: Node3D, index: int) -> void:
	var bodies: Array[Node] = instance.find_children("*", "CollisionObject3D", true, false)
	_require(bodies.size() == 1, "One static body per component")
	var body: StaticBody3D = instance.get_node("Collision/Body")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Static-world filtering")
	_require(body.get_child_count() == 1, "One simple shape per component")
	var node: CollisionShape3D = body.get_node("Shape")
	var shape: BoxShape3D = node.shape as BoxShape3D
	_require(shape.size.is_equal_approx(SHAPE_SIZES[index]), "Collider size")
	_require(node.position.is_equal_approx(SHAPE_POSITIONS[index]), "Collider centre")


## Check full-kit seams, static gate states, capsule contact and a vehicle-sized sweep.
func _check_physics() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	_check_assembly(fixture, space)
	var outcomes: Dictionary = {}
	for x: float in [-1.5, 0, 1.5]:
		var contact: Array[Vector3] = []
		var passage: Array[Vector3] = []
		for mode: ActorMotion.StepMode in [
			ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY,
		]:
			contact.append(await _walk(fixture.get_node("Actor"), x, CLOSED_OFFSET_M, mode))
			passage.append(await _walk(fixture.get_node("Actor"), x, 0, mode))
		_require(contact[0].z > 8.4 and contact[0].z < 8.45, "Closed gate not blocking")
		_require(abs(contact[0].y) < .015, "Capsule floor contact")
		_require(passage[0].distance_to(Vector3(x, 0, -2)) < .015, "Open passage blocked")
		_require(contact[0].is_equal_approx(contact[1]), "Closed authority/replay mismatch")
		_require(passage[0].is_equal_approx(passage[1]), "Open authority/replay mismatch")
		outcomes[str(x)] = {
			"closed_stop_m": [contact[0].x, contact[0].y, contact[0].z],
			"open_end_m": [passage[0].x, passage[0].y, passage[0].z],
		}
	_check_vehicle_envelope(space)
	_report["physics"] = {
		"authority_replay_equal": true, "capsule_radius_m": .35, "capsule_height_m": 1.8,
		"ticks_per_case_per_mode": WALK_TICKS, "outcomes": outcomes,
		"open_gate_clear_width_m": 6.166, "open_closed_and_above_rays_passed": true,
		"panel_post_and_closed_latch_seams_blocked": true,
		"vehicle_sized_sweep_open_clear_closed_blocked": true,
		"vehicle_controller_network_transport_and_placement": "not tested",
	}
	fixture.free()


## Check saved hinge/post/panel interfaces, not a runtime reconstruction of those placements.
func _check_assembly(fixture: Node3D, space: PhysicsDirectSpaceState3D) -> void:
	var gate: Node3D = fixture.get_node("Open")
	_check_open_width(gate)
	var left: Node3D = gate.get_node("LeftLeaf")
	var right: Node3D = gate.get_node("RightLeaf")
	_require(left.position.is_equal_approx(Vector3(-3.15, 0, 0)), "Left pivot")
	_require(right.position.is_equal_approx(Vector3(3.15, 0, 0)), "Right pivot")
	_require(left.to_global(Vector3(3, 0, 0)).distance_to(Vector3(-3.15, 0, -3)) < .001,
		"Left open angle")
	_require(right.to_global(Vector3(-3, 0, 0)).distance_to(Vector3(3.15, 0, -3)) < .001,
		"Right open angle")
	for name: String in ["LeftMount", "RightMount", "LeftPost", "RightPost"]:
		_require((gate.get_node(name) as Node3D).scale == Vector3.ONE, "Scaled hardware")
	var panel: Node3D = fixture.get_node("PanelRight")
	_require(panel.to_global(Vector3(-1.475, 1.1, 0)).distance_to(Vector3(3.34, 1.1, 0))
		< .00001, "Post clamp and panel frame mismatch")
	for x: float in [-3.265, -3.21, 3.21, 3.265, 3.32, 4.815, 6.365, 7.915, 9.465]:
		_require(_ray_hits(space, Vector3(x, .5, -1), Vector3(x, .5, 1)), "Kit seam gap")
	for x: float in [-3, -1.5, -.05, 0, .05, 1.5, 3]:
		_require(_ray_hits(space, Vector3(x, .5, 7), Vector3(x, .5, 9)), "Closed seam gap")
		_require(not _ray_hits(space, Vector3(x, 2.2, 7), Vector3(x, 2.2, 9)), "Above gate")
		_require(not _ray_hits(space, Vector3(x, .5, 1), Vector3(x, .5, -4)), "Open route")
	_require(_ray_hits(space, Vector3(2.8, .5, -1.5), Vector3(3.5, .5, -1.5)),
		"Open right leaf must still block")
	_require(_ray_hits(space, Vector3(-3.5, .5, -1.5), Vector3(-2.8, .5, -1.5)),
		"Open left leaf must still block")
	_require(_ray_hits(space, Vector3(-7, .5, -1.55), Vector3(-6, .5, -1.55)),
		"Corner return panel")


## Measure the real rotated leaf colliders instead of inferring an opening from render geometry.
func _check_open_width(gate: Node3D) -> void:
	var left: CollisionShape3D = gate.get_node("LeftLeaf/Collision/Body/Shape")
	var right: CollisionShape3D = gate.get_node("RightLeaf/Collision/Body/Shape")
	var left_size: Vector3 = (left.shape as BoxShape3D).size
	var right_size: Vector3 = (right.shape as BoxShape3D).size
	var left_bounds: AABB = left.global_transform * AABB(-left_size / 2, left_size)
	var right_bounds: AABB = right.global_transform * AABB(-right_size / 2, right_size)
	var width: float = right_bounds.position.x - left_bounds.end.x
	_require(abs(width - 6.166) < .001, "Wrong open gate clear width")
	_report["measured_open_clear_width_m"] = width


## Probe a conservative 2 by 1.5 by 4.5 m car box; this is not a vehicle-controller playtest.
func _check_vehicle_envelope(space: PhysicsDirectSpaceState3D) -> void:
	var shape := BoxShape3D.new()
	shape.size = Vector3(2, 1.5, 4.5)
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.collision_mask = 1
	query.transform = Transform3D(Basis.IDENTITY, Vector3(0, .9, 3))
	query.motion = Vector3(0, 0, -9)
	var open_sweep: PackedFloat32Array = space.cast_motion(query)
	_require(open_sweep[0] == 1.0, "Car-sized open sweep blocked")
	query.transform.origin.z = 11
	var closed_sweep: PackedFloat32Array = space.cast_motion(query)
	_require(closed_sweep[0] < .1, "Car-sized closed sweep did not stop")


## Query the actual static-world bodies without treating transparent wire as a filtering rule.
func _ray_hits(space: PhysicsDirectSpaceState3D, start: Vector3, end: Vector3) -> bool:
	return not space.intersect_ray(PhysicsRayQueryParameters3D.create(start, end, 1)).is_empty()


## Step the production actor through the open gate or into the separately saved closed one.
func _walk(actor: ActorMotion, x: float, z: float, mode: ActorMotion.StepMode) -> Vector3:
	actor.position = Vector3(x, .001, z + 2)
	actor.neutralize()
	actor.apply_floor_snap()
	for tick: int in WALK_TICKS:
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick + 1, tick, Vector2(0, -1), 0.0, false, false,
		)
		_require(actor.step(command, 1.0 / Engine.physics_ticks_per_second, mode), "Step rejected")

	return actor.position
