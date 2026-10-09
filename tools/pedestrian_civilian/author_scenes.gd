@tool
class_name PedestrianWorkerAuthoring
extends Node
## Editor-only authoring recipe. Saves linked scenes; never builds runtime render meshes.

const FAMILY: String = "res://scenes/prefabs/pedestrian_civilian/"
const PREVIEW: String = "res://tests/fixtures/pedestrian_civilian/pedestrian_worker_a_preview.tscn"
const MODEL: String = "res://art/models/pedestrian_civilian/pedestrian_worker_a.glb"
const LIBRARY: String = "res://art/animations/pedestrian_civilian/npc_locomotion_v1.tres"
const MATERIAL: String = "res://art/materials/pedestrian_worker_a_palette.tres"


## Build and save the approved worker resources within this verified private editor.
func build() -> Dictionary:
	assert(Engine.is_editor_hint())
	assert(ProjectSettings.globalize_path("res://").ends_with("brackett-pedestrian/"))
	for path: String in [FAMILY, LIBRARY.get_base_dir(), PREVIEW.get_base_dir()]:
		DirAccess.make_dir_recursive_absolute(path)
	var imported: PackedScene = load(MODEL)
	var model: Node3D = imported.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var imported_player: AnimationPlayer = model.find_child("AnimationPlayer", true, false)
	assert(imported_player != null)
	var library := AnimationLibrary.new()
	for clip: String in ["idle", "walk", "run", "death"]:
		assert(imported_player.has_animation(clip), "Missing imported clip: " + clip)
		var animation: Animation = imported_player.get_animation(clip).duplicate(true)
		animation.loop_mode = Animation.LOOP_NONE if clip == "death" else Animation.LOOP_LINEAR
		library.add_animation(clip, animation)
	assert(ResourceSaver.save(library, LIBRARY) == OK)
	library.take_over_path(LIBRARY)
	var material := ShaderMaterial.new()
	material.shader = load("res://art/materials/pedestrian_worker_a_palette.gdshader")
	assert(ResourceSaver.save(material, MATERIAL) == OK)
	material.take_over_path(MATERIAL)
	var worker := Node3D.new()
	worker.name = "PedestrianWorkerA"
	worker.set_script(load("res://scripts/presentation/pedestrian_civilian/pedestrian_worker_visual.gd"))
	worker.set("palette_material", material)
	worker.set("npc_library", library)
	var anchor := Node3D.new()
	anchor.name = "PresentationAnchor"
	own(worker, anchor, worker)
	var visuals := Node3D.new()
	visuals.name = "Visuals"
	own(anchor, visuals, worker)
	model.name = "Model"
	own(visuals, model, worker)
	save_scene(worker, FAMILY + "pedestrian_worker_a.tscn")
	worker.free()
	var packed: PackedScene = load(FAMILY + "pedestrian_worker_a.tscn")
	var preview := Node3D.new()
	preview.name = "PedestrianWorkerPreview"
	preview.set_script(load("res://tests/fixtures/pedestrian_civilian/pedestrian_worker_preview.gd"))
	var ground: Node3D = load("res://art/models/pedestrian_civilian/pedestrian_worker_stage.glb").instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	ground.name = "BlenderStage"
	own(preview, ground, preview)
	var workers := Node3D.new()
	workers.name = "Workers"
	own(preview, workers, preview)
	for index: int in 4:
		var actor: Node3D = packed.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
		actor.name = ["Idle", "Walk", "Run", "Death"][index]
		actor.position = Vector3((index - 1.5) * 2.2, 0, 0)
		actor.set("initial_clip", ["idle", "walk", "run", "death"][index])
		var palette: PackedColorArray = actor.get("palette").duplicate()
		if index == 1:
			palette[1] = Color("50ad98")
			palette[2] = Color("313c67")
			palette[4] = Color("cc9061")
		elif index == 2:
			palette[0] = Color("6a4433")
			palette[1] = Color("ca6279")
			palette[2] = Color("4d365e")
			palette[4] = Color("373f50")
		actor.set("palette", palette)
		own(workers, actor, preview)
	var game_camera := Camera3D.new()
	game_camera.name = "GameCamera"
	game_camera.position = Vector3(0, 47, 0)
	game_camera.rotation_degrees = Vector3(-90, 0, 0)
	game_camera.fov = 42
	game_camera.near = .1
	game_camera.far = 250
	game_camera.current = true
	own(preview, game_camera, preview)
	var overview := Camera3D.new()
	overview.name = "OverviewCamera"
	overview.position = Vector3(6, 5, -10)
	overview.fov = 42
	own(preview, overview, preview)
	overview.look_at_from_position(overview.position, Vector3(0, .7, 0))
	var sun := DirectionalLight3D.new()
	sun.name = "CityKey"
	sun.rotation_degrees = Vector3(-55, -35, 0)
	sun.light_color = Color("c8d5ef")
	sun.light_energy = 1.15
	sun.shadow_enabled = true
	sun.shadow_normal_bias = .1
	sun.shadow_bias = .015
	own(preview, sun, preview)
	var environment := WorldEnvironment.new()
	environment.name = "CityDusk"
	environment.environment = Environment.new()
	environment.environment.background_mode = Environment.BG_COLOR
	environment.environment.background_color = Color("17242f")
	environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.environment.ambient_light_color = Color("859eb5")
	environment.environment.ambient_light_energy = .7
	environment.environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	own(preview, environment, preview)
	var fill := OmniLight3D.new()
	fill.name = "CoralBounce"
	fill.position = Vector3(0, 4, -4)
	fill.light_color = Color("fd7f81")
	fill.light_energy = 2.5
	fill.omni_range = 14
	own(preview, fill, preview)
	var canvas := CanvasLayer.new()
	canvas.name = "ReviewLabels"
	own(preview, canvas, preview)
	var label := Label.new()
	label.name = "Context"
	label.text = (
		"OFF-SHIFT WORKER  /  idle · walk · run · death\n" +
		"Shared skeleton · separate NPC clips · independent instance colours\n" +
		"47 m · 42° · north-up · 1280×800   |   bounded 20-second preview"
	)
	label.position = Vector2(28, 24)
	own(canvas, label, preview)
	save_scene(preview, PREVIEW)
	preview.free()
	return {"pid": OS.get_process_id(), "project": ProjectSettings.globalize_path("res://"),
		"saved": [FAMILY + "pedestrian_worker_a.tscn", PREVIEW, LIBRARY, MATERIAL]}


## Keep authored children owned by the saved scene while preserving imported subtrees.
func own(parent: Node, child: Node, scene_root: Node) -> void:
	parent.add_child(child)
	child.owner = scene_root


## Serialize Godot-created resources with source-linked PackedScene instances intact.
func save_scene(scene_root: Node, path: String) -> void:
	var packed := PackedScene.new()
	assert(packed.pack(scene_root) == OK)
	assert(ResourceSaver.save(packed, path) == OK)
