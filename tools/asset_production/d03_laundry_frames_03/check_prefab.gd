extends SceneTree

const PREFIX: String = "res://scenes/prefabs/environment/d03_laundry_frames_03_"
const MODEL_PREFIX: String = (
	"res://art/models/environment/d03_laundry_frames_03/d03_laundry_frames_03_"
)
const FIXTURE: String = "res://tools/asset_production/d03_laundry_frames_03/check_scene.tscn"
const OUTPUT: String = "C:/tmp/ft/assets/d03_laundry_frames_03/prefab-check.json"
const TOLERANCE_M: float = 0.001

var _failures: Array[String] = []
var _report: Dictionary = {}


## Defer resource checks until the isolated scene tree is ready.
func _initialize() -> void:
	_run.call_deferred()


## Retain failures in diagnostics and the machine-readable receipt.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Retain explicit dependency UIDs even when the headless runtime saver omits them.
func _write_dependency_uids(path: String) -> void:
	var lines := FileAccess.get_file_as_string(path).split("\n")
	for index: int in range(lines.size()):
		var line := lines[index]
		if not line.begins_with("[ext_resource"):
			continue

		var dependency := line.get_slice("path=\"", 1).get_slice("\"", 0)
		var uid := ResourceLoader.get_resource_uid(dependency)
		_expect(uid != ResourceUID.INVALID_ID, "Dependency identity: " + dependency)
		if not line.contains("uid=\""):
			lines[index] = line.replace(" path=", " uid=\"%s\" path=" % ResourceUID.id_to_text(uid))

	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string("\n".join(lines))


## Require serialized identities, not merely successful fallback-path loading.
func _check_saved_identities(path: String) -> void:
	var text := FileAccess.get_file_as_string(path)
	_expect(text.get_slice("
", 0).contains("uid=\""), "Header UID: " + path)
	var dependencies: Dictionary = {}
	for line: String in text.split("
"):
		if line.begins_with("[ext_resource"):
			var dependency := line.get_slice("path=\"", 1).get_slice("\"", 0)
			_expect(line.contains("uid=\""), "Serialized dependency UID: " + dependency)
			if not line.contains("uid=\""):
				continue

			var saved_uid := line.get_slice("uid=\"", 1).get_slice("\"", 0)
			var uid := ResourceUID.text_to_id(saved_uid)
			_expect(uid != ResourceUID.INVALID_ID, "Valid dependency UID: " + dependency)
			_expect(ResourceUID.has_id(uid), "Registered dependency UID: " + dependency)
			if ResourceUID.has_id(uid):
				_expect(ResourceUID.get_id_path(uid) == dependency, "UID path: " + dependency)

			_expect(
				ResourceLoader.get_resource_uid(dependency) == uid,
				"UID resolves: " + dependency,
			)
			dependencies[dependency] = saved_uid

		if line.begins_with("[node"):
			_expect(line.contains("unique_id="), "Saved node identity: " + path)

	_report.get_or_add("serialized_dependency_uids", {})[path] = dependencies


## Normalize authored scenes without unpacking linked imported geometry or changing UIDs.
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
	_expect(ResourceSaver.set_uid(path, uid) == OK, "Scene UID retained")
	_write_dependency_uids(path)
	_check_saved_identities(path)
	instance.free()


## Prove two byte-stable load/pack/save cycles after first normalization.
func _roundtrip() -> void:
	for path: String in [PREFIX + "sheet.tscn", PREFIX + "towel.tscn", FIXTURE]:
		_save_scene(path)
		var first: String = FileAccess.get_sha256(path)
		_save_scene(path)
		var second: String = FileAccess.get_sha256(path)
		_save_scene(path)
		var third: String = FileAccess.get_sha256(path)
		_expect(first == second and second == third, "Stable scene: " + path)
		_report[path] = {"sha256": third, "byte_stable": first == second and second == third,
			"stable_reload_count": 2}


## Recursively verify saved dependencies and their registered UIDs.
func _dependencies(path: String) -> void:
	_expect(ResourceLoader.load(path) != null, "Resource loads: " + path)
	var uid: int = ResourceLoader.get_resource_uid(path)
	_expect(uid != ResourceUID.INVALID_ID, "Resource UID: " + path)
	_expect(ResourceUID.has_id(uid), "UID registered: " + path)
	_expect(ResourceUID.get_id_path(uid) == path, "UID resolves: " + path)
	for dependency: String in ResourceLoader.get_dependencies(path):
		_dependencies(dependency.split("::")[-1])


## Check independent literal envelopes, source-backed meshes and visual-only cloth wrappers.
func _inspect_cloth(variant: String, expected: AABB) -> void:
	var path: String = PREFIX + variant + ".tscn"
	_dependencies(path)
	var instance: Node3D = (load(path) as PackedScene).instantiate() as Node3D
	var model: Node3D = instance.get_node("Visuals/Model") as Node3D
	_expect(model.scene_file_path == MODEL_PREFIX + variant + ".glb", "Linked cloth model")
	_expect(model.transform == Transform3D.IDENTITY, "Identity model transform")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 1, "One cloth mesh")
	var visual: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = visual.transform * visual.get_aabb()
	_expect(bounds.position.distance_to(expected.position) < TOLERANCE_M, "Cloth AABB minimum")
	_expect(bounds.end.distance_to(expected.end) < TOLERANCE_M, "Cloth AABB maximum")
	_expect(visual.mesh.resource_path.begins_with(MODEL_PREFIX), "Source-backed mesh")
	_expect(visual.mesh.get_surface_count() == 2, "Body and hem surfaces")
	for index: int in range(2):
		var material: BaseMaterial3D = visual.mesh.surface_get_material(index) as BaseMaterial3D
		_expect(material != null, "Material loads")
		_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque material")
		_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Backface culling")
		_expect(is_equal_approx(material.roughness, 0.88), "Rough cloth material")

	_expect(instance.find_children("*", "CollisionObject3D", true, false).is_empty(),
		"Soft hanging decoration adds no rigid collision")
	_report[variant] = {"bounds_min_m": [bounds.position.x, bounds.position.y, bounds.position.z],
		"bounds_size_m": [bounds.size.x, bounds.size.y, bounds.size.z],
		"mesh_count": 1, "surfaces": 2, "collision_objects": 0,
		"prefab_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(path)),
		"model_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(model.scene_file_path)),
		"linked_model_identity": true}
	instance.free()


## Check the saved carrier composition fits its literal mounting contract without new blockers.
func _inspect_mounting() -> void:
	_dependencies(FIXTURE)
	var instance: Node3D = (load(FIXTURE) as PackedScene).instantiate() as Node3D
	var sheet: Node3D = instance.get_node("Sheet") as Node3D
	var towel: Node3D = instance.get_node("Towel") as Node3D
	_expect(sheet.position.is_equal_approx(Vector3(-0.62, 2.18, -0.48)), "Sheet line datum")
	_expect(towel.position.is_equal_approx(Vector3(0.78, 2.18, -0.48)), "Towel line datum")
	_expect(
		sheet.basis == Basis.IDENTITY and towel.basis == Basis.IDENTITY,
		"No corrective rotation",
	)
	var bodies: Array[Node] = instance.find_children("*", "CollisionObject3D", true, false)
	_expect(bodies.size() == 1, "Only existing frame collision remains")
	_expect(bodies[0] == instance.get_node("Frame/Collision/FrameBody"), "Frame owns collision")
	_expect(instance.find_children("*", "CollisionShape3D", true, false).size() == 3,
		"Unchanged three-box frame collision")
	var sheet_mesh: MeshInstance3D = sheet.find_children("*", "MeshInstance3D", true, false)[0]
	var towel_mesh: MeshInstance3D = towel.find_children("*", "MeshInstance3D", true, false)[0]
	var sheet_bounds: AABB = sheet.transform * sheet_mesh.get_aabb()
	var towel_bounds: AABB = towel.transform * towel_mesh.get_aabb()
	var gap: float = towel_bounds.position.x - sheet_bounds.end.x
	_expect(sheet_bounds.position.x > -1.6 and towel_bounds.end.x < 1.6, "Usable frame span")
	_expect(gap > 0.30, "Broad gap separates the two cloth shapes")
	_expect(sheet_bounds.position.y > 1.13, "Cloth remains above ground")
	_expect(sheet_bounds.position.z > -0.66, "Cloth stays within frame outer depth")
	_expect(sheet_bounds.end.z < -0.30, "Cloth stays clear of the middle line")
	_report["mounting"] = {"sheet_position_m": [-0.62, 2.18, -0.48],
		"towel_position_m": [0.78, 2.18, -0.48], "cloth_gap_m": gap,
		"lowest_cloth_height_m": sheet_bounds.position.y, "existing_frame_bodies": 1,
		"existing_frame_shapes": 3, "new_collision_objects": 0}
	instance.free()


## Separate normalization from final imported-resource checks and record the exact engine pin.
func _run() -> void:
	if not OS.get_cmdline_user_args().has("--normalize"):
		for path: String in [PREFIX + "sheet.tscn", PREFIX + "towel.tscn", FIXTURE]:
			_check_saved_identities(path)

		if not _failures.is_empty():
			quit(1)
			return

	_expect(Engine.get_version_info()["hash"].begins_with("c971f93e7"), "Pinned engine")
	var normalize: bool = OS.get_cmdline_user_args().has("--normalize")
	if normalize:
		_roundtrip()
	else:
		_inspect_cloth("sheet", AABB(Vector3(-0.7101, -1.0404, -0.1719),
			Vector3(1.4202, 1.0645, 0.3433)))
		_inspect_cloth("towel", AABB(Vector3(-0.3801, -0.8005, -0.1558),
			Vector3(0.7602, 0.8246, 0.3112)))
		_inspect_mounting()
		var roundtrip: String = FileAccess.get_file_as_string(OUTPUT + ".roundtrip")
		_report["roundtrip"] = JSON.parse_string(roundtrip)
		_expect(_report["roundtrip"]["ok"], "Roundtrip receipt passes")

	_report["engine"] = Engine.get_version_info()["string"]
	_report["failures"] = _failures
	_report["ok"] = _failures.is_empty()
	var file: FileAccess = FileAccess.open(
		OUTPUT + (".roundtrip" if normalize else ""), FileAccess.WRITE,
	)
	file.store_string(JSON.stringify(_report, "\t") + "\n")
	file.close()
	print(JSON.stringify(_report))
	quit(0 if _failures.is_empty() else 1)
