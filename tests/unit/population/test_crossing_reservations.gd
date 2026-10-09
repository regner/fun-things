extends GutTest
## Verifies finite crossing queues, conflict yielding, and reservation expiry.

var _navigation: SyntheticPopulationNavigation
var _reservations: CrossingReservations


## Creates one fresh synthetic graph and finite reservation owner per test.
func before_each() -> void:
	_navigation = SyntheticPopulationNavigation.new()
	_reservations = CrossingReservations.new()
	assert_true(_reservations.configure(_navigation, 2, 2, 6, 5))


## Caps queue admission and exposes active conflicts only to the AI-traffic query.
func test_queue_capacity_and_conflict_query_are_finite() -> void:
	assert_eq(
		_reservations.request(&"crossing_0", 1, 0),
		CrossingReservations.STATUS_ACTIVE,
	)
	assert_eq(
		_reservations.request(&"crossing_0", 2, 0),
		CrossingReservations.STATUS_ACTIVE,
	)
	assert_eq(
		_reservations.request(&"crossing_1", 3, 0),
		CrossingReservations.STATUS_QUEUED,
	)
	assert_eq(
		_reservations.request(&"crossing_1", 4, 0),
		CrossingReservations.STATUS_QUEUED,
	)
	assert_eq(
		_reservations.request(&"crossing_1", 5, 0),
		CrossingReservations.STATUS_REJECTED,
	)
	assert_true(_reservations.should_ai_traffic_yield(&"crossing_1"))
	assert_eq(_reservations.max_queue_length_observed(), 2)


## Expires active overlap and queued wait at their configured hard bounds.
func test_wait_and_overlap_expire_without_leaking_claims() -> void:
	assert_eq(
		_reservations.request(&"crossing_0", 1, 0),
		CrossingReservations.STATUS_ACTIVE,
	)
	assert_eq(
		_reservations.request(&"crossing_1", 2, 0),
		CrossingReservations.STATUS_QUEUED,
	)
	_reservations.advance(5)
	assert_eq(_reservations.status(1), CrossingReservations.STATUS_NONE)
	assert_eq(_reservations.status(2), CrossingReservations.STATUS_ACTIVE)
	assert_lte(
		_reservations.max_overlap_observed(),
		_reservations.max_overlap_ticks(),
	)
	_reservations.advance(10)
	assert_eq(_reservations.status(2), CrossingReservations.STATUS_NONE)
	assert_lte(
		_reservations.max_queue_age_observed(),
		_reservations.max_wait_ticks(),
	)
