extends SceneTree
## Independent lifecycle negatives and mid-route cancellation, using only the saved fixture APIs.

const FIXTURE: String = "res://tests/fixtures/s07_driver/intersection.tscn"
const CANCEL_AFTER_TICKS: int = 30

var checks: Array[String] = []
var failures: Array[String] = []


## Starts checks only after a tree exists for the saved fixture lifecycle.
func _initialize() -> void:
	_run.call_deferred()


## Tests ownership, stale admission, one-shot fencing, actual cancellation and saved reload.
func _run() -> void:
	var fixture: S07DriverFixture = load(FIXTURE).instantiate()
	fixture.authoritative = false
	root.add_child(fixture)
	await process_frame
	await _check_initial_lifecycle(fixture)
	await _check_fresh_reload()
	var file: FileAccess = FileAccess.open("res://guards.json", FileAccess.WRITE)
	file.store_string(JSON.stringify({ "checks": checks, "failures": failures }, "\t") + "\n")
	file.close()
	quit(0 if failures.is_empty() else 1)


## Checks admission, one-shot fencing, motion cancellation, and retirement on one instance.
func _check_initial_lifecycle(fixture: S07DriverFixture) -> void:
	_expect(fixture.saved_start_valid(), "pre-admission saved starts and passive collision")
	_expect(fixture.begin_route("foot") == "NOT_OWNER", "passive authority refused")
	fixture.authoritative = true
	_expect(fixture.begin_route("unknown") == "NO_ROUTE", "unknown route refused")
	var city: S06City = fixture.get_node("City")
	var saved: S06Bake = city.derived
	city.derived = null
	_expect(fixture.begin_route("foot") == "CONTENT_INVALID", "missing bake refused before motion")
	city.derived = saved
	_expect(fixture.begin_route("foot") == "OK", "restored content route admitted")
	_expect(
		fixture.begin_route("east_to_north") == "RELOAD_REQUIRED",
		"concurrent/reused binding refused",
	)
	for tick: int in CANCEL_AFTER_TICKS:
		await physics_frame  # gdstyle:ignore=quality/await-in-loop

	var moved: Dictionary = fixture.body_state("foot")
	_expect(moved.position.x > -19.0, "actual nonempty motion before cancellation")
	fixture.cancel_owned()
	_expect(fixture.passive_valid(), "cancellation clears producer and collision admission")
	_expect(
		fixture.body_state("foot").velocity == Vector3.ZERO,
		"cancellation neutralizes velocity",
	)
	_expect(fixture.begin_route("foot") == "RELOAD_REQUIRED", "cancelled fixture cannot restart")
	await physics_frame
	_expect(
		fixture.body_state("foot").position == moved.position,
		"no stale command moves cancelled body",
	)
	fixture.queue_free()
	await process_frame
	_expect(not is_instance_valid(fixture), "retired fixture freed before reload")


## Checks that a fresh saved instance restores content, physical state, and passive roles.
func _check_fresh_reload() -> void:
	var fresh: S07DriverFixture = load(FIXTURE).instantiate()
	fresh.authoritative = true
	root.add_child(fresh)
	await process_frame
	_expect(
		fresh.saved_start_valid(),
		"fresh saved reload restores all positions yaw velocity roles",
	)
	_expect(
		(fresh.get_node("City") as S06City).validate_content() == "OK",
		"fresh content revalidated",
	)
	fresh.cancel_owned()
	fresh.queue_free()
	await process_frame
	_expect(not is_instance_valid(fresh), "fresh fixture teardown complete")


## Records every literal public-boundary expectation and any failure.
func _expect(condition: bool, label: String) -> void:
	checks.append(label)
	if not condition:
		failures.append(label)
