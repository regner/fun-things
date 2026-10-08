@tool
class_name S06Link
extends Path3D
## Directed connectivity over a scene-authored curve; IDs survive reparenting.

@export var world_id: StringName
@export var from_id: StringName
@export var to_id: StringName
@export_enum("FOOT", "TRAFFIC", "ROAD") var kind: String = "FOOT"
@export var width_m: float = 0.0
