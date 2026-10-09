class_name SyntheticHostNavigation
extends PopulationNavigation
## Supplies a deterministic 8x8 synthetic graph for repeatable host-budget tracking.

const GRID_WIDTH: int = 8
const GRID_HEIGHT: int = 8
const NODE_SPACING_M: float = 6.0

var _nodes: PackedInt32Array = PackedInt32Array()
var _positions: Dictionary[int, Vector2] = {}
var _neighbors: Dictionary[int, PackedInt32Array] = {}
var _link_crossings: Dictionary[String, StringName] = {}
var _crossing_ids: Array[StringName] = []
var _conflicts: Dictionary[StringName, Array] = {}


## Builds one finite toroidal graph with eight marked midline crossings.
func _init() -> void:
	for row: int in GRID_HEIGHT:
		var crossing_id: StringName = StringName("crossing_%d" % row)
		_crossing_ids.append(crossing_id)
		_conflicts[crossing_id] = []
	for row: int in GRID_HEIGHT:
		for column: int in GRID_WIDTH:
			var node_id: int = grid_node(column, row)
			_nodes.append(node_id)
			_positions[node_id] = Vector2(column * NODE_SPACING_M, row * NODE_SPACING_M)
			_neighbors[node_id] = _grid_neighbors(column, row)
		if row % 2 == 0:
			_add_conflict(_crossing_ids[row], _crossing_ids[row + 1])
		var left: int = grid_node(3, row)
		var right: int = grid_node(4, row)
		_link_crossings[_link_key(left, right)] = _crossing_ids[row]
		_link_crossings[_link_key(right, left)] = _crossing_ids[row]


## Confirms the complete expected synthetic cardinality.
func is_valid() -> bool:
	return _nodes.size() == GRID_WIDTH * GRID_HEIGHT


## Returns every synthetic node identity.
func node_ids() -> PackedInt32Array:
	return _nodes.duplicate()


## Resolves one node to its finite world-XZ position.
func node_position(node_id: int) -> Vector2:
	return _positions.get(node_id, Vector2(INF, INF))


## Returns the four toroidal sidewalk neighbors for one node.
func sidewalk_neighbors(node_id: int) -> PackedInt32Array:
	return _neighbors.get(node_id, PackedInt32Array()).duplicate()


## Returns a marked crossing for horizontal midline links only.
func crossing_between(from_node: int, to_node: int) -> StringName:
	return _link_crossings.get(_link_key(from_node, to_node), &"")


## Returns every synthetic marked crossing identity.
func crossing_ids() -> Array[StringName]:
	return _crossing_ids.duplicate()


## Returns the symmetric crossing-conflict set.
func crossing_conflicts(crossing_id: StringName) -> Array[StringName]:
	return (_conflicts.get(crossing_id, []) as Array[StringName]).duplicate()


## Maps one grid coordinate to its stable row-major identity.
func grid_node(column: int, row: int) -> int:
	return row * GRID_WIDTH + column


## Builds four finite toroidal links for a grid coordinate.
func _grid_neighbors(column: int, row: int) -> PackedInt32Array:
	return PackedInt32Array([
		grid_node((column + 1) % GRID_WIDTH, row),
		grid_node((column - 1 + GRID_WIDTH) % GRID_WIDTH, row),
		grid_node(column, (row + 1) % GRID_HEIGHT),
		grid_node(column, (row - 1 + GRID_HEIGHT) % GRID_HEIGHT),
	])


## Adds one symmetric crossing conflict.
func _add_conflict(first: StringName, second: StringName) -> void:
	_conflicts[first].append(second)
	_conflicts[second].append(first)


## Encodes a directed graph link independently from scene identity.
func _link_key(from_node: int, to_node: int) -> String:
	return "%d>%d" % [from_node, to_node]
