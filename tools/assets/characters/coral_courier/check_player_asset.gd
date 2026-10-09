extends SceneTree
## Focused public-API skin, clip, layering and attachment contract checks.

const ACTOR: String = "res://scenes/prefabs/player_character/coral_courier.tscn"
const SHARED_ANIMATIONS: String = "res://art/animations/characters/shared_humanoid/"
const SHARED_MODELS: String = "res://art/models/characters/shared_humanoid/"
const SHARED_SOURCE: String = "res://art/source/models/characters/shared_humanoid/"
const EPSILON: float = 0.0001

var failures: Array[String] = []


## Run once after the scene tree has initialized.
func _initialize() -> void:
	check.call_deferred()


## Record every failed expectation before returning a nonzero process status.
func expect(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
		push_error(message)


## Sample a complete pose through the public animation player.
func sample(
	player: AnimationPlayer,
	skeleton: Skeleton3D,
	clip: String,
	time: float,
) -> Array[Transform3D]:
	player.play(clip)
	player.pause()
	player.seek(time, true)
	skeleton.force_update_all_bone_transforms()
	var result: Array[Transform3D] = []
	for index: int in range(skeleton.get_bone_count()):
		result.append(skeleton.get_bone_global_pose(index))
	return result


## Verify library duration, reset coverage, root stability and explicit loop endpoints.
func check_library(
	library: AnimationLibrary,
	manifest: Dictionary,
	player: AnimationPlayer,
	skeleton: Skeleton3D,
	prefix: String,
) -> void:
	expect(library.get_animation_list().size() == manifest.clips.size(), prefix + " clip count")
	for spec: Dictionary in manifest.clips:
		var name: String = spec.name
		var clip: Animation = library.get_animation(name)
		expect(absf(clip.length - float(spec.duration_s)) < EPSILON, name + " duration")
		expect(clip.get_track_count() == 84, name + " complete bone channel reset")
		expect(
			clip.loop_mode == (Animation.LOOP_LINEAR if spec.loop else Animation.LOOP_NONE),
			name + " loop mode",
		)
		var first: Array[Transform3D] = sample(player, skeleton, prefix + name, 0.0)
		# Temporarily disable wrapping on an isolated duplicate to inspect the actual final keys.
		var duplicate: Animation = clip.duplicate(true)
		duplicate.loop_mode = Animation.LOOP_NONE
		var inspection: AnimationLibrary = (
			AnimationLibrary.new()  # gdstyle:ignore=quality/allocation-in-loop
		)
		inspection.add_animation(&"endpoint", duplicate)
		player.add_animation_library(&"inspection", inspection)
		var last: Array[Transform3D] = sample(player, skeleton, "inspection/endpoint", clip.length)
		if spec.loop:
			for index: int in range(first.size()):
				expect(first[index].is_equal_approx(last[index]), name + " seam " + str(index))
		player.remove_animation_library(&"inspection")
		for step: int in range(9):
			var time: float = clip.length * step / 8.0
			var pose: Array[Transform3D] = sample(player, skeleton, prefix + name, time)
			expect(pose[0].is_equal_approx(skeleton.get_bone_global_rest(0)), name + " fixed root")
			for matrix: Transform3D in pose:
				expect(matrix.is_finite(), name + " finite pose")


## Exercise one bounded lifecycle with retained identities and independent resource references.
func check() -> void:  # gdstyle:ignore=quality/max-local-variables
	var actor: PlayerCharacterVisual = load(ACTOR).instantiate()
	root.add_child(actor)
	var skeleton: Skeleton3D = actor.get_skeleton()
	var player: AnimationPlayer = actor.get_animation_player()
	var mesh: MeshInstance3D = skeleton.find_children("*", "MeshInstance3D", true, false)[0]
	var original_mesh: Mesh = mesh.mesh
	var skeleton_id: int = skeleton.get_instance_id()
	var player_id: int = player.get_instance_id()
	expect(actor.play_clip(&"run"), "play run")
	player.pause()
	player.seek(0.23, true)
	var template: PackedScene = load(SHARED_MODELS + "shared_humanoid_bind_v1.glb")
	expect(actor.apply_skin(template), "compatible different mesh skin swap")
	expect(mesh.mesh != original_mesh, "geometry actually changed")
	expect(actor.get_skeleton().get_instance_id() == skeleton_id, "skeleton retained")
	expect(actor.get_animation_player().get_instance_id() == player_id, "animation player retained")
	expect(absf(player.current_animation_position - 0.23) < EPSILON, "playback time retained")
	expect(
		actor.apply_skin(load("res://art/models/characters/coral_courier/coral_courier.glb")),
		"restore courier",
	)
	expect(mesh.mesh == original_mesh, "courier resource restored")
	expect(not actor.apply_skin(null), "null rejected")
	var bad: Node3D = template.instantiate()
	bad.scale = Vector3(2, 2, 2)
	var bad_scene: PackedScene = PackedScene.new()
	bad_scene.pack(bad)
	expect(not actor.apply_skin(bad_scene), "transformed hierarchy rejected")
	bad.free()
	for family: String in ["player"]:
		var library_path: String = SHARED_ANIMATIONS + family + "_v1.tres"
		var library: AnimationLibrary = load(library_path)
		var source_path: String = SHARED_SOURCE + "shared_humanoid_"
		source_path += family + "_motion_v1.json"
		var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(source_path))
		check_library(library, manifest, player, skeleton, family + "/")
	check_startup_appearance(template)
	check_source_tracks(player)
	check_attachments(actor, player, skeleton)
	check_layers(actor, player, skeleton)
	print("PLAYER_ASSET_CHECK ", JSON.stringify({"failures": failures, "player_clips": 24,
		"bones": 28, "skin_swap": "different geometry; stable skeleton/time"}))
	actor.free()
	quit(0 if failures.is_empty() else 1)


## Check each authored hand-to-grip frame against independent source world targets.
func check_attachments(
	actor: PlayerCharacterVisual,
	player: AnimationPlayer,
	skeleton: Skeleton3D,
) -> void:
	var profiles: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(
		"res://art/source/models/characters/coral_courier/weapon_profiles.json"))
	for name: String in profiles.profiles:
		expect(actor.select_grip(StringName(name)), "grip selection " + name)
		sample(player, skeleton, "player/" + name + "_hold", 0.0)
		var hand: Transform3D = skeleton.get_bone_global_pose(skeleton.find_bone("hand_r"))
		var grip: Transform3D = hand * actor.get_node("Sockets/WeaponMount").transform
		var source: Array = profiles.profiles[name].hold_grip_blender
		var expected: Vector3 = Vector3(source[0], source[2], -source[1])
		expect(grip.origin.distance_to(expected) < EPSILON, name + " source grip position")
		expect(grip.basis.is_equal_approx(Basis.IDENTITY), name + " grip -Z/+Y basis")


## Verify clip resets and disjoint upper/lower animation writers.
func check_layers(
	actor: PlayerCharacterVisual,
	player: AnimationPlayer,
	skeleton: Skeleton3D,
) -> void:
	var idle: Array[Transform3D] = sample(player, skeleton, "player/idle", 0.0)
	sample(player, skeleton, "player/launcher_hold", 0.0)
	var reset: Array[Transform3D] = sample(player, skeleton, "player/idle", 0.0)
	for index: int in range(idle.size()):
		expect(idle[index].is_equal_approx(reset[index]), "idle restores bone " + str(index))
	expect(actor.play_layered(&"walk_left", &"smg_hold"), "independent move/aim layers")
	var lower: AnimationPlayer = actor.get_node("LowerBodyPlayer")
	var upper: AnimationPlayer = actor.get_node("UpperBodyPlayer")
	lower.pause()
	upper.pause()
	lower.seek(0.25, true)
	upper.seek(0.0, true)
	var leg: Transform3D = skeleton.get_bone_pose(skeleton.find_bone("thigh_l"))
	upper.seek(0.75, true)
	expect(
		leg.is_equal_approx(skeleton.get_bone_pose(skeleton.find_bone("thigh_l"))),
		"upper layer preserves legs",
	)
	expect(actor.play_clip(&"idle"), "return from layers")
	expect(not upper.is_playing() and not lower.is_playing(), "full clip stops layer writers")


## Compare every extracted player key with the current imported source to detect stale caches.
func check_source_tracks(player: AnimationPlayer) -> void:
	var path: String = SHARED_MODELS + "shared_humanoid_player_motion_v1.glb"
	var source: Node = (load(path) as PackedScene).instantiate()
	var imported: AnimationPlayer = source.find_child("AnimationPlayer", true, false)
	var library: AnimationLibrary = player.get_animation_library(&"player")
	for name: StringName in library.get_animation_list():
		var actual: Animation = library.get_animation(name)
		var expected: Animation = imported.get_animation(name)
		expect(actual.get_track_count() == expected.get_track_count(), str(name) + " source tracks")
		for track: int in range(actual.get_track_count()):
			expect(actual.track_get_path(track) == expected.track_get_path(track), "source path")
			expect(
				actual.track_get_key_count(track) == expected.track_get_key_count(track),
				"source keys",
			)
			for key: int in range(actual.track_get_key_count(track)):
				expect(is_equal_approx(actual.track_get_key_time(track, key),
					expected.track_get_key_time(track, key)), "source key time")
				var value: Variant = actual.track_get_key_value(track, key)
				var reference: Variant = expected.track_get_key_value(track, key)
				expect(value.is_equal_approx(reference), str(name) + " source key value")
	source.free()


## Exercise the exported property before ready; initialization must actually change geometry.
func check_startup_appearance(template: PackedScene) -> void:
	var actor: PlayerCharacterVisual = load(ACTOR).instantiate()
	var skeleton: Skeleton3D = actor.get_node("PresentationAnchor/Visuals/Model/Rig/Skeleton3D")
	var mesh: MeshInstance3D = skeleton.find_children("*", "MeshInstance3D", true, false)[0]
	var original_mesh: Mesh = mesh.mesh
	var animation: AnimationPlayer = actor.get_node("AnimationPlayer")
	actor.appearance = template
	root.add_child(actor)
	expect(mesh.mesh != original_mesh, "exported appearance applied during ready")
	expect(actor.get_skeleton() == skeleton, "startup appearance retains skeleton")
	expect(actor.get_animation_player() == animation, "startup appearance retains animation")
	expect(actor.play_clip(&"walk"), "startup skin retains player library")
	animation.pause()
	animation.seek(0.25, true)
	expect(skeleton.get_bone_count() == 28, "startup skin retains 28 bones")
	actor.free()
