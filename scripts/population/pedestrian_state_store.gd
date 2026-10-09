class_name PedestrianStateStore
extends RefCounted
## Stores compact typed pedestrian fields by stable slot index.

var ids: PackedInt64Array = PackedInt64Array()
var positions: PackedVector2Array = PackedVector2Array()
var current_nodes: PackedInt32Array = PackedInt32Array()
var target_nodes: PackedInt32Array = PackedInt32Array()
var states: PackedByteArray = PackedByteArray()
var decision_phases: PackedByteArray = PackedByteArray()
var decision_counts: PackedInt32Array = PackedInt32Array()
var sequences: PackedInt64Array = PackedInt64Array()
var flee_until_ticks: PackedInt64Array = PackedInt64Array()
var threat_positions: PackedVector2Array = PackedVector2Array()
var aim_yaws: PackedFloat32Array = PackedFloat32Array()
var last_threat_ids: PackedInt64Array = PackedInt64Array()
var crossings: Array[StringName] = []


## Clears all parallel arrays without replacing the reusable store.
func clear() -> void:
	ids.clear()
	positions.clear()
	current_nodes.clear()
	target_nodes.clear()
	states.clear()
	decision_phases.clear()
	decision_counts.clear()
	sequences.clear()
	flee_until_ticks.clear()
	threat_positions.clear()
	aim_yaws.clear()
	last_threat_ids.clear()
	crossings.clear()


## Appends one complete slot while preserving equal parallel-array lengths.
func append(
	agent_id: int,
	start_node: int,
	position: Vector2,
	decision_phase: int,
	initial_state: int,
) -> void:
	ids.append(agent_id)
	positions.append(position)
	current_nodes.append(start_node)
	target_nodes.append(start_node)
	states.append(initial_state)
	decision_phases.append(decision_phase)
	decision_counts.append(0)
	sequences.append(0)
	flee_until_ticks.append(-1)
	threat_positions.append(Vector2.ZERO)
	aim_yaws.append(0.0)
	last_threat_ids.append(0)
	crossings.append(&"")
