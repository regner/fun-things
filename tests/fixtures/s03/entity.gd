class_name S03Entity
extends Node3D

var authoritative: bool = false
var configured: bool = false
var entity_id: int = 0
var ready_configured: bool = false


## Record whether ownership was configured before tree entry.
func _ready() -> void:
	ready_configured = configured
