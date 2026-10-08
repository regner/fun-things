@tool
class_name S05EffectEditorProbe
extends Node
## Editor-only GLB instantiation workaround and saved-scene identity inspection.

const MODEL: String = "res://art/models/spikes/s05_explosion_carrier.glb"


## Instances the linked imported scene where the toolkit refuses non-tscn paths.
func link_model() -> Dictionary:
	var root: Node = EditorInterface.get_edited_scene_root()
	var packed: PackedScene = load(MODEL) as PackedScene
	var model: Node = packed.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	model.name = "Model"
	root.get_node("Visuals").add_child(model)
	model.owner = root
	return { "path": model.scene_file_path, "transform": str((model as Node3D).transform) }


## Reports real editor context and outstanding unsaved paths before cleanup.
func context() -> Dictionary:
	return {"editor_hint": Engine.is_editor_hint(), "pid": OS.get_process_id(),
		"project": ProjectSettings.globalize_path("res://"),
		"unsaved": EditorInterface.get_unsaved_scenes()}


## Inspects saved linked ancestry and authored transforms without a draw claim.
func inspect_scene(path: String) -> Dictionary:
	var packed: PackedScene = ResourceLoader.load(path, "PackedScene",
		ResourceLoader.CACHE_MODE_REPLACE) as PackedScene
	var scene: Node = packed.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var rows: Array[Dictionary] = []
	_walk(scene, scene, rows)
	scene.free()
	return {"uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(path)),
		"nodes": rows}


## Records structural model links recursively without modifying saved resources.
func _walk(node: Node, root: Node, rows: Array[Dictionary]) -> void:
	var row: Dictionary = {"path": str(root.get_path_to(node)),
		"class": node.get_class(), "scene": node.scene_file_path}
	if node is Node3D:
		row.transform = str(node.transform)
		row.visible = node.visible

	if node is MeshInstance3D:
		row.mesh_path = node.mesh.resource_path
		row.bounds = str(node.mesh.get_aabb())
		row.materials = []
		for surface: int in node.mesh.get_surface_count():
			row.materials.append(node.mesh.surface_get_material(surface).resource_name)

	rows.append(row)
	for child: Node in node.get_children():
		_walk(child, root, rows)


## Defers owned editor shutdown only after all authorized scene changes are saved.
func request_quit() -> bool:
	if not EditorInterface.get_unsaved_scenes().is_empty():
		return false

	call_deferred("_quit")
	return true


## Lets the completed tool response leave before gracefully quitting the editor tree.
func _quit() -> void:
	get_tree().quit()
