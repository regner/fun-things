class_name S06Bake
extends Resource
## Editor-derived content handshake and road drawing; never silently rebaked at runtime.

@export var district_id: StringName = &"s06/district"
@export var topology_revision: int = 1
@export var tool_version: String = "s06-bake-1"
@export var fingerprint: String = ""
@export var roads: Array[Dictionary] = []
@export var world_xz_bounds_m: Rect2
