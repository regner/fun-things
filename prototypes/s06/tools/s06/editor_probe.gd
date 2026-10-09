@tool
class_name S06EditorProbe
extends S04EditorProbe
## Editor-only bridge for linked GLBs, Path3D control points and explicit bake/save operations.

const FIXTURE: String = "res://tests/fixtures/s06/"


## Editor-only finite allocations author stable anchors and curves in one bounded editor mutation
## batch.
func author_topology(spec: Dictionary) -> void:
	assert(spec.anchors.size() <= S06City.MAX_ANCHORS)
	assert(spec.links.size() <= S06City.MAX_LINKS)
	var edited: Node = EditorInterface.get_edited_scene_root()
	var parent: Node3D = edited.get_node("Topology")
	for row: Dictionary in spec.anchors:
		var anchor: S06Anchor = S06Anchor.new()  # gdstyle:ignore=quality/allocation-in-loop
		anchor.name = row.name
		anchor.world_id = row.id
		anchor.position = Vector3(row.point[0], row.point[1], row.point[2])
		parent.add_child(anchor)
		anchor.owner = edited
	for row: Dictionary in spec.links:
		var link: S06Link = S06Link.new()  # gdstyle:ignore=quality/allocation-in-loop
		link.name = row.name
		link.world_id = row.id
		link.from_id = row.from
		link.to_id = row.to
		link.kind = row.kind
		link.width_m = row.get("width_m", 0.0)
		link.curve = Curve3D.new()  # gdstyle:ignore=quality/allocation-in-loop
		link.curve.bake_interval = 0.25
		for point: Dictionary in row.points:
			link.curve.add_point(_vector(point.p), _vector(point.get("in", [0, 0, 0])),
				_vector(point.get("out", [0, 0, 0])))
		parent.add_child(link)
		link.owner = edited
	EditorInterface.mark_scene_as_unsaved()


## Saves an explicit editor bake and assigns it; gameplay never calls this operation.
func bake_city(path: String) -> Dictionary:
	var edited: Node = EditorInterface.get_edited_scene_root()
	var city: S06City = edited.get_node("City")
	var result: S06Bake = city.bake_content()
	if result == null:
		return { "code": "CONTENT_INVALID" }

	var error: Error = ResourceSaver.save(result, path)
	if error != OK:
		return { "code": "SAVE_FAILED", "error": error }

	city.derived = ResourceLoader.load(path, "", ResourceLoader.CACHE_MODE_REPLACE)
	EditorInterface.mark_scene_as_unsaved()
	return { "code": city.validate_content(), "signature": result.fingerprint }


## Reports saved derived-data validation and both shared map and route boundaries.
func inspect_city() -> Dictionary:
	var edited: Node = EditorInterface.get_edited_scene_root()
	var city: S06City = edited.get_node("City")
	return { "validation": city.validate_content(), "signature": city.signature(),
		"map": city.map_data(), "foot": city.route("FOOT", &"s06/foot/west",
			&"s06/foot/east"), "traffic": city.route("TRAFFIC",
			&"s06/lane/west", &"s06/lane/north") }


## Creates values for editor-authored curve controls; does not run during gameplay.
func _vector(values: Array) -> Vector3:
	return Vector3(values[0], values[1], values[2])
