@tool
extends Node
## Finite editor-only asset authoring; this helper is never attached to delivered scenes.

const BASE: String = "res://scenes/world/brackett_greybox/"
const MODELS: String = "res://art/models/brackett_greybox/"
const INPUT: String = "res://tools/brackett_greybox/editor_input.json"

var _written: Array[String] = []


## Schedules the finite batch outside the toolkit's deferred dispatch context.
func author() -> String:
	_build.call_deferred()
	return "Scheduled private greybox editor authoring"


## Builds linked wrappers, saved district placements and review-only cameras.
func _build() -> void:
	assert(Engine.is_editor_hint())
	var spec: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(INPUT))
	for directory: String in ["prefabs", "sectors"]:
		DirAccess.make_dir_recursive_absolute(BASE + directory)
	for asset: Dictionary in spec.kit:
		_build_prefab(asset)
	for surface: String in spec.surfaces:
		_build_surface(surface)
	for district: Dictionary in spec.districts:
		_build_district(district, spec.placements)
	_build_city(spec)
	_build_preview()
	print("BRACKETT_EDITOR_AUTHORED ", _written.size())


## Creates an ordinary static wrapper with simple deliberately separate collision.
func _build_prefab(asset: Dictionary) -> void:
	var root: Node3D = _placement(asset.asset_id)
	root.set("asset_id", StringName(asset.asset_id))
	var visuals: Node3D = _node(root, root, "Visuals")
	_model(root, visuals, asset.asset_id)
	var collision: Node3D = _node(root, root, "Collision")
	var body: StaticBody3D = StaticBody3D.new()
	body.name = "Solid"
	body.collision_layer = 1
	body.collision_mask = 0
	_add(root, collision, body)
	for index: int in asset.collision_boxes.size():
		var values: Array = asset.collision_boxes[index]
		# Finite editor authoring creates separate saved collision resources.
		# gdstyle:ignore=quality/allocation-in-loop
		var shape: CollisionShape3D = CollisionShape3D.new()
		shape.name = "Envelope%d" % index
		var box: BoxShape3D = BoxShape3D.new() # gdstyle:ignore=quality/allocation-in-loop
		box.size = Vector3(values[0], values[1], values[2])
		shape.shape = box
		shape.position = Vector3(values[3], values[4], values[5])
		_add(root, body, shape)
	_save(root, BASE + "prefabs/" + asset.asset_id + ".tscn")


## Uses only the imported land surface for collision, avoiding duplicate road planes.
func _build_surface(asset: String) -> void:
	var root: Node3D = _placement(asset)
	root.set("world_id", StringName("brackett/" + asset))
	root.set("asset_id", StringName(asset))
	var visuals: Node3D = _node(root, root, "Visuals")
	var model: Node = _model(root, visuals, asset)
	var collision: Node3D = _node(root, root, "Collision")
	var land: MeshInstance3D = model.find_child("land", true, false)
	assert(land != null)
	var body: StaticBody3D = StaticBody3D.new()
	body.name = "Ground"
	body.collision_layer = 1
	body.collision_mask = 0
	_add(root, collision, body)
	var shape: CollisionShape3D = CollisionShape3D.new()
	shape.name = "Surface"
	shape.shape = land.mesh.create_trimesh_shape()
	shape.transform = land.transform
	_add(root, body, shape)
	_save(root, BASE + "sectors/" + asset + ".tscn")


## Saves individual prefab instances and explicit replacement IDs per district.
func _build_district(district: Dictionary, placements: Array) -> void:
	var root: Node3D = _placement("District%02d" % district.id)
	root.set("world_id", StringName("brackett/district_%02d" % district.id))
	root.set("district_id", int(district.id))
	root.set("district_name", district.name)
	root.set_meta("discussion_id", "%02d" % district.id)
	var geometry: Node3D = _node(root, root, "Geometry")
	for item: Dictionary in placements:
		if int(item.district_id) != int(district.id):
			continue
		var packed: PackedScene = load(BASE + "prefabs/" + item.asset_id + ".tscn")
		var placed: Node3D = packed.instantiate()
		placed.name = item.world_id.get_file()
		placed.position = Vector3(item.position[0], item.position[1], item.position[2])
		placed.rotation.y = deg_to_rad(item.yaw_degrees)
		placed.set("world_id", StringName(item.world_id))
		placed.set("district_id", int(district.id))
		placed.set("district_name", district.name)
		_add(root, geometry, placed)
	_save(root, BASE + "sectors/district_%02d.tscn" % district.id)


## Composes the full island from reusable saved sectors without gameplay dependencies.
func _build_city(spec: Dictionary) -> void:
	var root: Node3D = _placement("BrackettGreybox")
	root.set("world_id", &"brackett")
	root.set_meta("status", "whole-island greybox checkpoint; integration pending")
	var sectors: Node3D = _node(root, root, "Sectors")
	for asset: String in spec.surfaces:
		_instance(root, sectors, BASE + "sectors/" + asset + ".tscn", asset)
	for district: Dictionary in spec.districts:
		_instance(root, sectors, BASE + "sectors/district_%02d.tscn" % district.id,
			"District%02d" % district.id)
	_save(root, BASE + "city.tscn")


## Authors fixed overview and north-up 47 m / 42 degree review cameras in a saved scene.
func _build_preview() -> void:
	var root: Node3D = Node3D.new()
	root.name = "BrackettGreyboxPreview"
	root.set_script(load(BASE + "preview.gd"))
	_instance(root, root, BASE + "city.tscn", "City")
	var water: Node3D = _node(root, root, "Water")
	_model(root, water, "water")
	var environment: WorldEnvironment = WorldEnvironment.new()
	environment.name = "Environment"
	environment.environment = Environment.new()
	environment.environment.background_mode = Environment.BG_COLOR
	environment.environment.background_color = Color(0.08, 0.10, 0.13)
	environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.environment.ambient_light_color = Color(0.72, 0.78, 0.86)
	environment.environment.ambient_light_energy = 0.3
	_add(root, root, environment)
	var sun: DirectionalLight3D = DirectionalLight3D.new()
	sun.name = "ReviewSun"
	sun.rotation_degrees = Vector3(-58, -28, 0)
	sun.light_energy = 0.65
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 1800
	_add(root, root, sun)
	var cameras: Node3D = _node(root, root, "Cameras")
	var overview: Camera3D = _camera(root, cameras, "Overview", Vector3(0, 950, 690))
	overview.projection = Camera3D.PROJECTION_ORTHOGONAL
	overview.size = 890
	overview.rotation.x = -atan2(950, 690)
	overview.current = true
	var plan: Camera3D = _camera(root, cameras, "Plan", Vector3(0, 1000, 0))
	plan.projection = Camera3D.PROJECTION_ORTHOGONAL
	plan.size = 810
	var targets: Array[Vector2] = [Vector2(220, 205), Vector2(280, 267),
		Vector2(465, 205), Vector2(735, 285), Vector2(450, 490),
		Vector2(530, 350), Vector2(705, 530), Vector2(895, 405), Vector2(1090, 424)]
	for index: int in targets.size():
		var point: Vector2 = targets[index]
		_camera(root, cameras, "District%02d" % (index + 1),
			Vector3(point.x - 630, 47, point.y - 355))
	_overlay(root)
	_save(root, BASE + "preview.tscn")


## Authors the review legend without runtime UI hierarchy construction.
func _overlay(root: Node) -> void:
	var canvas: CanvasLayer = CanvasLayer.new()
	canvas.name = "ReviewOverlay"
	_add(root, root, canvas)
	var label: Label = Label.new()
	label.name = "Instructions"
	label.position = Vector2(20, 16)
	label.text = "BRACKETT GREYBOX  |  0 overview · Tab plan · 1–9 districts\n"
	label.text += "47 m / 42° district cameras · north up · provisional collision"
	label.add_theme_font_size_override("font_size", 17)
	label.add_theme_color_override("font_shadow_color", Color.BLACK)
	label.add_theme_constant_override("shadow_offset_x", 1)
	label.add_theme_constant_override("shadow_offset_y", 1)
	_add(root, canvas, label)


## Creates a fixed north-up perspective camera, later specialised only for overviews.
func _camera(root: Node, parent: Node, label: String, point: Vector3) -> Camera3D:
	var camera: Camera3D = Camera3D.new()
	camera.name = label
	camera.position = point
	camera.rotation_degrees = Vector3(-90, 0, 0)
	camera.fov = 42
	camera.near = 0.1
	camera.far = 2400
	_add(root, parent, camera)
	return camera


## Assigns the explicit placement schema before serialisation.
func _placement(label: String) -> Node3D:
	var root: Node3D = Node3D.new()
	root.name = label
	root.set_script(load(BASE + "placement.gd"))
	return root


## Adds an ordinary authored grouping node.
func _node(root: Node, parent: Node, label: String) -> Node3D:
	var child: Node3D = Node3D.new()
	child.name = label
	_add(root, parent, child)
	return child


## Keeps GLB ancestry linked and imported children noneditable.
func _model(root: Node, parent: Node, asset: String) -> Node:
	return _instance(root, parent, MODELS + asset + ".glb", "Model")


## Instances a saved resource without copying its authored descendants.
func _instance(root: Node, parent: Node, path: String, label: String) -> Node:
	var packed: PackedScene = load(path)
	assert(packed != null, path)
	var child: Node = packed.instantiate()
	child.name = label
	_add(root, parent, child)
	return child


## Gives only newly authored roots to the current scene owner.
func _add(root: Node, parent: Node, child: Node) -> void:
	parent.add_child(child)
	child.owner = root


## Packs editor-authored nodes; the later actual-editor roundtrip generates saved identities.
func _save(root: Node, path: String) -> void:
	assert(not FileAccess.file_exists(path), "Bootstrap only; preserve saved resource identities")
	var packed: PackedScene = PackedScene.new()
	assert(packed.pack(root) == OK)
	assert(ResourceSaver.save(packed, path) == OK)
	_written.append(path)
	root.free()
