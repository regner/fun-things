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


## Resolves participants from native senders and never from claimed payload identity.
func test_peer_registry_allocates_fresh_identity_after_reconnect() -> void:
	var registry := PeerIdentityRegistry.new()
	var first: Dictionary = registry.admit_peer(41)

	assert_true(first.ok)
	assert_eq(registry.resolve_sender(41), first.participant_id)
	assert_eq(registry.resolve_sender(999), 0)

	registry.remove_peer(41)
	var reconnect: Dictionary = registry.admit_peer(41)
	assert_true(reconnect.ok)
	assert_gt(reconnect.participant_id, first.participant_id)


## Advances generation before reuse and leaves retired references stale.
func test_entity_generation_prevents_reference_reuse() -> void:
	var tracker := EntityGenerationTracker.new()
	var first: Dictionary = tracker.allocate()

	assert_true(tracker.is_current(first))
	assert_true(tracker.retire(first))
	assert_false(tracker.is_current(first))

	var replacement: Dictionary = tracker.reuse(first.id)
	assert_eq(replacement.id, first.id)
	assert_eq(replacement.generation, first.generation + 1)
	assert_true(tracker.is_current(replacement))
	assert_false(tracker.is_current(first))


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
