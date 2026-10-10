extends SceneTree
## Check inherited container hardware, face-only art, collision retention and stable saved
## identities.

const DIRECTORY := "res://scenes/prefabs/environment/"
const MATERIALS := "res://art/materials/environment/d09_freight_graphics_02/"
const TEXTURES := "res://art/textures/environment/d09_freight_graphics_02/"
const SCRATCH := "C:/tmp/ft/assets/d09_freight_graphics_02/"
const VARIANTS := [
	{ "name": "long", "suffix": "", "carrier": "01", "length": 12.0 },
	{ "name": "short", "suffix": "_short", "carrier": "02", "length": 6.0 },
]

var _failures: Array[String] = []
var _result: Dictionary = {}
var _materials: Array[Material] = []


## Run after the isolated headless resource system has initialized.
func _initialize() -> void:
	_run.call_deferred()


## Accumulate diagnostics and exit nonzero on any unmet contract.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Preserve an existing inline UID, allocating only for newly authored resources.
func _saved_uid(path: String) -> int:
	var header := FileAccess.get_file_as_string(path).get_slice("\n", 0)
	var uid := ResourceUID.INVALID_ID
	if header.contains("uid=\""):
		uid = ResourceUID.text_to_id(header.get_slice("uid=\"", 1).get_slice("\"", 0))
	if uid == ResourceUID.INVALID_ID:
		uid = ResourceUID.create_id()
	if not ResourceUID.has_id(uid):
		ResourceUID.add_id(uid, path)
	return uid


## Save only the new artwork wrapper and material, never the inherited carrier.
func _save_resources(prefab: String, material_path: String) -> void:
	var material_uid := _saved_uid(material_path)
	var material := ResourceLoader.load(material_path, "", ResourceLoader.CACHE_MODE_IGNORE)
	_expect(ResourceSaver.save(material, material_path) == OK, "Material save")
	_expect(ResourceSaver.set_uid(material_path, material_uid) == OK, "Material UID")
	var scene_uid := _saved_uid(prefab)
	var source := ResourceLoader.load(
		prefab, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
	) as PackedScene
	_expect(source != null, "Prefab source load")
	if source == null:
		return

	var instance := source.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var packed := PackedScene.new()
	_expect(packed.pack(instance) == OK, "Prefab pack")
	_expect(ResourceSaver.save(packed, prefab) == OK, "Prefab save")
	_expect(ResourceSaver.set_uid(prefab, scene_uid) == OK, "Prefab UID")
	instance.free()


## Prove two save/reload cycles preserve complete bytes, including identities and UIDs.
func _roundtrip(prefab: String, material_path: String) -> Dictionary:
	var before := [FileAccess.get_sha256(prefab), FileAccess.get_sha256(material_path)]
	_save_resources(prefab, material_path)
	var hashes := [FileAccess.get_sha256(prefab), FileAccess.get_sha256(material_path)]
	if OS.get_cmdline_user_args().has("--verify-stable"):
		_expect(before == hashes, "Fresh-process initial bytes must remain stable")
	for cycle: int in range(2):
		_save_resources(prefab, material_path)
		_expect(FileAccess.get_sha256(prefab) == hashes[0], "Scene drift: " + str(cycle))
		_expect(FileAccess.get_sha256(material_path) == hashes[1], "Material drift: " + str(cycle))
	return { "stable_roundtrip_count": 2, "scene_sha256": hashes[0], "material_sha256": hashes[1] }


## Check the actual imported texture and non-emissive opaque ink settings.
func _check_material(material_path: String, texture_path: String) -> void:
	var material := load(material_path) as StandardMaterial3D
	_expect(material != null, "Material load")
	if material == null:
		return

	_expect(material.albedo_texture != null, "Texture load")
	_expect(material.albedo_texture.get_size() == Vector2(1400, 460), "Texture dimensions")
	_expect(material.albedo_texture.resource_path == texture_path, "Texture dependency")
	_expect(material.albedo_color == Color.WHITE, "White texture multiplier")
	_expect(is_equal_approx(material.roughness, 0.62), "Roughness")
	_expect(material.metallic == 0.0 and not material.emission_enabled, "Non-emissive ink")
	_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque ink")
	_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Back culling")
	_expect(not material.texture_repeat, "Clamp texture")
	_expect(
		material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS,
		"Linear mipmapped filtering"
	)
	var config := ConfigFile.new()
	_expect(config.load(texture_path + ".import") == OK, "Texture sidecar")
	_expect(config.get_value("params", "mipmaps/generate") == true, "Mipmaps")
	_expect(config.get_value("params", "compress/mode") == 0, "Lossless compression")
	_expect(config.get_value("params", "detect_3d/compress_to") == 0, "No automatic conversion")


## Compare the inherited mesh and each material surface to the pristine carrier prefab.
func _check_visuals(instance: Node3D, reference: Node3D, variant: Dictionary) -> void:
	var model := instance.get_node("Visuals/Model") as Node3D
	var carrier: String = "d09_storage_" + variant.carrier
	var model_path := "res://art/models/environment/%s/%s.glb" % [carrier, carrier]
	_expect(model.scene_file_path == model_path, "Linked Blender GLB")
	_expect(model.transform == Transform3D.IDENTITY, "Identity model transform")
	_expect((instance.get_node("Visuals") as Node3D).transform == Transform3D.IDENTITY, "Visuals")
	var meshes := model.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 1, "One imported mesh")
	for node: Node in meshes:
		var mesh := node as MeshInstance3D
		var original := reference.get_node(instance.get_path_to(mesh)) as MeshInstance3D
		_expect(mesh.mesh == original.mesh, "Unchanged imported mesh resource")
		_expect(mesh.transform == original.transform, "Unchanged mesh transform")
		_expect(mesh.material_override == null, "No whole-mesh override")
		_expect(mesh.mesh.get_surface_count() == 4, "Four imported surfaces")
		for surface: int in range(4):
			var override := mesh.get_surface_override_material(surface)
			if surface == 3:
				_expect(override == load(MATERIALS + "container_id_" + variant.name + ".tres"),
					"Artwork only on face")
				_expect(mesh.mesh.surface_get_material(surface).resource_name == "storage_id_face",
					"Original face slot")
			else:
				_expect(override == null, "No hardware surface override")
		var bounds := mesh.get_aabb()
		_expect(bounds.position.is_equal_approx(Vector3(-1.25, 0, -variant.length / 2)), "Bounds")
		_expect(bounds.size.is_equal_approx(Vector3(2.5, 2.6, variant.length)), "Dimensions")


## Retain the original one-box static collision, with no new collision owner or geometry.
func _check_collision(instance: Node3D, reference: Node3D, length_m: float) -> void:
	_expect(instance.find_children("*", "CollisionObject3D", true, false).size() == 1, "One body")
	_expect(instance.find_children("*", "CollisionShape3D", true, false).size() == 1, "One shape")
	var body := instance.get_node("Collision/Body") as StaticBody3D
	var shell := instance.get_node("Collision/Body/Shell") as CollisionShape3D
	var original := reference.get_node("Collision/Body/Shell") as CollisionShape3D
	_expect(body.collision_layer == 1 and body.collision_mask == 0, "Original collision filters")
	_expect(shell.shape == original.shape, "Inherited shape resource, not a duplicate")
	_expect(shell.transform == original.transform and not shell.disabled, "Inherited transform")
	_expect((shell.shape as BoxShape3D).size == Vector3(2.5, 2.6, length_m), "Box dimensions")
	_expect(shell.position.is_equal_approx(Vector3(0, 1.3, 0)), "Box centre")


## Check one complete inherited carrier without changing its geometry or physics owner.
func _check_variant(variant: Dictionary, normalize: bool) -> Dictionary:
	var prefab: String = DIRECTORY + "d09_freight_graphics_02" + variant.suffix + ".tscn"
	var carrier: String = DIRECTORY + "d09_storage_" + variant.carrier + ".tscn"
	var material_path: String = MATERIALS + "container_id_" + variant.name + ".tres"
	var texture_path: String = TEXTURES + "container_id_" + variant.name + "_albedo.png"
	var receipt: Dictionary = _roundtrip(prefab, material_path) if normalize else {}
	_check_material(material_path, texture_path)
	# Retain the ink resource until every temporary instance has completed destruction.
	_materials.append(load(material_path) as Material)
	var instance := (load(prefab) as PackedScene).instantiate() as Node3D
	var reference := (load(carrier) as PackedScene).instantiate() as Node3D
	_expect(instance.transform == Transform3D.IDENTITY, "Identity root")
	_check_visuals(instance, reference, variant)
	_check_collision(instance, reference, variant.length)
	instance.free()
	reference.free()
	for path: String in [prefab, carrier, material_path, texture_path]:
		var uid := ResourceLoader.get_resource_uid(path)
		_expect(uid != ResourceUID.INVALID_ID, "Dependency UID: " + path)
		receipt[path] = ResourceUID.id_to_text(uid)
	receipt.merge({ "meshes": 1, "surfaces": 4, "face_overrides": 1, "inherited_colliders": 1 })
	return receipt


## Validate both saved variants and all dependency UIDs, then emit a scratch receipt.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	for variant: Dictionary in VARIANTS:
		_result[variant.name] = _check_variant(variant, normalize)

	_result["engine"] = Engine.get_version_info().string
	_result["failures"] = _failures
	_result["status"] = "PASS" if _failures.is_empty() else "FAIL"
	var output := SCRATCH + ("normalize.json" if normalize else "prefab.json")
	var file := FileAccess.open(output, FileAccess.WRITE)
	file.store_string(JSON.stringify(_result, "\t") + "\n")
	file.close()
	print("CONTAINER_PREFAB_", _result.status, ": ", JSON.stringify(_result))
	quit(0 if _failures.is_empty() else 1)
