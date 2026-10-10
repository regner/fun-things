extends GutTest
## Verifies saved Match composition and host player wiring without changing standalone ownership.

const MATCH_SCENE: PackedScene = preload("res://scenes/match/match.tscn")


## Keeps replication outside authored content roots and spawns host at the first anchor.
func test_saved_replication_root_configures_host_player_and_local_rig() -> void:
	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match)
	var replication: MatchReplication = match.get_node("Replication") as MatchReplication
	var rig: LocalRig = match.get_node("LocalRig") as LocalRig
	var spawn: Marker3D = match.get_node("Anchors/PlayerSpawns/Spawn01") as Marker3D

	assert_eq(replication.get_parent(), match)
	assert_false(replication.is_ancestor_of(match.get_node("World")))
	assert_false(replication.is_ancestor_of(match.get_node("Anchors")))
	assert_true(
		replication.configure_network(ReplicationIdentity.create_session_id(), 1, true)
	)
	var actor: ActorMotion = replication.actor_for_participant(1)
	assert_not_null(actor)
	assert_eq(replication.player_count(), 1)
	assert_eq(rig.controlled_actor(), actor)
	assert_almost_eq(actor.global_position.x, spawn.global_position.x, 0.001)
	assert_not_null(actor.get_node_or_null("PresentationAnchor/Visuals/Model"))


## Mirrors a Session-owned remote sender without allocating another participant identity.
func test_host_accepts_current_session_peer_mapping_once() -> void:
	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match)
	var replication: MatchReplication = match.get_node("Replication") as MatchReplication
	assert_true(
		replication.configure_network(ReplicationIdentity.create_session_id(), 1, true)
	)

	assert_true(replication.admit_peer(42, 2))
	assert_true(replication.admit_peer(42, 2))
	assert_false(replication.admit_peer(42, 3))
