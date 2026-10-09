class_name PopulationSpatialGrid
extends RefCounted
## Reuses fixed-size XZ buckets for bounded pedestrian-neighbor queries.

const DEFAULT_CELL_SIZE_M: float = 1.5

var _cell_size_m: float = DEFAULT_CELL_SIZE_M
var _cells: Dictionary[Vector2i, Array] = {}


## Configures a positive bucket size and clears all previous entries.
func configure(cell_size_m: float) -> bool:
	if not is_finite(cell_size_m) or cell_size_m <= 0.0:
		return false

	_cell_size_m = cell_size_m
	clear()
	return true


## Removes entries while retaining this grid instance for the next motion tick.
func clear() -> void:
	_cells.clear()


## Inserts one slot into its current world-XZ bucket.
func insert(slot: int, position: Vector2) -> bool:
	if slot < 0 or not position.is_finite():
		return false

	var key: Vector2i = _key(position)
	if not _cells.has(key):
		_cells[key] = []
	_cells[key].append(slot)
	return true


## Returns candidates in cells intersecting a finite radius around a position.
func nearby(position: Vector2, radius_m: float) -> PackedInt32Array:
	var result: PackedInt32Array = PackedInt32Array()
	if not position.is_finite() or not is_finite(radius_m) or radius_m < 0.0:
		return result

	var center: Vector2i = _key(position)
	var reach: int = ceili(radius_m / _cell_size_m)
	for cell_x: int in range(center.x - reach, center.x + reach + 1):
		for cell_y: int in range(center.y - reach, center.y + reach + 1):
			var key: Vector2i = Vector2i(cell_x, cell_y)
			if not _cells.has(key):
				continue
			for slot: int in _cells[key]:
				result.append(slot)

	return result


## Maps one world-XZ position to its stable grid cell.
func _key(position: Vector2) -> Vector2i:
	return Vector2i(
		floori(position.x / _cell_size_m),
		floori(position.y / _cell_size_m),
	)
