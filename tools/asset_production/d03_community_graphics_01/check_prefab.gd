extends SceneTree
## Check the inherited noticeboard, face-only artwork, collision and stable saved identities.

const PREFAB := "res://scenes/prefabs/environment/d03_community_graphics_01.tscn"
const CARRIER := "res://scenes/prefabs/environment/city_sign_supports_03.tscn"
const GLB := "res://art/models/environment/city_sign_supports_03/city_sign_supports_03.glb"
const MATERIAL := "res://art/materials/environment/d03_community_graphics_01/community_board.tres"
const TEXTURE := (
	"res://art/textures/environment/d03_community_graphics_01/community_board_albedo.png"
)
const SCRATCH := "C:/tmp/ft/assets/d03_community_graphics_01/"

var _failures: Array[String] = []
var _result: Dictionary = {}
var _retained_material: Material


## Defer until the isolated resource system has initialized.
func _initialize() -> void:
	_run.call_deferred()


## Accumulate explicit diagnostics and return nonzero on any contract violation.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Preserve inline resource UIDs, allocating only on first normalization.
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


## Normalize only the artwork's own wrapper and material, never inherited hardware.
func _save_resources() -> void:
	var material_uid := _saved_uid(MATERIAL)
	var material := ResourceLoader.load(MATERIAL, "", ResourceLoader.CACHE_MODE_IGNORE)
	_expect(ResourceSaver.save(material, MATERIAL) == OK, "Material save")
	_expect(ResourceSaver.set_uid(MATERIAL, material_uid) == OK, "Material UID")
	var scene_uid := _saved_uid(PREFAB)
	var source := ResourceLoader.load(PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
	_expect(source != null, "Prefab source load")
	if source == null:
		return

	var instance := (source as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var packed := PackedScene.new()
	_expect(packed.pack(instance) == OK, "Prefab pack")
	_expect(ResourceSaver.save(packed, PREFAB) == OK, "Prefab save")
	_expect(ResourceSaver.set_uid(PREFAB, scene_uid) == OK, "Prefab UID")
	instance.free()


## Prove two complete save/reload passes preserve bytes, including node identities and UIDs.
func _roundtrip() -> void:
	var before := [FileAccess.get_sha256(PREFAB), FileAccess.get_sha256(MATERIAL)]
	_save_resources()
	var hashes := [FileAccess.get_sha256(PREFAB), FileAccess.get_sha256(MATERIAL)]
	if OS.get_cmdline_user_args().has("--verify-stable"):
		_expect(before == hashes, "Fresh-process initial bytes must remain stable")
		_result["fresh_process_initial_byte_stable"] = before == hashes
	for cycle: int in range(2):
		_save_resources()
		var stable := hashes == [FileAccess.get_sha256(PREFAB), FileAccess.get_sha256(MATERIAL)]
		_expect(stable, "Roundtrip drift: " + str(cycle))
		_result["roundtrip_%d_byte_stable" % (cycle + 1)] = stable
	_result["prefab_sha256"] = hashes[0]
	_result["material_sha256"] = hashes[1]


## Verify actual imported color texture, complete mips and quiet opaque ink settings.
func _check_material() -> void:
	var material := load(MATERIAL) as StandardMaterial3D
	_expect(material != null, "Material load")
	if material == null:
		return

	_retained_material = material
	_expect(material.albedo_texture != null, "Texture load")
	_expect(material.albedo_texture.get_size() == Vector2(1640, 1040), "41:26 dimensions")
	_expect(material.albedo_texture.resource_path == TEXTURE, "Texture dependency")
	_expect(material.albedo_color == Color.WHITE, "White albedo multiplier")
	_expect(is_equal_approx(material.roughness, 0.84), "Matte face")
	_expect(material.metallic == 0.0 and not material.emission_enabled, "Non-emissive ink")
	_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque ink")
	_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Back culling")
	_expect(not material.texture_repeat, "Clamp texture")
	_expect(
		material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS,
		"Linear mipmapped filtering"
	)
	var image := material.albedo_texture.get_image()
	_expect(image.has_mipmaps() and image.get_mipmap_count() == 10, "Actual full mip chain")
	_expect(image.get_format() == Image.FORMAT_RGB8, "Actual RGB8 color data")
	_result["texture_cpu_bytes_including_mips"] = image.get_data_size()
	_result["texture_mipmap_count"] = image.get_mipmap_count()
	var config := ConfigFile.new()
	_expect(config.load(TEXTURE + ".import") == OK, "Texture sidecar")
	_expect(config.get_value("params", "mipmaps/generate") == true, "Mip import")
	_expect(config.get_value("params", "compress/mode") == 0, "Lossless import")
	_expect(config.get_value("params", "detect_3d/compress_to") == 0, "No auto conversion")


## Compare every inherited surface and transform against the pristine hardware prefab.
func _check_visuals(instance: Node3D, reference: Node3D) -> void:
	var model := instance.get_node("Visuals/Model") as Node3D
	_expect(model.scene_file_path == GLB, "Linked Blender model")
	_expect(model.transform == Transform3D.IDENTITY, "Identity model")
	_expect((instance.get_node("Visuals") as Node3D).transform == Transform3D.IDENTITY, "Visuals")
	var meshes := model.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 2, "Two inherited meshes")
	var surfaces := 0
	var overrides := 0
	var bounds := AABB()
	for node: Node in meshes:
		var mesh := node as MeshInstance3D
		var original := reference.get_node(instance.get_path_to(mesh)) as MeshInstance3D
		_expect(mesh.mesh == original.mesh, "Unchanged imported mesh resource")
		_expect(mesh.transform == original.transform, "Unchanged mesh transform")
		_expect(mesh.material_override == null, "No whole-mesh override")
		bounds = mesh.get_aabb() if surfaces == 0 else bounds.merge(mesh.get_aabb())
		for surface: int in range(mesh.mesh.get_surface_count()):
			surfaces += 1
			var override := mesh.get_surface_override_material(surface)
			if mesh.name == "CitySignSupports03_ArtworkCarrier" and surface == 0:
				_expect(override == load(MATERIAL), "Artwork face material")
				_expect(
					mesh.mesh.surface_get_material(surface).resource_name == "sign_face",
					"Slot",
				)
				overrides += 1
			else:
				_expect(override == null, "No override on hardware or face sides/back")
	_expect(surfaces == 5 and overrides == 1, "Exactly one of five surfaces overridden")
	_expect(bounds.position.is_equal_approx(Vector3(-0.95, 0, -0.22)), "AABB minimum")
	_expect(bounds.size.is_equal_approx(Vector3(1.9, 2.1, 0.44)), "Original dimensions")
	_result["meshes"] = meshes.size()
	_result["surfaces"] = surfaces
	_result["face_overrides"] = overrides


## Retain the existing one-box freestanding collision without introducing a second owner.
func _check_collision(instance: Node3D, reference: Node3D) -> void:
	_expect(instance.find_children("*", "CollisionObject3D", true, false).size() == 1, "One body")
	_expect(instance.find_children("*", "CollisionShape3D", true, false).size() == 1, "One shape")
	var body := instance.get_node("Collision/Body") as StaticBody3D
	var shape := instance.get_node("Collision/Body/Shape") as CollisionShape3D
	var original := reference.get_node("Collision/Body/Shape") as CollisionShape3D
	_expect(body.collision_layer == 1 and body.collision_mask == 0, "Original filters")
	_expect(shape.shape == original.shape, "Inherited shape resource")
	_expect(shape.transform == original.transform and not shape.disabled, "Inherited transform")
	_expect((shape.shape as BoxShape3D).size == Vector3(1.9, 2.1, 0.44), "Box size")
	_expect(shape.position.is_equal_approx(Vector3(0, 1.05, 0)), "Box centre")
	_result["inherited_colliders"] = 1


## Resolve final dependencies and write a scratch receipt; no world/gameplay changes.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	if normalize:
		_roundtrip()

	_check_material()
	var instance := (load(PREFAB) as PackedScene).instantiate() as Node3D
	var reference := (load(CARRIER) as PackedScene).instantiate() as Node3D
	_expect(instance.transform == Transform3D.IDENTITY, "Identity root")
	_check_visuals(instance, reference)
	_check_collision(instance, reference)
	instance.free()
	reference.free()
	for path: String in [PREFAB, CARRIER, GLB, MATERIAL, TEXTURE]:
		var uid := ResourceLoader.get_resource_uid(path)
		_expect(uid != ResourceUID.INVALID_ID, "Dependency UID: " + path)
		_result[path] = ResourceUID.id_to_text(uid)
	_result["engine"] = Engine.get_version_info().string
	_result["failures"] = _failures
	_result["ok"] = _failures.is_empty()
	var output := SCRATCH + ("roundtrip.json" if normalize else "prefab-check.json")
	var file := FileAccess.open(output, FileAccess.WRITE)
	file.store_string(JSON.stringify(_result, "\t") + "\n")
	file.close()
	print("COMMUNITY_PREFAB_CHECK: ", JSON.stringify(_result))
	quit(0 if _failures.is_empty() else 1)
