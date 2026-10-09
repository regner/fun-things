class_name S05Car
extends S04Kinematic
## Adds only fixture lifecycle collision to the unchanged S04 planar body API.


## Completes neutralization/collision/presentation before terminal state publication.
func apply_life(host: bool, phase: String) -> void:
	configure(host and phase == "LIVE")
	if host and phase == "WRECK":
		collision_layer = S04DriveRules.CAR_COLLISION_LAYER
		collision_mask = S04DriveRules.CAR_COLLISION_MASK

	visible = phase != "RETIRED"
	if phase == "RETIRED":
		retire()
