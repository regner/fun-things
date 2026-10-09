class_name SyntheticPopulationNavigation
extends PopulationNavigation
## Builds a deterministic 8x8 block grid with marked midline crossings for tests.

const GRID_WIDTH: int = 8
const GRID_HEIGHT: int = 8
const NODE_SPACING_M: float = 6.0

var _nodes: PackedInt32Array = PackedInt32Array()
var _positions: Dictionary[int, Vector2] = {}
var _neighbors: Dictionary[int, PackedInt32Array] = {}
var _link_crossings: Dictionary[String, StringName] = {}
var _crossing_ids: Array[StringName] = []
var _conflicts: Dictionary[StringName, Array] = {}


## Compiles the finite grid, marked links, and symmetric conflict pairs.
func _init() -> void:
	for row: int in GRID_HEIGHT:
		var crossing_id: StringName = StringName("crossing_%d" % row)
		_crossing_ids.append(crossing_id)
		_conflicts[crossing_id] = []
	for row: int in GRID_HEIGHT:
		for column: int in GRID_WIDTH:
			var node_id: int = _node_id(column, row)
			_nodes.append(node_id)
			_positions[node_id] = Vector2(column * NODE_SPACING_M, row * NODE_SPACING_M)
			_neighbors[node_id] = _grid_neighbors(column, row)
		if row % 2 == 0:
			_add_conflict(_crossing_ids[row], _crossing_ids[row + 1])
		var left: int = _node_id(3, row)
		var right: int = _node_id(4, row)
		_link_crossings[_link_key(left, right)] = _crossing_ids[row]
		_link_crossings[_link_key(right, left)] = _crossing_ids[row]


## Confirms this generated graph has its complete expected cardinality.
func is_valid() -> bool:
	return _nodes.size() == GRID_WIDTH * GRID_HEIGHT


## Returns all generated node identities.
func node_ids() -> PackedInt32Array:
	return _nodes.duplicate()


## Returns one generated world-XZ node position.
func node_position(node_id: int) -> Vector2:
	return _positions.get(node_id, Vector2(INF, INF))


## Returns one generated node's finite sidewalk links.
func sidewalk_neighbors(node_id: int) -> PackedInt32Array:
	return _neighbors.get(node_id, PackedInt32Array()).duplicate()


## Returns the marked crossing carried by one horizontal midline link.
func crossing_between(from_node: int, to_node: int) -> StringName:
	return _link_crossings.get(_link_key(from_node, to_node), &"")


## Returns all eight generated marked crossings.
func crossing_ids() -> Array[StringName]:
	return _crossing_ids.duplicate()


## Returns the synthetic crossing's symmetric traffic-conflict set.
func crossing_conflicts(crossing_id: StringName) -> Array[StringName]:
	return (_conflicts.get(crossing_id, []) as Array[StringName]).duplicate()


## Returns a row-major node identity for behavior test setup.
func grid_node(column: int, row: int) -> int:
	return _node_id(column, row)


## Returns the finite toroidal grid neighbors around one node.
func _grid_neighbors(column: int, row: int) -> PackedInt32Array:
	return PackedInt32Array([
		_node_id((column + 1) % GRID_WIDTH, row),
		_node_id((column - 1 + GRID_WIDTH) % GRID_WIDTH, row),
		_node_id(column, (row + 1) % GRID_HEIGHT),
		_node_id(column, (row - 1 + GRID_HEIGHT) % GRID_HEIGHT),
	])


## Adds one symmetric crossing conflict used by traffic-yield tests.
func _add_conflict(first: StringName, second: StringName) -> void:
	_conflicts[first].append(second)
	_conflicts[second].append(first)


## Encodes one directed edge without relying on NodePath or scene identity.
func _link_key(from_node: int, to_node: int) -> String:
	return "%d>%d" % [from_node, to_node]


## Maps a grid coordinate to its row-major node identity.
func _node_id(column: int, row: int) -> int:
	return row * GRID_WIDTH + column
