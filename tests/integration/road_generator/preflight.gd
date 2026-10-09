extends Node3D
## Exercises the vendored road generator's production-facing construction and persistence seams.

const CUSTOM_CONTAINER := preload("res://addons/road-generator/custom_containers/4way_1x1.tscn")
const EXPECTED_MINIMUM_LANES := 4
const EXPECTED_MINIMUM_MESHES := 3

var _result_path := ""
var _saved_scene_path := ""
var _capture_path := ""
var _windowed := false


## Builds the fixture, verifies save/reload, and writes a machine-readable result.
func _ready() -> void:
	_parse_arguments()
	var failures: Array[String] = []
	if _result_path.is_empty() or _saved_scene_path.is_empty():
		failures.append("missing required --result or --saved-scene argument")
	var fixture_result := await _build_and_persist(failures)
	if _windowed:
		await _capture_frame(failures)

	var result := {
		"ok": failures.is_empty(),
		"engine": Engine.get_version_info().get("string", "unknown"),
		"display_server": DisplayServer.get_name(),
		"windowed": _windowed,
		"live_counts": fixture_result["live_counts"],
		"reloaded_counts": fixture_result["reloaded_counts"],
		"saved_scene": _saved_scene_path,
		"capture": _capture_path,
		"failures": failures,
	}
	_write_result(result)
	print("ROAD_GENERATOR_PREFLIGHT ", JSON.stringify(result))
	for child in get_children():
		child.queue_free()
	await get_tree().process_frame
	await get_tree().process_frame
	get_tree().quit(0 if failures.is_empty() else 1)


## Creates all requested road forms and persists the resulting live addon scene.
func _build_and_persist(failures: Array[String]) -> Dictionary:
	var roads_root := Node3D.new()
	roads_root.name = "RoadPreflight"
	add_child(roads_root)
	var manager := RoadManager.new()
	manager.name = "RoadManager"
	manager.auto_refresh = false
	roads_root.add_child(manager)
	manager.owner = roads_root

	var road := await _build_road(manager)
	var intersection := await _build_intersection(manager)
	var custom := CUSTOM_CONTAINER.instantiate()
	custom.name = "Custom4Way"
	custom.position = Vector3(50.0, 0.0, 0.0)
	manager.add_child(custom)
	custom.owner = roads_root
	await get_tree().process_frame
	manager.rebuild_all_containers(true)
	await get_tree().process_frame

	var live_counts := _counts(roads_root)
	_validate_live_fixture(road, intersection, custom, live_counts, failures)
	var reloaded_counts := await _persist_and_reload(roads_root, failures)
	return {
		"live_counts": live_counts,
		"reloaded_counts": reloaded_counts,
	}


## Packs, saves, and reloads the generated road source scene.
func _persist_and_reload(roads_root: Node, failures: Array[String]) -> Dictionary:
	var packed := PackedScene.new()
	var pack_error := packed.pack(roads_root)
	if pack_error != OK:
		failures.append("PackedScene.pack failed: %s" % error_string(pack_error))
	var save_error := ResourceSaver.save(packed, _saved_scene_path)
	if save_error != OK:
		failures.append("ResourceSaver.save failed: %s" % error_string(save_error))
		return {}
	return await _reload_counts(failures)


## Reads only the bounded output arguments supplied by the preflight runner.
func _parse_arguments() -> void:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--result="):
			_result_path = argument.trim_prefix("--result=")
		elif argument.begins_with("--saved-scene="):
			_saved_scene_path = argument.trim_prefix("--saved-scene=")
		elif argument.begins_with("--capture="):
			_capture_path = argument.trim_prefix("--capture=")
		elif argument == "--windowed-check":
			_windowed = true


## Creates one ordinary two-point road with generated lanes and edge curves.
func _build_road(manager: RoadManager) -> RoadContainer:
	var container := RoadContainer.new()
	container.name = "GeneratedRoad"
	container.generate_ai_lanes = true
	container.create_edge_curves = true
	container._auto_refresh = false
	manager.add_child(container)
	container.owner = manager.owner
	await get_tree().process_frame
	container.setup_road_container()

	var start := RoadPoint.new()
	start.name = "Start"
	start.position = Vector3(-18.0, 0.0, -24.0)
	var finish := RoadPoint.new()
	finish.name = "Finish"
	finish.position = Vector3(18.0, 0.0, -24.0)
	finish.rotation_degrees.y = -90.0
	start.rotation_degrees.y = -90.0
	container.add_child(start)
	container.add_child(finish)
	start.owner = container.owner
	finish.owner = container.owner
	start.next_pt_init = start.get_path_to(finish)
	finish.prior_pt_init = finish.get_path_to(start)
	container.update_edges()
	container.rebuild_segments(true)
	return container


## Creates a valid four-branch procedural intersection and its generated turn lanes.
func _build_intersection(manager: RoadManager) -> RoadContainer:
	var container := RoadContainer.new()
	container.name = "ProceduralIntersection"
	container.generate_ai_lanes = true
	container.create_edge_curves = true
	container._auto_refresh = false
	manager.add_child(container)
	container.owner = manager.owner
	await get_tree().process_frame
	container.setup_road_container()

	var intersection := RoadIntersection.new()
	intersection.name = "Intersection"
	container.add_child(intersection)
	intersection.owner = container.owner
	var points: Array[RoadPoint] = [
		_create_branch(container, "Branch0", Vector3(0.0, 0.0, -20.0), 0.0),
		_create_branch(container, "Branch1", Vector3(0.0, 0.0, 20.0), 180.0),
		_create_branch(container, "Branch2", Vector3(20.0, 0.0, 0.0), -90.0),
		_create_branch(container, "Branch3", Vector3(-20.0, 0.0, 0.0), 90.0),
	]
	intersection.edge_points = points
	for point in points:
		point.next_pt_init = point.get_path_to(intersection)
	container.update_edges()
	container.rebuild_segments(true)
	return container


## Adds one configured branch without allocating road nodes inside a loop.
func _create_branch(
	container: RoadContainer, branch_name: String, position: Vector3, yaw_degrees: float
) -> RoadPoint:
	var point := RoadPoint.new()
	point.name = branch_name
	point.position = position
	point.rotation_degrees.y = yaw_degrees
	container.add_child(point)
	point.owner = container.owner
	return point


## Verifies each requested live feature without depending on private generated node names.
func _validate_live_fixture(
	road: RoadContainer,
	intersection: RoadContainer,
	custom: Node,
	counts: Dictionary,
	failures: Array[String]
) -> void:
	if road.find_children("*", "RoadLane", true, false).is_empty():
		failures.append("ordinary road generated no lanes")
	if intersection.find_children("*", "RoadIntersection", true, false).is_empty():
		failures.append("procedural intersection was not retained")
	if intersection.find_children("*", "RoadLane", true, false).is_empty():
		failures.append("procedural intersection generated no lanes")
	if custom.find_children("*", "RoadLane", true, false).is_empty():
		failures.append("custom container has no authored lanes")
	if counts["lanes"] < EXPECTED_MINIMUM_LANES:
		failures.append("too few total lanes: %d" % counts["lanes"])
	if counts["meshes"] < EXPECTED_MINIMUM_MESHES:
		failures.append("too few generated/imported meshes: %d" % counts["meshes"])


## Reloads the saved scene from disk and verifies its essential generated content.
func _reload_counts(failures: Array[String]) -> Dictionary:
	var resource := ResourceLoader.load(
		_saved_scene_path, "PackedScene", ResourceLoader.CACHE_MODE_REPLACE
	)
	if not resource is PackedScene:
		failures.append("saved scene did not reload as PackedScene")
		return {}
	var reloaded := (resource as PackedScene).instantiate()
	add_child(reloaded)
	await get_tree().process_frame
	var counts := _counts(reloaded)
	if counts["containers"] < 3:
		failures.append("reloaded scene lost road containers")
	if counts["lanes"] < EXPECTED_MINIMUM_LANES:
		failures.append("reloaded scene lost lanes")
	if counts["meshes"] < EXPECTED_MINIMUM_MESHES:
		failures.append("reloaded scene lost meshes")
	reloaded.queue_free()
	await get_tree().process_frame
	return counts


## Captures a presented frame during the capped graphical preflight.
func _capture_frame(failures: Array[String]) -> void:
	if _capture_path.is_empty():
		failures.append("windowed check requires --capture")
		return
	var camera := Camera3D.new()
	camera.position = Vector3(46.0, 42.0, 46.0)
	add_child(camera)
	camera.look_at(Vector3.ZERO)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-55.0, -35.0, 0.0)
	add_child(light)
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	if image.is_empty():
		failures.append("windowed viewport capture was empty")
		return
	var capture_error := image.save_png(_capture_path)
	if capture_error != OK:
		failures.append("capture save failed: %s" % error_string(capture_error))


## Counts public addon types and visible mesh instances in one subtree.
func _counts(root: Node) -> Dictionary:
	return {
		"containers": root.find_children("*", "RoadContainer", true, false).size(),
		"intersections": root.find_children("*", "RoadIntersection", true, false).size(),
		"lanes": root.find_children("*", "RoadLane", true, false).size(),
		"meshes": root.find_children("*", "MeshInstance3D", true, false).size(),
		"points": root.find_children("*", "RoadPoint", true, false).size(),
	}


## Retains the result even when one of the semantic checks fails.
func _write_result(result: Dictionary) -> void:
	if _result_path.is_empty():
		return
	var file := FileAccess.open(_result_path, FileAccess.WRITE)
	if file == null:
		push_error("cannot write preflight result: %s" % _result_path)
		return
	file.store_string(JSON.stringify(result, "\t") + "\n")
