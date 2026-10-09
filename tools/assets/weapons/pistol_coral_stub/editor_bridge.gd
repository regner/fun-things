@tool
class_name CoralStubEditorBridge
extends Node3D
## Editor-only authoring bridge for imported GLBs; never attached to shipped assets.


## Adds a linked imported model where scene.instantiate rejects GLB file extensions.
func add_imported_model(asset_path: String, parent_path: NodePath, model_name: String) -> String:
	assert(Engine.is_editor_hint())
	assert(asset_path.begins_with("res://art/models/"))
	var parent_node: Node = get_node(parent_path)
	assert(not parent_node.has_node(NodePath(model_name)))
	var packed: PackedScene = load(asset_path) as PackedScene
	assert(packed != null)
	var model: Node = packed.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	model.name = model_name
	parent_node.add_child(model)
	model.owner = self
	return str(get_path_to(model))


## Relays source-authored marker transforms into stable prefab-facing sockets.
func relay_pistol_sockets() -> Dictionary:
	assert(Engine.is_editor_hint())
	var model: Node3D = get_node("Visuals/Model") as Node3D
	var mappings: Dictionary = { "socket_grip": "Sockets/Grip", "socket_muzzle": "Sockets/Muzzle" }
	var result: Dictionary = {}
	for source_name: String in mappings:
		var source: Node3D = model.find_child(source_name, true, false) as Node3D
		assert(source != null)
		var target: Node3D = get_node(mappings[source_name]) as Node3D
		target.transform = global_transform.affine_inverse() * source.global_transform
		result[source_name] = str(target.transform)
	return result
