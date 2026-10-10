extends SceneTree

const PREFAB: String = "res://scenes/prefabs/environment/d05_quay_paving_02.tscn"
const MODEL: String = (
	"res://art/models/environment/d05_quay_paving_02/d05_quay_paving_02.glb"
)
const MATERIAL: String = "res://art/materials/environment/d05_quay_paving_02/civic_inset.tres"
const SCRATCH: String = "C:/tmp/ft/assets/d05_quay_paving_02/"
const STARTUP_FRAMES: int = 10
const BOUNDS_TOLERANCE_M: float = 0.001

var _failures: Array[String] = []
var _receipt: Dictionary = {}


## Defer checks until the headless tree has completed startup.
func _initialize() -> void:
	_run.call_deferred()


## Accumulate failures and return a nonzero exit rather than relying on debug assertions.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Save only the owned wrapper, retaining the external GLB instance and its ancestry.
func _save_prefab() -> void:
	var packed := ResourceLoader.load(PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
	_expect(packed is PackedScene, "Prefab dependency load")
	if not packed is PackedScene:
		return

	var instance: Node = (packed as PackedScene).instantiate()
	var saved := PackedScene.new()
	_expect(saved.pack(instance) == OK, "Prefab pack")
	_expect(ResourceSaver.save(saved, PREFAB) == OK, "Prefab save")
	instance.free()


## Compare two fresh load/pack/save passes after the first UID-generating normalization.
func _normalize(material: StandardMaterial3D) -> void:
	_expect(Engine.is_editor_hint(), "Normalization requires headless editor mode")
	_expect(ResourceSaver.save(material, MATERIAL) == OK, "Material normalization")
	_save_prefab()
	var scene_hash := FileAccess.get_sha256(PREFAB)
	var material_hash := FileAccess.get_sha256(MATERIAL)
	for pass_index: int in range(2):
		_save_prefab()
		var fresh := ResourceLoader.load(
			MATERIAL, "StandardMaterial3D", ResourceLoader.CACHE_MODE_IGNORE
		)
		_expect(ResourceSaver.save(fresh, MATERIAL) == OK, "Material resave")
		_expect(FileAccess.get_sha256(PREFAB) == scene_hash, "Roundtrip scene bytes")
		_expect(FileAccess.get_sha256(MATERIAL) == material_hash, "Roundtrip material bytes")
		_receipt["roundtrip_%s_byte_stable" % (pass_index + 1)] = (
			FileAccess.get_sha256(PREFAB) == scene_hash
			and FileAccess.get_sha256(MATERIAL) == material_hash
		)


## Verify the external artwork material and imported mipmapped texture contract.
func _check_material(material: StandardMaterial3D) -> void:
	_expect(material.albedo_texture != null, "Missing artwork PNG dependency")
	if material.albedo_texture == null:
		return

	_expect(material.albedo_texture.get_size() == Vector2(960, 960), "Artwork texture size")
	var image: Image = material.albedo_texture.get_image()
	_expect(image.has_mipmaps(), "Generated mipmaps")
	_expect(image.get_format() == Image.FORMAT_RGB8, "Lossless RGB8 artwork import")
	_receipt["texture_image_bytes_including_mips"] = image.get_data().size()
	_receipt["texture_image_format"] = image.get_format()
	_expect(material.albedo_color == Color.WHITE, "No albedo colour multiplier")
	_expect(is_equal_approx(material.roughness, 0.94), "Matte inset roughness")
	_expect(material.metallic == 0 and not material.emission_enabled, "No metal or emission")
	_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque inset")
	_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Single upward-facing artwork")
	_expect(not material.texture_repeat, "Clamp atlas UV edges")
	_expect(
		material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS,
		"Linear mipmap filtering"
	)


## Independently inspect the compressed imported quad's positions, UVs and upward normals.
func _check_arrays(mesh: Mesh) -> void:
	var arrays: Array = mesh.surface_get_arrays(0)
	var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
	var uvs: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
	var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
	_expect(vertices.size() == 4 and indices.size() == 6, "Four vertices / two triangles")
	_expect(normals.size() == 4 and uvs.size() == 4, "Normals and UV0 for every vertex")
	if vertices.size() != 4 or normals.size() != 4 or uvs.size() != 4:
		return

	for index: int in range(vertices.size()):
		var point: Vector3 = vertices[index]
		_expect(absf(point.y - 0.015) < 0.001, "All artwork above supporting ground datum")
		_expect(normals[index].distance_to(Vector3.UP) < 0.001, "Unit upward normals")
		var expected_uv := Vector2((point.x + 3.0) / 6.0, (point.z + 3.0) / 6.0)
		_expect(uvs[index].distance_to(expected_uv) < 0.00005, "Imported UV0 orientation")

	_receipt["import_vertices"] = vertices.size()
	_receipt["import_triangles"] = indices.size() / 3
	_receipt["import_normals_uvs_valid"] = true


## Inspect actual imported resources and require an entirely collision-free linked wrapper.
func _inspect(instance: Node3D) -> void:
	var model: Node3D = instance.get_node("Visuals/Model") as Node3D
	_expect(model.scene_file_path == MODEL, "Linked GLB ancestry")
	_expect(model.transform == Transform3D.IDENTITY, "Identity model transform")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 1, "One imported mesh")
	if meshes.size() != 1:
		return

	var mesh := meshes[0] as MeshInstance3D
	_expect(mesh.transform == Transform3D.IDENTITY, "Identity imported mesh transform")
	_expect(mesh.mesh.resource_path.begins_with(MODEL), "Mesh remains GLB resource")
	_expect(mesh.mesh.get_surface_count() == 1, "One material surface")
	_check_arrays(mesh.mesh)
	_expect(mesh.material_override == null, "No mesh material override")
	_expect(mesh.get_surface_override_material(0) == null, "No editable child face override")
	var imported_material := mesh.mesh.surface_get_material(0)
	_expect(imported_material.resource_path == MATERIAL, "Import maps external artwork material")
	var bounds := mesh.get_aabb()
	_expect(
		bounds.position.distance_to(Vector3(-3, .015, -3)) < BOUNDS_TOLERANCE_M,
		"Source/import AABB minimum"
	)
	_expect(bounds.size.distance_to(Vector3(6, 0, 6)) < BOUNDS_TOLERANCE_M, "AABB size")
	_expect(
		instance.find_children("*", "CollisionObject3D", true, false).is_empty(),
		"Flush artwork must not introduce terrain collision"
	)
	_receipt.merge({
		"mesh_count": meshes.size(),
		"surface_count": mesh.mesh.get_surface_count(),
		"aabb_min": [bounds.position.x, bounds.position.y, bounds.position.z],
		"aabb_size": [bounds.size.x, bounds.size.y, bounds.size.z],
		"external_material": imported_material.resource_path,
		"linked_identity_model": true,
		"collision_objects": 0,
		"material_overrides": 0,
	})


## Load, optionally normalize, check all dependencies and write a fresh bounded receipt.
func _run() -> void:
	# Bounded startup delay lets the headless editor finish UID registration before saving.
	for frame_index: int in range(STARTUP_FRAMES):
		await process_frame  # gdstyle:ignore=quality/await-in-loop

	var version: Dictionary = Engine.get_version_info()
	_expect(version.string == "4.8-dev7 (official)", "Pinned engine version")
	_expect(str(version.hash).begins_with("c971f93e7"), "Pinned engine commit")
	var material := load(MATERIAL) as StandardMaterial3D
	_expect(material != null, "Material resource load")
	if material == null:
		quit(1)
		return

	_check_material(material)
	var normalize: bool = OS.get_cmdline_user_args().has("--normalize")
	if normalize:
		_normalize(material)

	var packed := ResourceLoader.load(PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
	_expect(packed is PackedScene, "Fresh prefab load")
	if not packed is PackedScene:
		quit(1)
		return

	var instance := (packed as PackedScene).instantiate() as Node3D
	_inspect(instance)
	instance.free()
	for path: String in [PREFAB, MODEL, MATERIAL, material.albedo_texture.resource_path]:
		var uid: int = ResourceLoader.get_resource_uid(path)
		_expect(uid != ResourceUID.INVALID_ID, "Registered resource UID: " + path)
		_receipt[path.get_file() + "_uid"] = ResourceUID.id_to_text(uid)

	_receipt["prefab_sha256"] = FileAccess.get_sha256(PREFAB)
	_receipt["material_sha256"] = FileAccess.get_sha256(MATERIAL)
	_receipt["engine"] = version.string
	_receipt["engine_hash"] = version.hash
	_receipt["texture_size"] = [960, 960]
	_receipt["mipmaps"] = true
	_receipt["failures"] = _failures
	_receipt["ok"] = _failures.is_empty()
	var name: String = "roundtrip.json" if normalize else "prefab-check.json"
	var file := FileAccess.open(SCRATCH + name, FileAccess.WRITE)
	file.store_string(JSON.stringify(_receipt, "\t") + "\n")
	file.close()
	print("QUAY_PREFAB_CHECK ", JSON.stringify(_receipt))
	quit(0 if _failures.is_empty() else 1)
