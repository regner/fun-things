@tool
class_name SmgWedgewireEditorAuthor
extends Node3D
## Editor-only bridge for linked GLB instances; stock scene_instantiate accepts .tscn only.


## Adds the imported instance without expanding or making its children editable.
func author_linked_model(resource_path: String, parent_path: NodePath) -> int:
	if not Engine.is_editor_hint():
		return ERR_UNAUTHORIZED

	var parent_node: Node = get_node(parent_path)
	var packed: PackedScene = load(resource_path) as PackedScene
	var instance: Node = packed.instantiate()
	instance.name = "Model"
	parent_node.add_child(instance)
	instance.owner = self
	return OK


## Relays the source marker's transform to a stable prefab-facing marker.
func author_relay_socket(source_name: String, target_path: NodePath) -> int:
	if not Engine.is_editor_hint():
		return ERR_UNAUTHORIZED

	var model: Node3D = get_node("Visuals/Model") as Node3D
	var source: Node3D = model.find_child(source_name, true, false) as Node3D
	var target: Node3D = get_node(target_path) as Node3D
	target.transform = global_transform.affine_inverse() * source.global_transform
	return OK
