class_name S06Minimap
extends Control
## Saved UI draws CityData roads and one supplied controlled-body marker; no layout writer.

@export var pixels_per_metre: float = 3.0
@export var map_origin_px: Vector2 = Vector2(80, 80)

var roads: Array[Dictionary] = []
var marker: Vector3 = Vector3.ZERO
var content_valid: bool = false


## Draws shared derived roads and the sole controlled-entity marker in the saved Control.
func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Color("#123646"))
	if not content_valid:
		return

	for road: Dictionary in roads:
		var projected: PackedVector2Array = []
		for point: Vector3 in road.points:
			projected.append(project_point(point))
		draw_polyline(projected, Color("#85929d"), road.width_m * pixels_per_metre)

	draw_circle(project_point(marker), 3.0, Color("#ff725d"))


## Installs validated shared road data; stale content clears drawing instead of fallback.
func bind_city(city: S06City) -> String:
	roads.clear()
	var data: Dictionary = city.map_data()
	content_valid = data.code == "OK"
	if content_valid:
		roads.assign(data.road_polylines_m)
	queue_redraw()
	return data.code


## Supplies presentation state without deciding route or movement.
func set_marker(world_position: Vector3) -> void:
	marker = world_position
	queue_redraw()


## Projects world XZ at the saved map origin/scale.
func project_point(point: Vector3) -> Vector2:
	return map_origin_px + Vector2(point.x, point.z) * pixels_per_metre
