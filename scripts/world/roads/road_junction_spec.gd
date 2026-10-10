class_name RoadJunctionSpec
extends Resource
## Assigns stable project semantics to one addon intersection without owning its branches.

enum Mode {
	PREFAB,
	PROCEDURAL,
}
enum TrafficControl {
	NONE,
	SIGNAL,
}

@export var junction_id: StringName
@export var mode: Mode = Mode.PROCEDURAL
@export var prefab_id: StringName
@export var traffic_control: TrafficControl = TrafficControl.NONE
@export var marked_crossing_ids: Array[StringName] = []
@export var crossing_policy_id: StringName = &"standard"
@export var street_lighting: bool = true


## Returns whether identity, mode-specific fields, and crossing IDs are unambiguous.
func is_valid() -> bool:
	if junction_id == &"" or crossing_policy_id == &"":
		return false
	if mode == Mode.PREFAB and prefab_id == &"":
		return false
	if mode == Mode.PROCEDURAL and prefab_id != &"":
		return false
	var seen: Dictionary[StringName, bool] = {}
	for crossing_id: StringName in marked_crossing_ids:
		if crossing_id == &"" or seen.has(crossing_id):
			return false
		seen[crossing_id] = true
	return true
