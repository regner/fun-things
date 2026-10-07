@tool
class_name S01FixtureIdentity
extends Node3D
## Spike-only authored identity and root appearance tuning; never owns placement.

@export var world_id: StringName
@export var body_material: Material


## Applies the authored appearance after the linked imported model enters the tree.
func _ready() -> void:
	apply_appearance()


## Keeps variant tuning on the stable wrapper root, outside imported-child identities.
func apply_appearance() -> void:
	if body_material == null:
		return

	var body: MeshInstance3D = get_node("Visuals/Model/Body")
	body.material_override = body_material
