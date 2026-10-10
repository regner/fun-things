extends GutTest
## Exercise the production tracer's inherited lifecycle and explicit segment boundary.

const TRACER: PackedScene = preload(
	"res://scenes/effects/weapon_effects/weapon_effects_a_tracer.tscn"
)
const BURST_SIZE: int = 40
const ASYNC_TIMEOUT_SECONDS: float = 5.0


## Require immediate visibility, occupied-root retention, one completion, and safe reuse.
func test_immediate_play_busy_completion_and_reuse() -> void:
	var tracer: Node3D = TRACER.instantiate()
	add_child_autofree(tracer)
	watch_signals(tracer)
	assert_false(tracer.visible)
	assert_false(tracer.is_active())
	assert_true(tracer.configure_segment(Vector3.ZERO, Vector3(0, 0, -35)))
	assert_true(tracer.play())
	assert_true(
		tracer.visible,
		"No timer, host verdict, or GPU-particle warmup precedes visibility",
	)
	assert_true(tracer.is_active())
	tracer.stop_emission()
	assert_true(tracer.is_active(), "Stopping continuous emission cannot erase a one-shot span")
	assert_false(tracer.play(), "A second event cannot reset an occupied root")
	assert_false(tracer.configure_segment(Vector3.ONE, Vector3(1, 1, -2)))
	assert_eq(tracer.position, Vector3.ZERO)
	assert_true(
		await wait_for_signal(
			Signal(tracer, &"finished"),
			ASYNC_TIMEOUT_SECONDS,
			"tracer completion",
		),
		"tracer did not finish within %.1f seconds" % ASYNC_TIMEOUT_SECONDS,
	)
	assert_false(tracer.is_active())
	assert_false(tracer.visible)
	assert_signal_emit_count(tracer, "finished", 1)
	assert_true(tracer.play())
	tracer.clear()
	assert_false(tracer.is_active())
	assert_false(tracer.visible)
	var witness: Node3D = TRACER.instantiate()
	add_child_autofree(witness)
	assert_true(witness.play())
	assert_true(
		await wait_for_signal(
			Signal(witness, &"finished"),
			ASYNC_TIMEOUT_SECONDS,
			"post-clear witness completion",
		),
		"post-clear witness did not finish within %.1f seconds" % ASYNC_TIMEOUT_SECONDS,
	)
	assert_signal_emit_count(tracer, "finished", 1, "Clear cancels completion, not gameplay")


## Map the authored unit -Z span to supplied endpoints without changing its cross-section.
func test_segment_transform_and_vertical_aim() -> void:
	var tracer: Node3D = TRACER.instantiate()
	add_child_autofree(tracer)
	for endpoint: Vector3 in [Vector3(45, 0, 0), Vector3(0, 45, 0), Vector3(0, -45, 0)]:
		assert_true(tracer.configure_segment(Vector3.ZERO, endpoint))
		assert_almost_eq(tracer.transform * Vector3.FORWARD, endpoint, Vector3.ONE * 0.0001)
		assert_almost_eq(tracer.basis.x.length(), 1.0, 0.0001)
		assert_almost_eq(tracer.basis.y.length(), 1.0, 0.0001)

	var start: Vector3 = Vector3(10, 1.2, 4)
	var end: Vector3 = Vector3(-12, 2, -9)
	assert_true(tracer.configure_segment(start, end))
	assert_almost_eq(tracer.transform * Vector3.FORWARD, end, Vector3.ONE * 0.0001)
	assert_eq(tracer.position, start)


## Reject malformed or unsupported cosmetic spans atomically; never query or clip gameplay.
func test_invalid_segment_retains_idle_transform() -> void:
	var tracer: Node3D = TRACER.instantiate()
	add_child_autofree(tracer)
	var original: Transform3D = tracer.transform
	for endpoint: Vector3 in [
		Vector3.ZERO, Vector3(0, 0, -46), Vector3(INF, 0, 0), Vector3(NAN, 0, 0),
	]:
		assert_false(tracer.configure_segment(Vector3.ZERO, endpoint))
		assert_eq(tracer.transform, original)

	assert_false(tracer.configure_segment(Vector3(INF, 0, 0), Vector3.ONE))
	assert_false(tracer.visible)


## Allocate one independent saved scene for every event, beyond an eight-slot cosmetic pool.
func test_every_event_has_shared_geometry_and_independent_lifetime() -> void:
	var tracers: Array[Node3D] = []
	var shared_mesh: Mesh
	for index: int in range(BURST_SIZE):
		var tracer: Node3D = TRACER.instantiate()
		add_child_autofree(tracer)
		tracers.append(tracer)
		var meshes: Array[Node] = tracer.find_children("*", "MeshInstance3D", true, false)
		assert_eq(meshes.size(), 1)
		var mesh: Mesh = (meshes[0] as MeshInstance3D).mesh
		if index == 0:
			shared_mesh = mesh

		assert_same(mesh, shared_mesh, "Per-event allocation does not duplicate draw geometry")
		assert_eq(tracer.find_children("*", "CollisionObject3D", true, false).size(), 0)
		assert_eq(tracer.find_children("*", "GPUParticles3D", true, false).size(), 0)
		assert_true(tracer.play())
		assert_true(tracer.visible)

	tracers[0].clear()
	assert_true(tracers[1].is_active(), "Clearing one event cannot erase another")
	assert_true(
		await wait_until(
			_all_tracers_inactive.bind(tracers),
			ASYNC_TIMEOUT_SECONDS,
			"burst tracer completion",
		),
		"burst tracers did not finish within %.1f seconds" % ASYNC_TIMEOUT_SECONDS,
	)
	for tracer: Node3D in tracers:
		assert_false(tracer.is_active())
		assert_false(tracer.visible)


## Reports when every retained tracer has completed its independent lifetime.
func _all_tracers_inactive(tracers: Array[Node3D]) -> bool:
	for tracer: Node3D in tracers:
		if tracer.is_active() or tracer.visible:
			return false

	return true


## The importer's static AABB encloses all draw vertices; no particle travel bound is needed.
func test_draw_bounds_and_saved_lifetime() -> void:
	var tracer: Node3D = TRACER.instantiate()
	add_child_autofree(tracer)
	assert_eq(tracer.settle_seconds, 0.075)
	assert_false(tracer.continuous)
	var model: MeshInstance3D = tracer.find_children("*", "MeshInstance3D", true, false)[0]
	var bounds: AABB = model.get_aabb()
	assert_almost_eq(bounds.position, Vector3(-0.06, -0.06, -1), Vector3.ONE * 0.0001)
	assert_almost_eq(bounds.end, Vector3(0.06, 0.079, 0), Vector3.ONE * 0.0001)
	assert_eq(model.mesh.get_surface_count(), 2)
	assert_true(tracer.configure_segment(Vector3.ZERO, Vector3(0, 0, -45)))
	var world_bounds: AABB = tracer.transform * bounds
	assert_almost_eq(world_bounds.end, Vector3(0.06, 0.079, 0), Vector3.ONE * 0.0001)
	assert_almost_eq(world_bounds.position, Vector3(-0.06, -0.06, -45), Vector3.ONE * 0.0001)


## Saving and reloading a configured instance retains the linked GLB, APIs, and endpoint pose.
func test_saved_roundtrip_keeps_import_ancestry() -> void:
	var tracer: Node3D = TRACER.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	assert_true(tracer.configure_segment(Vector3(2, 1, 3), Vector3(2, 1, -7)))
	var packed: PackedScene = PackedScene.new()
	assert_eq(packed.pack(tracer), OK)
	tracer.free()
	var path: String = "user://tracer_roundtrip.tscn"
	assert_eq(ResourceSaver.save(packed, path), OK)
	var reopened: PackedScene = ResourceLoader.load(
		path,
		"PackedScene",
		ResourceLoader.CACHE_MODE_IGNORE,
	)
	var instance: Node3D = reopened.instantiate()
	add_child_autofree(instance)
	assert_eq(
		instance.get_node("Model").scene_file_path,
		"res://art/models/effects/weapon_effects/weapon_effects_a_tracer.glb"
	)
	assert_almost_eq(
		instance.transform * Vector3.FORWARD, Vector3(2, 1, -7), Vector3.ONE * 0.0001
	)
	assert_true(instance.play())
	assert_true(instance.visible)
	assert_false(FileAccess.get_file_as_string(path).contains('[sub_resource type="ArrayMesh"'))
	assert_eq(DirAccess.remove_absolute(path), OK)
