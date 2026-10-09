class_name AssetLineOfSightProbe
extends Node
## Test-only facing ray used by delivered-asset line-of-sight checks.

const WORLD_LAYER: int = 1
const ACTOR_LAYER: int = 2
const QUERY_MASK: int = WORLD_LAYER | ACTOR_LAYER
const ORIGIN_HEIGHT_M: float = 1.2

@export var range_m: float = 18.0
@export var interval_seconds: float = 0.25

var last_hit: Node
var last_endpoint: Vector3 = Vector3.ZERO
var _cooldown_seconds: float = 0.0


## Resolves centre-to-muzzle obstruction before the forward query used by the fixtures.
func step(actor: AssetScaleClearanceProbe, firing: bool, delta_seconds: float) -> void:
	_cooldown_seconds = maxf(0.0, _cooldown_seconds - delta_seconds)
	if not firing or _cooldown_seconds > 0.0:
		return

	_cooldown_seconds = interval_seconds
	var origin: Vector3 = actor.global_position + Vector3.UP * ORIGIN_HEIGHT_M
	var muzzle: Vector3 = actor.muzzle_position()
	var endpoint: Vector3 = muzzle - actor.global_basis.z * range_m
	var space: PhysicsDirectSpaceState3D = actor.get_world_3d().direct_space_state
	var query: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(
		origin, muzzle, QUERY_MASK, [actor.get_rid()]
	)
	query.hit_from_inside = true
	var result: Dictionary = space.intersect_ray(query)
	if result.is_empty():
		query.from = muzzle
		query.to = endpoint
		result = space.intersect_ray(query)

	last_hit = result.get("collider") as Node
	last_endpoint = result.get("position", endpoint)
