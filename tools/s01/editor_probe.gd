@tool
class_name S01EditorProbe
extends Node
## Editor-only probe for toolkit operations unavailable on this session's tool surface.


## Instantiates a linked import or prefab through the toolkit's editor command.
func instance(parameters: Dictionary) -> Dictionary:
	var commands: GDScript = _scene_commands()
	return commands._cmd_scene_instantiate(self, parameters)


## Adds an imported GLB as a linked editor instance; toolkit rejects GLB paths.
func model(path: String, parent_path: String) -> void:
	var packed: PackedScene = load(path)
	var model_root: Node = packed.instantiate()
	var edited: Node = EditorInterface.get_edited_scene_root()
	model_root.name = "Model"
	edited.get_node(parent_path).add_child(model_root)
	model_root.owner = edited
	EditorInterface.mark_scene_as_unsaved()


## Enables recorded overrides on linked imported children.
func editable_model(enabled: bool = true) -> void:
	var edited: Node = EditorInterface.get_edited_scene_root()
	edited.set_editable_instance(edited.get_node("Visuals/Model"), enabled)


## Creates a variant through the toolkit's inheritance command.
func inherited(parameters: Dictionary) -> Dictionary:
	var commands: GDScript = _scene_commands()
	return await commands._cmd_create_inherited(parameters)


## Writes an external resource through the toolkit resource command.
func resource(parameters: Dictionary) -> Dictionary:
	var commands: GDScript = load("res://addons/godot_mcp_toolkit/commands/resource_commands.gd")
	return await commands._cmd_resource_write({"file_path": parameters.file_path,
		"type": parameters.class_name, "properties": JSON.parse_string(parameters.properties)})


## Reloads saved state even when the scene already has an open editor tab.
func reopen(path: String) -> Dictionary:
	var commands: GDScript = _scene_commands()
	return await commands._cmd_scene_close({ "file_path": path })


## Refreshes external exports; callers must reopen affected scenes separately.
func refresh() -> void:
	EditorInterface.get_resource_filesystem().scan()


## Saves explicit material remaps and animation loop modes before editor reimport.
func configure_import(path: String) -> Error:
	var options: ConfigFile = ConfigFile.new()
	var error: Error = options.load(path + ".import")
	if error != OK:
		return error

	var animations: Dictionary = {}
	if path.ends_with("s01_rig.glb"):
		for clip: String in ["idle", "walk", "run"]:
			animations[clip] = { "settings/loop_mode": Animation.LOOP_LINEAR }
		animations["death"] = { "settings/loop_mode": Animation.LOOP_NONE }
	options.set_value("params", "_subresources", {
		"materials": {"body_paint": {
			"use_external/enabled": true,
			"use_external/path": "res://art/materials/s01_petrol.tres"}},
		"animations": animations})
	options.set_value("params", "meshes/generate_lods", false)
	options.set_value("params", "animation/remove_immutable_tracks", false)
	error = options.save(path + ".import")
	if error == OK:
		reimport(path)
	return error


## Reimports outside the MCP deferred-dispatch queue to avoid progress-dialog errors.
func reimport(path: String) -> void:
	_reimport_on_frame.bind(path).call_deferred()


## Waits for a normal process frame before showing the engine's reimport progress.
func _reimport_on_frame(path: String) -> void:
	await get_tree().process_frame
	EditorInterface.get_resource_filesystem().reimport_files(PackedStringArray([path]))


## Inspects a packed source without editing or copying its mesh data.
func inspect_scene(path: String) -> Array[Dictionary]:
	var packed: PackedScene = load(path)
	var instance_root: Node = packed.instantiate()
	var rows: Array[Dictionary] = []
	_inspect_node(instance_root, instance_root, rows)
	instance_root.free()
	return rows


## Collects transforms, imported bounds, bone rest poses and clip metadata.
func _inspect_node(node: Node, instance_root: Node, rows: Array[Dictionary]) -> void:
	var row: Dictionary = {
		"path": str(instance_root.get_path_to(node)), "class": node.get_class(),
	}
	if node is Node3D:
		row["transform"] = str(node.transform)
	if node is MeshInstance3D:
		row["aabb"] = str(node.get_aabb())
		row["material"] = str(node.mesh.surface_get_material(0))
	if node is Skeleton3D:
		var bones: Array[Dictionary] = []
		for index: int in node.get_bone_count():
			bones.append({
				"name": node.get_bone_name(index), "rest": str(node.get_bone_rest(index)),
			})
		row["bones"] = bones
	if node is AnimationPlayer:
		var clips: Array[Dictionary] = []
		for clip: StringName in node.get_animation_list():
			var animation: Animation = node.get_animation(clip)
			clips.append({
				"name": str(clip), "length": animation.length, "loop": animation.loop_mode,
			})
		row["clips"] = clips
	rows.append(row)
	for child: Node in node.get_children():
		_inspect_node(child, instance_root, rows)


## Inspects exact pinned APIs when development-engine interfaces differ from stable docs.
func inspect_api(type_name: String, pattern: String) -> Array[String]:
	var methods: Array[String] = []
	for method: Dictionary in ClassDB.class_get_method_list(type_name):
		if pattern in str(method.name):
			methods.append(str(method.name))
	return methods


## Loads the vendor scene handler in the editor only.
func _scene_commands() -> GDScript:
	return load("res://addons/godot_mcp_toolkit/commands/scene_commands.gd")
