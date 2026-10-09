@tool
class_name VehicleEditorAuthor
extends Node3D
## Editor-only authoring bridge for linked vehicle visuals and saved vehicle wrappers.

const MODEL_DIR: String = "res://art/models/vehicles/"
const WRAPPER_DIR: String = "res://scenes/prefabs/city_cars/"
const SOCKET_NAMES: Dictionary = {
	"socket_driver": "DriverSeat", "socket_entry_left": "EntryLeft",
	"socket_entry_right": "EntryRight", "socket_exit_left": "ExitLeft",
	"socket_exit_right": "ExitRight",
}


## Reports process, project and unsaved editor state before mutations.
func context() -> Dictionary:
	return {"project": ProjectSettings.globalize_path("res://"),
		"pid": OS.get_process_id(), "engine": Engine.get_version_info().string,
		"open": EditorInterface.get_open_scenes(),
		"unsaved": EditorInterface.get_unsaved_scenes()}


## Adds authored children with explicit scene ownership for editor serialization.
func _owned(parent: Node, child: Node, label: String) -> Node:
	if parent.has_node(NodePath(label)):
		child.free()
		return parent.get_node(NodePath(label))

	child.name = label
	parent.add_child(child)
	child.owner = self
	return child


## Instantiates a GLB or saved wrapper without making imported children editable.
func _linked(parent: Node, path: String, label: String) -> Node3D:
	if parent.has_node(NodePath(label)):
		return parent.get_node(NodePath(label))

	var packed: PackedScene = load(path)
	assert(packed != null, path)
	var child: Node3D = packed.instantiate()
	_owned(parent, child, label)
	return child


## Authors a visual-only wrapper and copies source-authored socket transforms.
func build_wrapper(asset: String) -> Dictionary:
	var visuals: Node3D = _owned(self, Node3D.new(), "Visuals")
	var model: Node3D = _linked(visuals, MODEL_DIR + asset + "/" + asset + ".glb", "Model")
	var sockets: Node3D = _owned(self, Node3D.new(), "Sockets")
	var socket_rows: Dictionary = {}
	for source_name: String in SOCKET_NAMES:
		var source: Node3D = model.get_node(asset + "/Markers/" + source_name)
		var target: Marker3D = _socket(sockets, SOCKET_NAMES[source_name])
		target.transform = global_transform.affine_inverse() * source.global_transform
		socket_rows[str(target.name)] = [target.position.x, target.position.y, target.position.z]

	set_meta("asset_id", asset)
	set_meta("visual_only", true)
	EditorInterface.mark_scene_as_unsaved()
	return { "asset": asset, "sockets": socket_rows, "model_source": model.scene_file_path }


## Creates one source-mapped socket during the editor-only authoring transaction.
func _socket(parent: Node, label: String) -> Marker3D:
	return _owned(parent, Marker3D.new(), label)


## Measures imported rest bounds, mesh ancestry and socket agreement from saved scenes.
func inspect_asset(asset: String) -> Dictionary:
	var packed: PackedScene = load(WRAPPER_DIR + asset + ".tscn")
	var instance: Node3D = packed.instantiate()
	var rows: Array[Dictionary] = []
	_collect(instance, Transform3D.IDENTITY, rows)
	var source: Node3D = instance.get_node("Visuals/Model")
	var agrees: bool = true
	for source_name: String in SOCKET_NAMES:
		var authored: Node3D = source.get_node(asset + "/Markers/" + source_name)
		var saved: Node3D = instance.get_node("Sockets/" + SOCKET_NAMES[source_name])
		agrees = agrees and authored.transform.is_equal_approx(saved.transform)

	var result: Dictionary = {"asset": asset, "model": source.scene_file_path,
		"socket_agreement": agrees, "mesh_rows": rows,
		"visual_only": instance.get_meta("visual_only") }
	instance.free()
	return result


## Accumulates world-relative mesh bounds without requiring a running physics tree.
func _collect(node: Node, parent_pose: Transform3D, rows: Array[Dictionary]) -> void:
	var pose: Transform3D = parent_pose
	if node is Node3D:
		pose = parent_pose * node.transform

	if node is MeshInstance3D:
		var bounds: AABB = pose * node.get_aabb()
		rows.append({"node": str(node.name), "resource": node.mesh.resource_path,
			"min": [bounds.position.x, bounds.position.y, bounds.position.z],
			"size": [bounds.size.x, bounds.size.y, bounds.size.z]})

	for child: Node in node.get_children():
		_collect(child, pose, rows)
