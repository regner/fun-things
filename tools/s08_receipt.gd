class_name S08Receipt
extends SceneTree
## Bounded exported-package observer; instances only the unchanged saved S01 scene.

const FIXTURES: String = "res://tests/fixtures/s01/"
const STATIC_MODEL: String = "res://art/models/spikes/s01_static.glb"
const RIG_MODEL: String = "res://art/models/spikes/s01_rig.glb"
const PETROL: String = "res://art/materials/s01_petrol.tres"
const CORAL: String = "res://art/materials/s01_coral.tres"
const PALETTE: String = "res://art/textures/spikes/s01_palette.png"
const ENGINE_HASH: String = "c971f93e7e76b0ef919bf6009e7b868bea04db7f"

var _failures: Array[String] = []
var _resources: Array[Dictionary] = []
var _checks: Array[String] = []


## Waits for the SceneTree before reading the packaged resources.
func _initialize() -> void:
	_observe.call_deferred()


## Resolves source identities, saved links and appearance through runtime APIs.
func _observe() -> void:
	var version: Dictionary = Engine.get_version_info()
	_check(version.hash == ENGINE_HASH, "exact runtime engine source")
	_check(version.major == 4 and version.minor == 8 and version.status == "dev7",
		"runtime engine version")
	_check(not ClassDB.class_exists("Steam"), "Steam class absent")
	_check(not Engine.has_singleton("Steam"), "Steam singleton absent")
	_check(not root.has_node("MCPRuntimeServer"), "MCP autoload absent")
	_check(not ProjectSettings.has_setting("autoload/MCPRuntimeServer"), "MCP setting absent")
	var inputs: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://s08_inputs.json"))
	if not inputs is Array:
		_check(false, "source input manifest readable")
		_finish(version)
		return

	for row: Dictionary in inputs:
		var path: String = "res://" + str(row.path)
		if path.ends_with(".uid") or path.ends_with(".import"):
			continue

		var resource: Resource = load(path)
		_check(resource != null, "load " + path)
		var observed: Dictionary = { "logical_path": path, "uid": row.uid }
		if resource != null:
			observed.resource_path = resource.resource_path
			observed.type = resource.get_class()
		observed.runtime_bytes = _representations(path)
		if not str(row.uid).is_empty():
			var identity: int = ResourceUID.text_to_id(str(row.uid))
			_check(ResourceUID.has_id(identity), "registered UID " + path)
			if ResourceUID.has_id(identity):
				observed.uid_path = ResourceUID.get_id_path(identity)
				_check(observed.uid_path == path, "UID/path agreement " + path)
				_check(load(str(row.uid)) == resource, "UID load identity " + path)
		_resources.append(observed)

	var packed: PackedScene = load(FIXTURES + "roundtrip.tscn") as PackedScene
	if packed == null:
		_check(false, "saved roundtrip loads")
		_finish(version)
		return

	var scene: Node = packed.instantiate()
	root.add_child(scene)
	await process_frame
	_saved_links(scene)
	scene.queue_free()
	await process_frame
	_finish(version)


## Reads packaged remap/import destinations and hashes the actually resolved payloads.
func _representations(path: String) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	var config: ConfigFile = ConfigFile.new()
	for suffix: String in ["", ".remap", ".import"]:
		var entry: String = path + suffix
		if not FileAccess.file_exists(entry):
			continue

		rows.append({ "path": entry, "sha256": FileAccess.get_sha256(entry),
			"bytes": FileAccess.get_file_as_bytes(entry).size() })
		if suffix.is_empty():
			continue

		config.clear()
		_check(config.load(entry) == OK, "packaged remap readable " + entry)
		for key: String in config.get_section_keys("remap"):
			if not key.begins_with("path"):
				continue

			var target: String = str(config.get_value("remap", key))
			_check(FileAccess.file_exists(target), "packaged payload exists " + target)
			rows.append({ "path": target, "sha256": FileAccess.get_sha256(target),
				"bytes": FileAccess.get_file_as_bytes(target).size() })
	return rows


## Checks repeated wrapper identities and linked imported meshes/materials/texture.
func _saved_links(scene: Node) -> void:
	var wrappers: Dictionary = {
		"StaticA": STATIC_MODEL, "StaticB": STATIC_MODEL, "Variant": STATIC_MODEL,
		"RigA": RIG_MODEL, "RigB": RIG_MODEL,
	}
	for name: String in wrappers:
		var wrapper: Node = scene.get_node_or_null(name)
		_check(wrapper != null, "saved wrapper " + name)
		if wrapper == null:
			return

		_check(wrapper.get("world_id") == StringName("s01/roundtrip/" + name.to_lower()),
			"saved world identity " + name)
		var model: Node = wrapper.get_node_or_null("Visuals/Model")
		_check(model != null, "saved Model " + name)
		if model == null:
			return

		_check(model.scene_file_path == wrappers[name], "GLB scene link " + name)

	var body: MeshInstance3D = scene.get_node("StaticA/Visuals/Model/Body")
	var repeat: MeshInstance3D = scene.get_node("StaticB/Visuals/Model/Body")
	var variant: MeshInstance3D = scene.get_node("Variant/Visuals/Model/Body")
	_check(body.mesh == repeat.mesh and body.mesh == variant.mesh, "static shared import mesh")
	var rig_a: MeshInstance3D = scene.get_node("RigA/Visuals/Model/Rig/Skeleton3D/Skin")
	_check(rig_a.mesh == scene.get_node("RigB/Visuals/Model/Rig/Skeleton3D/Skin").mesh,
		"rig shared import mesh")
	var material: StandardMaterial3D = body.mesh.surface_get_material(0)
	_check(material != null and material.resource_path == PETROL, "external petrol material")
	if material != null:
		_check(material.albedo_texture != null, "external palette texture")
		if material.albedo_texture != null:
			_check(material.albedo_texture.resource_path == PALETTE, "palette resource link")
			_check(material.albedo_texture.get_size() == Vector2(8, 8), "palette dimensions")
	_check(variant.material_override != null, "inherited coral override")
	if variant.material_override != null:
		_check(variant.material_override.resource_path == CORAL, "coral resource link")
	_check(body.material_override == null, "base appearance preserved")
	for name: String in ["entity", "local_rig"]:
		var packed: PackedScene = load("res://tests/fixtures/s03/" + name + ".tscn")
		_check(packed != null, "dynamic S03 scene " + name)
		if packed != null:
			var instance: Node = packed.instantiate()
			_check(instance != null, "dynamic S03 instance " + name)
			instance.free()


## Retains independent expectations without using release-disabled assertions.
func _check(condition: bool, contract: String) -> void:
	_checks.append(contract)
	if not condition:
		_failures.append(contract)


## Emits the complete machine-readable observation after freeing the saved scene.
func _finish(version: Dictionary) -> void:
	print("S08 " + JSON.stringify({
		"ok": _failures.is_empty(), "failures": _failures, "checks": _checks,
		"resources": _resources, "engine": version, "executable": OS.get_executable_path(),
		"executable_sha256": FileAccess.get_sha256(OS.get_executable_path()),
		"user_dir": OS.get_user_data_dir(),
	}))
	quit(0 if _failures.is_empty() else 1)
