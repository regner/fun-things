class_name S07DriverFixture
extends S06Fixture
## One-shot inherited S06 authority; repetition requires teardown and saved-scene reload.

const CASES: Array[String] = ["foot", "east_to_north", "west_to_south"]
const EXPECTED_SIGNATURE: String = (
	"eaec39bbde6bd39e0b9c6c5c005f6285be49881faeb3a2cbfa02363014ff1604"
)
const START_TOLERANCE_M: float = 0.001
const START_YAW_TOLERANCE_RAD: float = 0.001

var used: bool = false


## Refuses reused, passive, stale or non-restored fixtures before binding owned commands.
func begin_route(case_name: String) -> String:
	if used:
		return "RELOAD_REQUIRED"
	if not authoritative:
		return "NOT_OWNER"
	if case_name not in CASES:
		return "NO_ROUTE"

	var city: S06City = $City
	if city.validate_content() != "OK" or city.signature() != EXPECTED_SIGNATURE:
		return "CONTENT_INVALID"
	if not saved_start_valid():
		return "START_INVALID"

	used = true
	return start_route(case_name)


## Checks all saved starts, neutral velocities and passive admission before each fresh route.
func saved_start_valid() -> bool:
	var positions: Array[Vector3] = [
		Vector3(-20, 0.001, 6.5), Vector3(-20, 0, 2.25), Vector3(20, 0, -2.25)]
	var yaws: Array[float] = [-PI / 2.0, -PI / 2.0, PI / 2.0]
	for index: int in CASES.size():
		var state: Dictionary = body_state(CASES[index])
		if state.position.distance_to(positions[index]) > START_TOLERANCE_M:
			return false
		if absf(wrapf(state.yaw - yaws[index], -PI, PI)) > START_YAW_TOLERANCE_RAD:
			return false
		if state.velocity != Vector3.ZERO:
			return false

	return passive_valid()


## Observes inherited pre-tree collision roles and cleared command state without rewriting them.
func passive_valid() -> bool:
	var person: S02ActorMotion = $Person
	var west: S04Kinematic = $CarWest
	var east: S04Kinematic = $CarEast
	return (active_body == null and not controller.enabled and controller.points.is_empty()
		and person.collision_layer == 0 and person.collision_mask == 0
		and west.collision_layer == 0 and west.collision_mask == 0
		and east.collision_layer == 0 and east.collision_mask == 0
		and not west.simulation_enabled and not east.simulation_enabled)


## Cancels producer state and neutralizes every owned body before fixture lifetime retirement.
func cancel_owned() -> void:
	stop_route()
	($Person as S02ActorMotion).neutralize()
	($CarWest as S04Kinematic).neutralize()
	($CarEast as S04Kinematic).neutralize()
	used = true
