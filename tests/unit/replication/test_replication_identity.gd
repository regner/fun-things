extends GutTest
## Verifies session, sender, participant, entity, and generation identity fences.


## Creates canonical fresh session IDs and rejects alternate text spellings.
func test_session_identity_is_exact_and_fresh() -> void:
	var first: String = ReplicationIdentity.create_session_id()
	var second: String = ReplicationIdentity.create_session_id()

	assert_true(ReplicationIdentity.is_valid_session_id(first))
	assert_true(ReplicationIdentity.is_valid_session_id(second))
	assert_ne(first, second)
	assert_false(ReplicationIdentity.is_valid_session_id(first.to_upper()))
	assert_false(ReplicationIdentity.is_valid_session_id(first.left(31)))


## Mirrors Session identities and rejects stale participant reuse after reconnect.
func test_peer_registry_fences_stale_identity_after_reconnect() -> void:
	var registry := PeerIdentityRegistry.new()
	var first: Dictionary = registry.bind_peer(41, 7)

	assert_true(first.ok)
	assert_eq(registry.resolve_sender(41), 7)
	assert_eq(registry.resolve_sender(999), 0)

	registry.remove_peer(41)
	assert_false(registry.bind_peer(41, 7).ok)
	assert_true(registry.bind_peer(41, 8).ok)
	assert_eq(registry.resolve_sender(41), 8)


## Advances generation before reuse and leaves retired references stale.
func test_entity_generation_prevents_reference_reuse() -> void:
	var tracker := EntityGenerationTracker.new()
	var first_result: Dictionary = tracker.allocate()
	var first: Dictionary = first_result.entity_ref

	assert_true(first_result.ok)
	assert_true(tracker.is_current(first))
	assert_true(tracker.retire(first))
	assert_false(tracker.is_current(first))

	var replacement_result: Dictionary = tracker.reuse(first.id)
	var replacement: Dictionary = replacement_result.entity_ref
	assert_true(replacement_result.ok)
	assert_eq(replacement.id, first.id)
	assert_eq(replacement.generation, first.generation + 1)
	assert_true(tracker.is_current(replacement))
	assert_false(tracker.is_current(first))


## Accepts exactly the final match reference and specifically rejects the next reuse.
func test_entity_generation_enforces_match_spawned_reference_ceiling() -> void:
	const POOL_SIZE: int = 258
	var tracker := EntityGenerationTracker.new()
	var active_refs: Array[Dictionary] = []
	for _index: int in POOL_SIZE:
		var allocated: Dictionary = tracker.allocate()
		assert_true(allocated.ok)
		active_refs.append(allocated.entity_ref)

	var cursor: int = 0
	while tracker.spawned_reference_count() < EntityGenerationTracker.MAX_SPAWNED_REFERENCES:
		var slot: int = cursor % POOL_SIZE
		var retired: Dictionary = active_refs[slot]
		if not tracker.retire(retired):
			fail_test("expected active reference at boundary slot %d" % slot)
			return
		var reused: Dictionary = tracker.reuse(int(retired.id))
		if not reused.ok:
			fail_test("unexpected early reference refusal: %s" % reused)
			return
		active_refs[slot] = reused.entity_ref
		cursor += 1

	assert_eq(
		tracker.spawned_reference_count(),
		EntityGenerationTracker.MAX_SPAWNED_REFERENCES,
	)
	assert_true(tracker.retire(active_refs[0]))
	var refused: Dictionary = tracker.reuse(int(active_refs[0].id))
	assert_false(refused.ok)
	assert_eq(refused.failure.code, &"SPAWNED_REFERENCE_LIMIT")


## Rejects malformed references and stale session or match envelopes.
func test_identity_validators_reject_out_of_range_shapes() -> void:
	var session_id: String = ReplicationIdentity.create_session_id()
	assert_true(ReplicationIdentity.is_valid_entity_ref({ "id": 1, "generation": 1 }))
	assert_false(ReplicationIdentity.is_valid_entity_ref({ "id": 0, "generation": 1 }))
	assert_false(ReplicationIdentity.is_valid_entity_ref({ "id": 1, "generation": 0 }))
	var extended_ref: Dictionary = { "id": 1, "generation": 1, "extra": true }
	assert_false(ReplicationIdentity.is_valid_entity_ref(extended_ref))
	assert_true(ReplicationIdentity.is_current_envelope(session_id, 2, session_id, 2))
	assert_false(ReplicationIdentity.is_current_envelope(session_id, 1, session_id, 2))
