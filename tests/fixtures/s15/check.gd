extends SceneTree
## Headless public-API and saved-composition check for the S15 effect fixture.

const EFFECT_PATHS: Array[String] = [
	"res://tests/fixtures/s15/explosion.tscn",
	"res://tests/fixtures/s15/muzzle_flash.tscn",
	"res://tests/fixtures/s15/tracer.tscn",
	"res://tests/fixtures/s15/impact_puff.tscn",
	"res://tests/fixtures/s15/rocket_trail.tscn",
	"res://tests/fixtures/s15/shooter.tscn",
	"res://tests/fixtures/s15/rocket.tscn",
]


## Loads every reusable saved effect and validates the stress scene through public APIs.
func _initialize() -> void:
	var failures: Array[String] = []
	for path: String in EFFECT_PATHS:
		var packed: PackedScene = load(path)
		if packed == null:
			failures.append("failed to load %s" % path)
			continue
		var instance: Node = packed.instantiate()
		if instance == null:
			failures.append("failed to instantiate %s" % path)
		instance.free()

	var stress_scene: PackedScene = load("res://tests/fixtures/s15/stress.tscn")
	var stress: Node = stress_scene.instantiate() if stress_scene != null else null
	if stress == null:
		failures.append("failed to instantiate stress scene")
	else:
		var explosion_count: int = stress.get_node("Effects/Explosions").get_child_count()
		var shooter_count: int = stress.get_node("Effects/Shooters").get_child_count()
		var rocket_count: int = stress.get_node("Effects/Rockets").get_child_count()
		if [explosion_count, shooter_count, rocket_count] != [24, 4, 16]:
			failures.append("unexpected stress counts: %s" % [
				explosion_count, shooter_count, rocket_count])
		var explosion: Node = stress.get_node("Effects/Explosions").get_child(0)
		if not explosion.has_method("set_quality") or not explosion.has_method("trigger"):
			failures.append("explosion public API missing")
		stress.free()

	print(JSON.stringify({ "ok": failures.is_empty(), "failures": failures }))
	quit(0 if failures.is_empty() else 1)
