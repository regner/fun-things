@tool
class_name VehicleEditorAuthor
extends Node3D
## Editor-only authoring bridge for linked vehicle visuals and saved asset previews.

const MODEL_DIR: String = "res://art/models/city_cars/"
const WRAPPER_DIR: String = "res://scenes/prefabs/city_cars/"
const SOCKET_NAMES: Dictionary = {
	"socket_driver": "DriverSeat", "socket_entry_left": "EntryLeft",
	"socket_entry_right": "EntryRight", "socket_exit_left": "ExitLeft",
	"socket_exit_right": "ExitRight",
}
const DEMO_SECONDS: float = 6.0
const DOOR_OPEN_RAD: float = 0.872664626
const STEER_RAD: float = 0.30


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
	var model: Node3D = _linked(visuals, MODEL_DIR + asset + ".glb", "Model")
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


## Adds a scalar animation track; it only targets rigid visual descendants.
func _track(animation: Animation, path: String, keys: Array) -> void:
	var index: int = animation.add_track(Animation.TYPE_VALUE)
	animation.track_set_path(index, NodePath(path))
	animation.value_track_set_update_mode(index, Animation.UPDATE_CONTINUOUS)
	for key: Array in keys:
		animation.track_insert_key(index, float(key[0]), float(key[1]))


## Authors a saved preview with target and inspection cameras and cosmetic rigid motion.
func build_preview(asset: String) -> Dictionary:
	_linked(self, MODEL_DIR + "car_preview_stage.glb", "Stage")
	var car: Node3D = _linked(self, WRAPPER_DIR + asset + ".tscn", "Car")
	_preview_lighting()
	_preview_cameras()
	var door_count: int = _preview_animation(asset, car)
	set_meta("asset_id", asset)
	set_meta("preview_only", true)
	EditorInterface.mark_scene_as_unsaved()
	return { "asset": asset, "camera_height_m": 47.0, "fov_deg": 42.0,
		"door_count": door_count, "clip": "mechanical_demo", "seconds": DEMO_SECONDS }


## Configures only saved preview lighting and environment resources.
func _preview_lighting() -> void:
	var environment_node: WorldEnvironment = _owned(self, WorldEnvironment.new(), "Environment")
	var environment: Environment = Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color("#182632")
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color("#aecbd2")
	environment.ambient_light_energy = 0.30
	environment.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	environment_node.environment = environment

	var key: DirectionalLight3D = _owned(self, DirectionalLight3D.new(), "KeyLight")
	key.rotation_degrees = Vector3(-55.0, -32.0, 0.0)
	key.light_color = Color(1.0, 0.96, 0.92)
	key.light_energy = 0.85
	key.shadow_bias = 0.15
	key.shadow_enabled = true
	var fill: DirectionalLight3D = _owned(self, DirectionalLight3D.new(), "FillLight")
	fill.rotation_degrees = Vector3(-30.0, 140.0, 0.0)
	fill.light_color = Color("#78bbc7")
	fill.light_energy = 0.25


## Authors the prescribed game view and a separate close inspection camera.
func _preview_cameras() -> void:
	var game_camera: Camera3D = _owned(self, Camera3D.new(), "GameCamera")
	game_camera.position = Vector3(0.0, 47.0, 0.0)
	game_camera.rotation_degrees = Vector3(-90.0, 0.0, 0.0)
	game_camera.fov = 42.0
	game_camera.near = 0.1
	game_camera.far = 160.0
	game_camera.current = true
	var inspection: Camera3D = _owned(self, Camera3D.new(), "InspectionCamera")
	inspection.position = Vector3(4.6, 3.7, -5.4)
	inspection.fov = 42.0
	inspection.look_at(Vector3(0.0, 0.75, 0.0), Vector3.UP)


## Installs the cosmetic rigid-part demonstration in the asset-local preview.
func _preview_animation(asset: String, car: Node3D) -> int:
	var player: AnimationPlayer = _owned(self, AnimationPlayer.new(), "AnimationPlayer")
	var library: AnimationLibrary = AnimationLibrary.new()
	var demo: Animation = Animation.new()
	demo.length = DEMO_SECONDS
	demo.loop_mode = Animation.LOOP_LINEAR
	var reset: Animation = Animation.new()
	var model: Node3D = car.get_node("Visuals/Model/" + asset)
	_door_tracks(demo, reset, asset, model)
	_wheel_tracks(demo, reset, asset, model)

	library.add_animation("mechanical_demo", demo)
	library.add_animation("RESET", reset)
	if player.has_animation_library(""):
		player.remove_animation_library("")

	player.add_animation_library("", library)
	player.autoplay = "mechanical_demo"
	return model.get_node("Doors").get_child_count()


## Animates source-owned side hinges without root or gameplay-state motion.
func _door_tracks(demo: Animation, reset: Animation, asset: String, model: Node3D) -> void:
	for hinge: Node3D in model.get_node("Doors").get_children():
		var sign_value: float = -1.0 if str(hinge.name).ends_with("Left") else 1.0
		var track_path: String = "Car/Visuals/Model/" + asset + "/Doors/"
		track_path += str(hinge.name) + ":rotation:y"
		_track(demo, track_path, [[0.0, 0.0], [1.0, 0.0],
			[2.0, sign_value * DOOR_OPEN_RAD], [3.3, sign_value * DOOR_OPEN_RAD],
			[4.5, 0.0], [DEMO_SECONDS, 0.0]])
		_track(reset, track_path, [[0.0, 0.0]])


## Demonstrates local axle spin and front steering with stable authored pivot centres.
func _wheel_tracks(demo: Animation, reset: Animation, asset: String, model: Node3D) -> void:
	for steer: Node3D in model.get_node("Wheels").get_children():
		var spin: Node3D = steer.get_child(0)
		var spin_path: String = "Car/Visuals/Model/" + asset + "/Wheels/" + str(steer.name)
		spin_path += "/" + str(spin.name) + ":rotation:x"
		_track(demo, spin_path, [[0.0, 0.0], [DEMO_SECONDS, TAU]])
		_track(reset, spin_path, [[0.0, 0.0]])
		if str(steer.name).begins_with("SteerFront"):
			var steer_path: String = "Car/Visuals/Model/" + asset + "/Wheels/"
			steer_path += str(steer.name) + ":rotation:y"
			_track(demo, steer_path, [[0.0, 0.0], [1.5, STEER_RAD],
				[3.0, 0.0], [4.5, -STEER_RAD], [DEMO_SECONDS, 0.0]])
			_track(reset, steer_path, [[0.0, 0.0]])


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


## Caps only private-editor launches without altering project launch or gameplay settings.
func cap_preview() -> void:
	EditorInterface.get_editor_settings().set_setting("run/main_run_args",
		"--max-fps 60 --resolution 1280x800 --rendering-method gl_compatibility")
