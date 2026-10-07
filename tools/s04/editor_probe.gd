@tool
class_name S04EditorProbe
extends S02EditorProbe
## Editor-only authored inspection bridge; never part of gameplay rule ownership.


## Reports the actual pinned editor and saved project at the authoring boundary.
func s04_state() -> Dictionary:
	return { "project": ProjectSettings.globalize_path("res://"),
		"pin": Engine.get_version_info(), "open": EditorInterface.get_open_scenes(),
		"unsaved": EditorInterface.get_unsaved_scenes() }


## Inspects imported ancestry and bounds without copying mesh data or entering gameplay.
func inspect_owned(path: String) -> Array[Dictionary]:
	var packed: PackedScene = load(path)
	var instance_root: Node = packed.instantiate()
	var rows: Array[Dictionary] = []
	_collect(instance_root, ".", Transform3D.IDENTITY, rows)
	instance_root.free()
	return rows


## Accumulates packed node transforms and model bounds without tree-dependent positions.
func _collect(node: Node, path: String, parent_pose: Transform3D,
	rows: Array[Dictionary]) -> void:
	var pose: Transform3D = parent_pose
	var row: Dictionary = { "path": path, "class": node.get_class() }
	if node is Node3D:
		pose = parent_pose * node.transform
		row["pose"] = str(pose)
	if node is MeshInstance3D:
		row["aabb"] = str(pose * node.get_aabb())
		row["mesh_resource"] = node.mesh.resource_path
		row["surfaces"] = node.mesh.get_surface_count()
	rows.append(row)
	for child: Node in node.get_children():
		_collect(child, path + "/" + str(child.name), pose, rows)
