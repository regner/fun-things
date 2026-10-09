class_name PopulationNavigation
extends RefCounted
## Defines the injected foot graph consumed by host-owned pedestrian decisions.


## Reports whether all nodes, sidewalk links, crossings, and conflict sets are usable.
func is_valid() -> bool:
	return false


## Returns the finite node identifiers available to population slots.
func node_ids() -> PackedInt32Array:
	return PackedInt32Array()


## Returns the world-XZ position for a valid node identifier.
func node_position(_node_id: int) -> Vector2:
	return Vector2.ZERO


## Returns the finite sidewalk neighbors for a valid node identifier.
func sidewalk_neighbors(_node_id: int) -> PackedInt32Array:
	return PackedInt32Array()


## Returns a marked-crossing identifier or an empty name for one directed link.
func crossing_between(_from_node: int, _to_node: int) -> StringName:
	return &""


## Returns every marked crossing exposed by this graph.
func crossing_ids() -> Array[StringName]:
	return []


## Returns crossings that cannot be occupied with the named crossing.
func crossing_conflicts(_crossing_id: StringName) -> Array[StringName]:
	return []
