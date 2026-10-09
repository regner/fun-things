@tool
class_name BatchThreeAuthor
extends Node3D
## Editor-only saved collision and source-marker assembly for the bounded batch.


# Literal extents remain together in this one editor-only authoring operation.
## Authors deliberate static shells or closed leaves without changing visual imports.
func collision_boxes(  # gdstyle:ignore=quality/max-local-variables,quality/max-function-length
	kind: String
) -> Dictionary:
	assert(Engine.is_editor_hint())
	var root: Node3D = EditorInterface.get_edited_scene_root()
	assert(not root.has_node("Collision"))
	var boxes: Array[Array] = []
	if kind == "shell":
		boxes = [
			[-3.2, -2.47, 0, 4.3, -7.0, -6.72],
			[-2.47, .57, 0, .54, -7.0, -6.72],
			[-2.47, .57, 2.42, 4.3, -7.0, -6.72],
			[.57, 1.24, 0, 4.3, -7.0, -6.72],
			[1.24, 2.66, 2.45, 4.3, -7.0, -6.72],
			[2.66, 3.2, 0, 4.3, -7.0, -6.72],
			[-3.2, -2.92, 0, 4.3, -6.72, 7.0],
			[2.92, 3.2, 0, 4.3, -6.72, 7.0],
			[-2.92, 2.92, 0, 4.3, 6.72, 7.0],
			[-3.2, 3.2, 4.14, 4.3, -7.0, 7.0],
		]
	elif kind == "single":
		boxes = [[-.512, .512, .03, 2.232, .43, .475]]
	elif kind == "double":
		boxes = [[-.912, -.004, .03, 2.232, .43, .475],
			[.004, .912, .03, 2.232, .43, .475]]
	elif kind == "pane":
		boxes = [[-1.469, -.031, .146, 1.854, -.035, .04],
			[.031, 1.469, .146, 1.854, -.035, .04]]
	else:
		assert(false, kind)

	var group: Node3D = Node3D.new()
	group.name = "Collision"
	root.add_child(group)
	group.owner = root
	var body: StaticBody3D = StaticBody3D.new()
	body.name = "Body"
	body.collision_layer = 1
	body.collision_mask = 0
	group.add_child(body)
	body.owner = root
	for index: int in range(boxes.size()):
		var b: Array = boxes[index]
		var shape := BoxShape3D.new()  # gdstyle:ignore=quality/allocation-in-loop
		shape.size = Vector3(b[1] - b[0], b[3] - b[2], b[5] - b[4])
		var node := CollisionShape3D.new()  # gdstyle:ignore=quality/allocation-in-loop
		node.name = "Shape" + str(index)
		node.shape = shape
		node.position = Vector3((b[0] + b[1]) / 2.0, (b[2] + b[3]) / 2.0, (b[4] + b[5]) / 2.0)
		body.add_child(node)
		node.owner = root

	EditorInterface.mark_scene_as_unsaved()
	return { "kind": kind, "bounds_xyz": boxes, "count": boxes.size() }


## Mounts immutable prefabs at actual imported shell marker transforms in a saved scene.
func mount_frontage() -> Dictionary:
	assert(Engine.is_editor_hint())
	var root: Node3D = EditorInterface.get_edited_scene_root()
	var model: Node3D = root.get_node("Shell/Visuals/Model")
	var paths: Dictionary = {
		"Entrance": ["mount_entrance_single", "city_shop_fittings_03_single"],
		"Door": ["mount_door_single", "city_shop_fittings_06_single"],
		"Window": ["mount_display_window", "city_shop_fittings_05"],
		"Canopy": ["mount_canopy", "city_shop_fittings_01"],
		"Fascia": ["mount_fascia", "city_shop_fittings_02"],
	}
	var rows: Array[Dictionary] = []
	for label: String in paths:
		var marker: Node3D = model.find_child(paths[label][0], true, false)
		assert(marker != null, paths[label][0])
		var path: String = "res://scenes/prefabs/environment/" + paths[label][1] + ".tscn"
		var packed: PackedScene = load(path)
		var node: Node3D = packed.instantiate()  # gdstyle:ignore=quality/allocation-in-loop
		node.name = label
		root.add_child(node)
		node.owner = root
		node.transform = model.transform * marker.transform
		rows.append({"node": label, "marker": str(marker.get_path()),
			"transform": str(node.transform), "prefab": node.scene_file_path})

	EditorInterface.mark_scene_as_unsaved()
	return { "mounts": rows }
