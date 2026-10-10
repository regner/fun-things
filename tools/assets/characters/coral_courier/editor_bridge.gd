@tool
class_name PlayerAssetEditorBridge
extends Node3D
## Editor-only authoring bridge; bounded allocations create saved resources, never runtime meshes.

const MOTION_PATH: String = "res://art/animations/characters/shared_humanoid/player_v1.tres"


## Add an authored node and assign only its wrapper ownership.
func add_owned(parent: Node, node: Node, node_name: String) -> Node:
	node.name = node_name
	parent.add_child(node)
	node.owner = self
	return node


## Build the reusable visual wrapper around a linked imported skin scene.
func build_actor() -> void:
	assert(get_child_count() == 0)
	var anchor: Node3D = add_owned(self, Node3D.new(), "PresentationAnchor") as Node3D
	var visuals: Node3D = add_owned(anchor, Node3D.new(), "Visuals") as Node3D
	var packed: PackedScene = load("res://art/models/characters/coral_courier/coral_courier.glb")
	add_owned(visuals, packed.instantiate(), "Model")
	EditorInterface.mark_scene_as_unsaved()


## Compose the close preview with linked player/ground and saved camera/lighting.
func build_preview() -> void:
	assert(get_child_count() == 0)
	var packed: PackedScene = load("res://scenes/prefabs/player_character/coral_courier.tscn")
	add_owned(self, packed.instantiate(), "Courier")
	var ground: PackedScene = load("res://art/models/brackett_greybox/ground_00_00.glb")
	add_owned(self, ground.instantiate(), "Ground")
	var camera: Camera3D = add_owned(self, Camera3D.new(), "Camera") as Camera3D
	camera.position = Vector3(-2.7, 2.1, -3.9)
	camera.look_at(Vector3(0.0, 0.95, 0.0))
	camera.fov = 32.0
	camera.near = 0.01
	camera.far = 120.0
	camera.current = true
	var sun: DirectionalLight3D = add_owned(
		self,
		DirectionalLight3D.new(),
		"Key",
	) as DirectionalLight3D
	sun.rotation_degrees = Vector3(-45.0, -35.0, 0.0)
	sun.light_color = Color(1.0, 0.88, 0.75)
	sun.light_energy = 1.6
	sun.shadow_enabled = true
	var fill: DirectionalLight3D = add_owned(
		self,
		DirectionalLight3D.new(),
		"Fill",
	) as DirectionalLight3D
	fill.rotation_degrees = Vector3(-35.0, 140.0, 0.0)
	fill.light_color = Color(0.48, 0.70, 1.0)
	fill.light_energy = 0.65
	var world: WorldEnvironment = add_owned(
		self,
		WorldEnvironment.new(),
		"Environment",
	) as WorldEnvironment
	var environment: Environment = Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color(0.028, 0.065, 0.09)
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.55, 0.65, 0.72)
	environment.ambient_light_energy = 0.65
	world.environment = environment
	EditorInterface.mark_scene_as_unsaved()


## Extract the explicit player animation library from their source-linked motion GLBs.
func save_motion_libraries() -> Dictionary:
	DirAccess.make_dir_recursive_absolute("res://art/animations/characters/shared_humanoid")
	var result: Dictionary = {}
	for family: String in ["player"]:
		var stem: String = "shared_humanoid_" + family + "_motion_v1"
		var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(
			"res://art/source/models/characters/shared_humanoid/" + stem + ".json"))
		# Extraction must consume the fresh imported file, not an editor-held older scene.
		var packed: PackedScene = ResourceLoader.load(
			"res://art/models/characters/shared_humanoid/" + stem + ".glb",
			"PackedScene", ResourceLoader.CACHE_MODE_IGNORE_DEEP
		)
		var source: Node = packed.instantiate()
		var imported: AnimationPlayer = source.find_child(
			"AnimationPlayer",
			true,
			false,
		) as AnimationPlayer
		assert(imported != null)
		var library: AnimationLibrary = (
			AnimationLibrary.new()  # gdstyle:ignore=quality/allocation-in-loop
		)
		var summary: Array[Dictionary] = []
		for clip: Dictionary in manifest.clips:
			assert(imported.has_animation(clip.name), "Missing imported clip " + str(clip.name))
			var animation: Animation = imported.get_animation(clip.name).duplicate(true)
			animation.loop_mode = Animation.LOOP_LINEAR if clip.loop else Animation.LOOP_NONE
			if clip.has("stance_right_seconds"):
				var stance: Array = clip.stance_right_seconds
				animation.set_meta(&"stance_right_seconds", Vector2(stance[0], stance[1]))
			library.add_animation(clip.name, animation)
			summary.append({
				"name": clip.name, "duration": animation.length,
				"tracks": animation.get_track_count(),
				"first_path": str(animation.track_get_path(0)),
			})
		_save_library(library,
			"res://art/animations/characters/shared_humanoid/" + family + "_v1.tres")
		result[family] = summary
		source.free()
	return result


## Add a saved animation player whose tracks target the linked model's stable skeleton.
func install_actor_motion() -> void:
	assert(not has_node("AnimationPlayer"))
	var player: AnimationPlayer = add_owned(
		self,
		AnimationPlayer.new(),
		"AnimationPlayer",
	) as AnimationPlayer
	player.root_node = NodePath("../PresentationAnchor/Visuals/Model")
	var library: AnimationLibrary = load(MOTION_PATH)
	player.add_animation_library("player", library)
	player.autoplay = "player/idle"
	EditorInterface.mark_scene_as_unsaved()


## Add the exact saved gameplay-camera view without replacing the close preview camera.
func add_game_camera() -> void:
	assert(not has_node("GameCamera"))
	var camera: Camera3D = add_owned(self, Camera3D.new(), "GameCamera") as Camera3D
	camera.position = Vector3(0.0, 47.0, 0.0)
	camera.rotation_degrees = Vector3(-90.0, 0.0, 0.0)
	camera.fov = 42.0
	camera.near = 0.1
	camera.far = 160.0
	camera.current = false
	EditorInterface.mark_scene_as_unsaved()


## Preserve constant bone tracks so switching clips restores hands and other idle joints.
func configure_motion_imports() -> void:
	var paths: PackedStringArray = PackedStringArray()
	for family: String in ["player"]:
		var path: String = "res://art/models/characters/shared_humanoid/shared_humanoid_"
		path += family + "_motion_v1.glb"
		var config: ConfigFile = ConfigFile.new()  # gdstyle:ignore=quality/allocation-in-loop
		assert(config.load(path + ".import") == OK)
		config.set_value("params", "animation/remove_immutable_tracks", false)
		assert(config.save(path + ".import") == OK)
		paths.append(path)
	_reimport_motion.bind(paths).call_deferred()


## Reimport on an ordinary editor frame outside the deferred toolkit dispatch queue.
func _reimport_motion(paths: PackedStringArray) -> void:
	await get_tree().process_frame
	EditorInterface.get_resource_filesystem().reimport_files(paths)


## Save complementary animation libraries without inventing or changing source keyframes.
func save_layer_libraries() -> void:
	var full: AnimationLibrary = ResourceLoader.load(
		MOTION_PATH, "AnimationLibrary", ResourceLoader.CACHE_MODE_IGNORE_DEEP
	)
	var upper: AnimationLibrary = AnimationLibrary.new()
	var lower: AnimationLibrary = AnimationLibrary.new()
	var lower_bones: PackedStringArray = ["root", "pelvis", "spine", "thigh_r", "shin_r",
		"foot_r", "toe_r", "thigh_l", "shin_l", "foot_l", "toe_l"]
	for name: StringName in full.get_animation_list():
		if name == &"death":
			continue
		var is_weapon: bool = str(name).begins_with("pistol") or str(name).begins_with("smg")
		is_weapon = is_weapon or str(name).begins_with("launcher")
		var animation: Animation = full.get_animation(name).duplicate(true)
		for index: int in range(animation.get_track_count() - 1, -1, -1):
			var bone: String = str(animation.track_get_path(index).get_subname(0))
			if lower_bones.has(bone) == is_weapon:
				animation.remove_track(index)
		if is_weapon:
			upper.add_animation(name, animation)
		else:
			lower.add_animation(name, animation)
	var upper_path: String = "res://art/animations/characters/shared_humanoid/player_upper_v1.tres"
	_save_library(upper, upper_path)
	var lower_path: String = "res://art/animations/characters/shared_humanoid/player_lower_v1.tres"
	_save_library(lower, lower_path)


## Preserve saved library UIDs and animation identities across headless extraction.
func _save_library(library: AnimationLibrary, path: String) -> void:
	var uid: int = ResourceUID.INVALID_ID
	if ResourceLoader.exists(path):
		uid = ResourceLoader.get_resource_uid(path)
		var previous: AnimationLibrary = ResourceLoader.load(
			path, "AnimationLibrary", ResourceLoader.CACHE_MODE_IGNORE_DEEP
		)
		for name: StringName in library.get_animation_list():
			if previous.has_animation(name):
				library.get_animation(name).resource_scene_unique_id = (
					previous.get_animation(name).resource_scene_unique_id
				)
	var error: Error = ResourceSaver.save(library, path)
	assert(error == OK)
	if uid != ResourceUID.INVALID_ID:
		error = ResourceSaver.set_uid(path, uid)
		assert(error == OK)


## Install saved layer players and source-authored grip offsets on the existing actor.
func install_layers_and_grips() -> void:
	for family: String in ["upper", "lower"]:
		var node_name: String = "UpperBodyPlayer" if family == "upper" else "LowerBodyPlayer"
		var player: AnimationPlayer = add_owned(
			self,
			AnimationPlayer.new(),  # gdstyle:ignore=quality/allocation-in-loop
			node_name,
		) as AnimationPlayer
		player.root_node = NodePath("../PresentationAnchor/Visuals/Model")
		player.add_animation_library(
			&"",
			load("res://art/animations/characters/shared_humanoid/player_" + family + "_v1.tres"),
		)
	var attachment: BoneAttachment3D = add_owned(
		self,
		BoneAttachment3D.new(),
		"Sockets",
	) as BoneAttachment3D
	attachment.use_external_skeleton = true
	attachment.external_skeleton = NodePath("../PresentationAnchor/Visuals/Model/Rig/Skeleton3D")
	attachment.bone_name = "hand_r"
	add_owned(attachment, Marker3D.new(), "WeaponMount")
	EditorInterface.mark_scene_as_unsaved()


## Convert source matrices into Godot bone space and store them on the visual script.
func store_grip_profiles() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(
		"res://art/source/models/characters/coral_courier/weapon_profiles.json"))
	var conversion: Transform3D = Transform3D(
		Basis(Vector3.RIGHT, Vector3.FORWARD, Vector3.UP),
		Vector3.ZERO,
	)
	var profiles: Dictionary[StringName, Transform3D] = {}
	for name: String in data.profiles:
		var rows: Array = data.profiles[name].hand_to_grip_blender
		var matrix: Transform3D = Transform3D(Basis(
			Vector3(rows[0][0], rows[1][0], rows[2][0]),
			Vector3(rows[0][1], rows[1][1], rows[2][1]),
			Vector3(rows[0][2], rows[1][2], rows[2][2])),
			Vector3(rows[0][3], rows[1][3], rows[2][3]))
		profiles[StringName(name)] = matrix * conversion.affine_inverse()
	set_meta("authored_grip_profiles", profiles)
	EditorInterface.mark_scene_as_unsaved()


## Build a temporary diagnostic scene from immutable peer GLBs staged by the fit tool.
func build_fit_preview() -> void:
	build_preview()
	set_editable_instance(get_node("Courier"), true)
	add_game_camera()
	var mount: Node = get_node("Courier/Sockets/WeaponMount")
	for weapon: String in ["pistol", "smg", "launcher"]:
		var path: String = "res://art/models/characters/coral_courier/fit_check/" + weapon + ".glb"
		var packed: PackedScene = load(path)
		var instance: Node3D = add_owned(mount, packed.instantiate(), weapon.capitalize()) as Node3D
		instance.visible = false
	EditorInterface.mark_scene_as_unsaved()


## Retain diagnostic-only children beneath the project-owned actor wrapper when saving.
func retain_fit_children() -> void:
	set_editable_instance(get_node("Courier"), true)
	EditorInterface.mark_scene_as_unsaved()


## Save a minimal inspection overlay in the player-only review scene.
func add_review_overlay() -> void:
	var canvas: CanvasLayer = add_owned(self, CanvasLayer.new(), "ReviewOverlay") as CanvasLayer
	var caption: Label = add_owned(canvas, Label.new(), "Caption") as Label
	caption.position = Vector2(20, 20)
	caption.add_theme_font_size_override("font_size", 18)
	caption.add_theme_color_override("font_shadow_color", Color(0.015, 0.025, 0.04, 1))
	caption.add_theme_constant_override("shadow_offset_x", 2)
	caption.add_theme_constant_override("shadow_offset_y", 2)
	caption.text = "Coral Courier • idle\n← / → clip    Tab camera\nClose review"
	EditorInterface.mark_scene_as_unsaved()


## View the support side so the launcher does not hide the face in the close inspection.
func set_support_side_camera() -> void:
	var camera: Camera3D = get_node("Camera")
	camera.position = Vector3(-2.7, 2.1, -3.9)
	camera.look_at(Vector3(0.0, 0.95, 0.0))
	EditorInterface.mark_scene_as_unsaved()
