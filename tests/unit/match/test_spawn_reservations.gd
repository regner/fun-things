extends GutTest
## Verifies atomic bounded spawn claims reject overlap and release cleanly.


## Prevents same-tick candidates from sharing clearance while allowing later reuse.
func test_overlapping_claims_conflict_until_owner_releases() -> void:
	var reservations := SpawnReservations.new()
	assert_true(reservations.reserve(1, &"spawn/a", Vector3.ZERO, 0.45))
	assert_false(reservations.reserve(2, &"spawn/b", Vector3(0.5, 0.0, 0.0), 0.45))
	assert_true(reservations.reserve(2, &"spawn/c", Vector3(2.0, 0.0, 0.0), 0.45))
	assert_eq(reservations.count(), 2)

	reservations.release(1)
	assert_true(reservations.reserve(3, &"spawn/b", Vector3(0.5, 0.0, 0.0), 0.45))
	reservations.clear()
	assert_eq(reservations.count(), 0)


## Rejects malformed and duplicate-owner claims without consuming capacity.
func test_invalid_or_duplicate_claims_do_not_mutate_reservations() -> void:
	var reservations := SpawnReservations.new()
	assert_false(reservations.reserve(0, &"spawn/a", Vector3.ZERO, 0.45))
	assert_false(reservations.reserve(1, &"", Vector3.ZERO, 0.45))
	assert_true(reservations.reserve(1, &"spawn/a", Vector3.ZERO, 0.45))
	assert_false(reservations.reserve(1, &"spawn/b", Vector3(3.0, 0.0, 0.0), 0.45))
	assert_eq(reservations.count(), 1)
