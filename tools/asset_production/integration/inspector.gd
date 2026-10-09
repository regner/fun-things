@tool
class_name AssetProductionInspector
extends Node3D
## Editor-only measurements and ownership checks for the production commission.


## Reports private project/process identity and saved/unsaved editor scenes.
func context() -> Dictionary:
	return {"project": ProjectSettings.globalize_path("res://"),
		"pid": OS.get_process_id(), "engine": Engine.get_version_info().string,
		"open": EditorInterface.get_open_scenes(),
		"unsaved": EditorInterface.get_unsaved_scenes()}


## Authors one source-linked static model with deliberate pole collision in the editor.
func build_pole(path: String, radius_m: float, height_m: float) -> Dictionary:
	assert(Engine.is_editor_hint())
	var root: Node3D = EditorInterface.get_edited_scene_root()
	assert(root != null and not root.has_node("Visuals"))
	var visuals: Node3D = Node3D.new()
	visuals.name = "Visuals"
	root.add_child(visuals)
	visuals.owner = root
	var packed: PackedScene = load(path)
	assert(packed != null, path)
	var model: Node3D = packed.instantiate()
	model.name = "Model"
	visuals.add_child(model)
	model.owner = root
	var collision: Node3D = Node3D.new()
	collision.name = "Collision"
	root.add_child(collision)
	collision.owner = root
	var body: StaticBody3D = StaticBody3D.new()
	body.name = "PoleBody"
	body.collision_layer = 1
	body.collision_mask = 0
	collision.add_child(body)
	body.owner = root
	var shape: CollisionShape3D = CollisionShape3D.new()
	shape.name = "Shape"
	var cylinder: CylinderShape3D = CylinderShape3D.new()
	cylinder.radius = radius_m
	cylinder.height = height_m
	shape.shape = cylinder
	shape.position.y = height_m * 0.5
	body.add_child(shape)
	shape.owner = root
	EditorInterface.mark_scene_as_unsaved()
	return {"model": model.scene_file_path, "radius_m": radius_m,
		"height_m": height_m, "collision_layer": body.collision_layer}


## Measures source-linked imported mesh bounds and records model ancestry.
func inspect_prefab(path: String) -> Dictionary:
	var packed: PackedScene = load(path)
	assert(packed != null, path)
	var instance: Node3D = packed.instantiate()
	var rows: Array[Dictionary] = []
	_collect(instance, Transform3D.IDENTITY, rows)
	var model: Node3D = instance.get_node("Visuals/Model")
	var result: Dictionary = {"prefab": path, "model": model.scene_file_path,
		"model_transform": str(model.transform), "mesh_rows": rows}
	instance.free()
	return result


## Accumulates transformed imported bounds without changing meshes or placement.
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
