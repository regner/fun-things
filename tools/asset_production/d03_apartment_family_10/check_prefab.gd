@tool
extends SceneTree

const NID: String = "d03_apartment_family_10"
const OUTPUT: String = "C:/tmp/ft/assets/d03_apartment_family_10/prefab-check.json"
const STRAIGHT: String = "res://scenes/prefabs/environment/d03_apartment_family_05.tscn"
const VARIANTS: Array[String] = ["straight", "end", "outside", "inside"]
const BOUNDS: Array[AABB] = [
	AABB(Vector3(-3, 3.2, -6), Vector3(6, 0.32, 12)),
	AABB(Vector3(-0.12, 3.2, -6), Vector3(0.24, 0.32, 12)),
	AABB(Vector3(-6, 3.2, -6), Vector3(12, 0.32, 12)),
	AABB(Vector3(-9, 3.2, -9), Vector3(18, 0.32, 18)),
]
const TOLERANCE_M: float = 0.001
const EDITOR_STARTUP_SECONDS: float = 3.0

var _failures: Array[String] = []
var _result: Dictionary = {}


## Defer resource checks until the isolated headless tree is ready.
func _initialize() -> void:
	_run.call_deferred()


## Preserve every failed expectation in both logs and the final receipt.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Return the owned wrapper path for one explicit variant.
func _prefab_path(variant: String) -> String:
	return "res://scenes/prefabs/environment/%s_%s.tscn" % [NID, variant]


## Return the explicitly linked export, not an embedded mesh resource.
func _model_path(variant: String) -> String:
	return "res://art/models/environment/%s/%s_%s.glb" % [NID, NID, variant]


## Pack and save only the requested owned wrapper using the headless editor.
func _save_wrapper(path: String) -> void:
	var scene: PackedScene = ResourceLoader.load(
		path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
	) as PackedScene
	_expect(scene != null, "Dependencies load: " + path)
	if scene == null:
		return

	var instance: Node = scene.instantiate()
	var packed: PackedScene = PackedScene.new()
	_expect(packed.pack(instance) == OK, "Pack: " + path)
	_expect(ResourceSaver.save(packed, path) == OK, "Save: " + path)
	instance.free()


## Require two subsequent reload/save cycles to preserve bytes and all serialized identities.
func _roundtrip(variant: String) -> void:
	var path: String = _prefab_path(variant)
	_save_wrapper(path)
	var expected: String = FileAccess.get_sha256(path)
	_save_wrapper(path)
	var second: String = FileAccess.get_sha256(path)
	_save_wrapper(path)
	var third: String = FileAccess.get_sha256(path)
	_expect(expected == second and second == third, "Stable reloads: " + variant)
	_result[variant] = {
		"normalized_sha256": expected, "byte_stable": expected == second and second == third,
		"stable_reload_count": 2,
	}


## Check imported material identity against the existing sibling and the roof-specific swatch.
func _materials(mesh: Mesh, variant: String) -> void:
	var sibling: Node = (load(STRAIGHT) as PackedScene).instantiate()
	var original: MeshInstance3D = sibling.get_node("Visuals/Model").find_children(
		"*", "MeshInstance3D", true, false)[0] as MeshInstance3D
	var count: int = 2 if variant == "end" else 3
	_expect(mesh.get_surface_count() == count, "Surface count: " + variant)
	for index: int in range(count):
		var material: BaseMaterial3D = mesh.surface_get_material(index) as BaseMaterial3D
		_expect(material != null, "Material dependency")
		_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque material")
		_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Backface culling")
		if index < 2:
			var reference: BaseMaterial3D = (
				original.mesh.surface_get_material(index) as BaseMaterial3D
			)
			_expect(material.resource_name == reference.resource_name, "Family material name")
			_expect(material.albedo_color == reference.albedo_color, "Family color")
			_expect(material.roughness == reference.roughness, "Family roughness")
			_expect(material.metallic == reference.metallic, "Family metallic")
		else:
			_expect(material.resource_name == "terrace_bluegrey_roof", "Roof surface name")
			_expect(material.albedo_color.is_equal_approx(Color("526b7b")), "Roof sRGB swatch")
			_expect(is_equal_approx(material.roughness, 0.8), "Roof roughness")

	sibling.free()


## Verify linked resources, exact bounds, mounted datum and absence of gameplay collision.
func _inspect(variant: String, expected: AABB) -> void:
	var path: String = _prefab_path(variant)
	var scene: PackedScene = load(path) as PackedScene
	_expect(scene != null, "Prefab loads: " + variant)
	if scene == null:
		return

	var instance: Node3D = scene.instantiate() as Node3D
	root.add_child(instance)
	var model: Node3D = instance.get_node("Visuals/Model") as Node3D
	_expect(model.scene_file_path == _model_path(variant), "Linked model: " + variant)
	_expect(model.transform == Transform3D.IDENTITY, "Model identity: " + variant)
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 1, "Single mesh: " + variant)
	var visual: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = visual.global_transform * visual.get_aabb()
	_expect(bounds.position.distance_to(expected.position) < TOLERANCE_M, "Minimum bounds")
	_expect(bounds.size.distance_to(expected.size) < TOLERANCE_M, "Size bounds")
	_expect(bounds.position.y > 2.5, "Entire roof is above overhead-only threshold")
	_expect(visual.mesh.resource_path.begins_with(_model_path(variant)), "Mesh linkage")
	_expect(instance.find_children("*", "CollisionObject3D", true, false).is_empty(),
		"No roof gameplay body")
	_expect(instance.find_children("*", "CollisionShape3D", true, false).is_empty(),
		"No walkable roof or guard collider")
	_materials(visual.mesh, variant)
	_mounting_datum(variant, bounds)
	_record_instance(variant, bounds)
	instance.free()


## Compare the cap footprint and underside to the actual sibling structural collider bounds.
func _mounting_datum(variant: String, roof_bounds: AABB) -> void:
	var host_path: String = STRAIGHT
	if variant == "end":
		host_path = "res://scenes/prefabs/environment/d03_apartment_family_07.tscn"
	elif variant in ["outside", "inside"]:
		host_path = "res://scenes/prefabs/environment/d03_apartment_family_06_%s.tscn" % variant

	var host: Node3D = (load(host_path) as PackedScene).instantiate() as Node3D
	root.add_child(host)
	var shapes: Array[Node] = host.find_children("*", "CollisionShape3D", true, false)
	var bounds: AABB
	for index: int in range(shapes.size()):
		var shape: CollisionShape3D = shapes[index] as CollisionShape3D
		var box: BoxShape3D = shape.shape as BoxShape3D
		_expect(box != null, "Expected sibling structural box")
		var part: AABB = shape.global_transform * AABB(-box.size / 2.0, box.size)
		bounds = part if index == 0 else bounds.merge(part)

	_expect(absf(bounds.end.y - roof_bounds.position.y) < TOLERANCE_M, "Roof seats on host")
	_expect(absf(bounds.position.x - roof_bounds.position.x) < TOLERANCE_M, "Host west extent")
	_expect(absf(bounds.position.z - roof_bounds.position.z) < TOLERANCE_M, "Host north extent")
	_expect(absf(bounds.end.x - roof_bounds.end.x) < TOLERANCE_M, "Host east extent")
	_expect(absf(bounds.end.z - roof_bounds.end.z) < TOLERANCE_M, "Host south extent")
	host.free()


## Retain actual imported bounds and resolved source/prefab UIDs.
func _record_instance(variant: String, bounds: AABB) -> void:
	var prefab_uid: int = ResourceLoader.get_resource_uid(_prefab_path(variant))
	var model_uid: int = ResourceLoader.get_resource_uid(_model_path(variant))
	_expect(prefab_uid != ResourceUID.INVALID_ID, "Prefab UID resolves")
	_expect(model_uid != ResourceUID.INVALID_ID, "Model UID resolves")
	_result[variant] = {
		"aabb_min": [bounds.position.x, bounds.position.y, bounds.position.z],
		"aabb_size": [bounds.size.x, bounds.size.y, bounds.size.z],
		"prefab_uid": ResourceUID.id_to_text(prefab_uid),
		"model_uid": ResourceUID.id_to_text(model_uid),
		"minimum_underside_m": bounds.position.y, "collision_shape_count": 0,
		"linked_model_identity": true, "family_materials_match": true,
		"actual_host_footprint_and_roof_seat_match": true,
	}


## Wait for scans before saving resource identities or exiting the isolated editor.
func _wait_for_scan() -> void:
	if not Engine.is_editor_hint():
		return

	await create_timer(EDITOR_STARTUP_SECONDS).timeout
	while EditorInterface.get_resource_filesystem().is_scanning():
		# The outer CLI timeout bounds this intentional scan polling.
		await create_timer(1.0).timeout  # gdstyle:ignore=quality/await-in-loop


## Separate editor normalization from clean runtime dependency/bounds inspection.
func _run() -> void:
	await _wait_for_scan()
	var normalize: bool = OS.get_cmdline_user_args().has("--normalize")
	if normalize and not Engine.is_editor_hint():
		push_error("Normalization requires --editor to preserve UIDs")
		quit(1)
		return

	for index: int in range(VARIANTS.size()):
		if normalize:
			_roundtrip(VARIANTS[index])
		else:
			_inspect(VARIANTS[index], BOUNDS[index])

	if not normalize:
		_result["roundtrip"] = JSON.parse_string(
			FileAccess.get_file_as_string(OUTPUT + ".roundtrip")
		)

	_result["engine"] = Engine.get_version_info()["string"]
	_result["failures"] = _failures
	_result["ok"] = _failures.is_empty()
	var output_path: String = OUTPUT + ".roundtrip" if normalize else OUTPUT
	var file: FileAccess = FileAccess.open(output_path, FileAccess.WRITE)
	file.store_string(JSON.stringify(_result, "\t") + "\n")
	file.close()
	print(JSON.stringify(_result))
	await _wait_for_scan()
	quit(0 if _failures.is_empty() else 1)
