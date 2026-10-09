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


## Registers existing saved IDs in the editor cache without changing authored resources.
func register_uids(paths: Array) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	for path: String in paths:
		var uid: int = ResourceLoader.get_resource_uid(path)
		assert(uid != ResourceUID.INVALID_ID, path)
		var existed: bool = ResourceUID.has_id(uid)
		var prior: String = ResourceUID.get_id_path(uid) if existed else ""
		assert(prior.is_empty() or prior == path, "UID collision: " + prior)
		if not existed:
			ResourceUID.add_id(uid, path)

		rows.append({"path": path, "uid": ResourceUID.id_to_text(uid),
			"was_registered": existed, "resolved": ResourceUID.get_id_path(uid)})

	return rows


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


# One-shot editor authoring keeps shape construction local; no runtime allocation loop.
# The collision branches and multiline arguments stay local to this editor-only operation.
## Authors linked static props; facade hardware has no independent gameplay collision.
func build_static(  # gdstyle:ignore=quality/max-local-variables
	path: String, collision_kind: String
) -> Dictionary:
	assert(Engine.is_editor_hint())
	var root: Node3D = EditorInterface.get_edited_scene_root()
	assert(root != null and not root.has_node("Visuals"))
	var visuals: Node3D = _owned(root, Node3D.new(), "Visuals", root)
	var packed: PackedScene = load(path)
	assert(packed != null, path)
	var model: Node3D = packed.instantiate()
	_owned(visuals, model, "Model", root)
	var shape_count: int = 0
	if collision_kind != "none":
		var collision: Node3D = _owned(root, Node3D.new(), "Collision", root)
		var body: StaticBody3D = _owned(collision, StaticBody3D.new(), "Body", root)
		body.collision_layer = 1
		body.collision_mask = 0
		if collision_kind == "box":
			var box: BoxShape3D = BoxShape3D.new()
			box.size = Vector3(2.4, 0.6, 0.9)
			var shape: CollisionShape3D = _owned(body, CollisionShape3D.new(), "Shape", root)
			shape.shape = box
			shape.position.y = 0.3
			shape_count = 1
		elif collision_kind == "ring":
			const SEGMENTS: int = 16
			const CLEAR_RADIUS_M: float = 0.62
			const OUTER_R_M: float = 0.9
			const HEIGHT_M: float = 0.48
			var inner_radius: float = CLEAR_RADIUS_M / cos(PI / SEGMENTS)
			for index: int in range(SEGMENTS):

				var convex: ConvexPolygonShape3D
				convex = ConvexPolygonShape3D.new()  # gdstyle:ignore=quality/allocation-in-loop
				convex.points = _ring_points(index, SEGMENTS, inner_radius, OUTER_R_M, HEIGHT_M)
				var shape := CollisionShape3D.new()  # gdstyle:ignore=quality/allocation-in-loop
				_owned(body, shape, "Segment" + str(index), root)
				shape.shape = convex
				shape_count += 1

		else:
			assert(false, "Unsupported collision kind")

	EditorInterface.mark_scene_as_unsaved()
	return {"model": model.scene_file_path, "collision_kind": collision_kind,
		"shape_count": shape_count}


## Returns one annular prism's corners while preserving the authored clear inner radius.
func _ring_points(
	index: int, segments: int, inner: float, outer: float, height_m: float
) -> PackedVector3Array:
	var points: PackedVector3Array = []
	for height: float in [0.0, height_m]:
		for radius: float in [inner, outer]:
			for angle: float in [TAU * index / segments, TAU * (index + 1) / segments]:
				points.append(Vector3(cos(angle) * radius, height, sin(angle) * radius))

	return points


## Assigns explicit scene ownership to editor-authored children while keeping imports linked.
func _owned(parent: Node, child: Node, label: String, scene_root: Node) -> Node:
	child.name = label
	parent.add_child(child)
	child.owner = scene_root
	return child


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
			"size": [bounds.size.x, bounds.size.y, bounds.size.z],
			"surfaces": _surface_info(node.mesh)})

	for child: Node in node.get_children():
		_collect(child, pose, rows)


## Records imported material response without adding an override or external writer.
func _surface_info(mesh: Mesh) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	for index: int in range(mesh.get_surface_count()):
		var material: StandardMaterial3D = mesh.surface_get_material(index)
		assert(material != null)
		rows.append({"slot": index, "name": material.resource_name,
			"color": str(material.albedo_color), "roughness": material.roughness,
			"metallic": material.metallic, "cull_mode": material.cull_mode,
			"transparency": material.transparency, "resource": material.resource_path})

	return rows
