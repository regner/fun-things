class_name S10Pedestrian
extends CharacterBody3D
## Capsule-only pedestrian presentation and bounded motion adapter for the S10 experiment.


## Installs a graph-owned spawn pose without giving presentation ownership of AI state.
func install_position(world_position: Vector3) -> void:
	global_position = world_position
	velocity = Vector3.ZERO
	rotation = Vector3.ZERO


## Applies graph-constrained displacement directly for the query-only motion option.
func advance_graph(displacement: Vector3) -> Vector3:
	global_position += displacement
	velocity = displacement * 60.0
	return global_position


## Applies the same displacement through CharacterBody3D collision motion.
func advance_character(displacement: Vector3) -> Vector3:
	var collision: KinematicCollision3D = move_and_collide(displacement)
	velocity = displacement * 60.0
	if collision != null:
		velocity = velocity.slide(collision.get_normal())

	return global_position


## Converts a live capsule into a retained, noncolliding dead presentation.
func retain_dead() -> void:
	velocity = Vector3.ZERO
	collision_layer = 0
	collision_mask = 0
	rotation.x = PI * 0.5
