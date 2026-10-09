class_name S05Replication
extends S03Replication
## Adds scoped fire/current-car/live-event methods to the existing S03 RPC writer.

signal fire_result(reason: String)

const MAX_FIRE_BYTES: int = 512
const FIRE_BURST: int = 4
const FIRE_RATE: float = 4.0
const MAX_CUT_BYTES: int = 8192

var fire_rates: Dictionary = {}
var max_car_bytes: int = 0
var max_fire_bytes: int = 0
var live_received: int = 0
var duplicate_live_rejected: int = 0


## Sends only primitive fire intent; target, damage and ShotId allocation stay on host.
func send_fire(envelope: Variant) -> void:
	_fire.rpc_id(1, envelope)


## Resolves sender before allocating rate state or validating admitted fire intent.
@rpc("any_peer", "call_remote", "reliable", 0)
func _fire(envelope: Variant) -> void:
	if not multiplayer.is_server():
		return

	var peer: int = multiplayer.get_remote_sender_id()
	var participant: int = int(resolve_participant.call(peer))
	if participant == 0:
		return

	var bytes: int = var_to_bytes(envelope).size()
	max_fire_bytes = maxi(max_fire_bytes, bytes)
	var reason: String = "RATE_LIMIT"
	if _permit(peer):
		reason = "INVALID"
		if bytes <= MAX_FIRE_BYTES:
			reason = (match_state as S05Match).submit_fire(participant, envelope)

	_fire_result.rpc_id(peer, reason)


## Bounds requests to one token bucket per inherited sender mapping and no queue.
func _permit(peer: int) -> bool:
	if not fire_rates.has(peer):
		fire_rates[peer] = { "tokens": float(FIRE_BURST), "time": Time.get_ticks_msec() }

	var bucket: Dictionary = fire_rates[peer]
	var now: int = Time.get_ticks_msec()
	bucket.tokens = minf(FIRE_BURST, bucket.tokens + (now - bucket.time) * FIRE_RATE / 1000.0)
	bucket.time = now
	if bucket.tokens < 1.0:
		return false

	bucket.tokens -= 1.0
	return true


## Reports rejection/acceptance without creating another authoritative state writer.
@rpc("authority", "call_remote", "reliable", 0)
func _fire_result(reason: String) -> void:
	fire_result.emit(reason)


## Publishes a bounded complete current cut only to already admitted participants.
func publish_cars(cut: Dictionary) -> void:
	max_car_bytes = maxi(max_car_bytes, JSON.stringify(cut).to_utf8_buffer().size())
	assert(max_car_bytes <= MAX_CUT_BYTES)
	for peer: int in multiplayer.get_peers():
		var participant: int = int(resolve_participant.call(peer))
		if match_state.bindings.has(participant) and match_state.bindings[participant].admitted:
			_cars.rpc_id(peer, cut)


## Applies current life/collision rows atomically on the sole reliable state stream.
@rpc("authority", "call_remote", "reliable", 1)
func _cars(cut: Dictionary) -> void:
	if JSON.stringify(cut).to_utf8_buffer().size() <= MAX_CUT_BYTES:
		(match_state as S05Match).apply_cars(cut)


## Publishes one bounded live event only to admitted participants.
func publish_blast(event: Dictionary) -> void:
	for peer: int in multiplayer.get_peers():
		var participant: int = int(resolve_participant.call(peer))
		if match_state.bindings.has(participant) and match_state.bindings[participant].admitted:
			_blast.rpc_id(peer, event)


## Consumes bounded live receipts only after current-state installation; no future queue.
@rpc("authority", "call_remote", "reliable", 1)
func _blast(event: Dictionary) -> void:
	if var_to_bytes(event).size() > MAX_FIRE_BYTES:
		return

	var state: S05Match = match_state as S05Match
	if state.effects.consume(event, state.damage.revision, state.damage.tick):
		live_received += 1
	else:
		duplicate_live_rejected += 1


## Drops disconnected request buckets alongside inherited baseline/held work.
func forget(peer: int) -> void:
	fire_rates.erase(peer)
	super.forget(peer)


## Clears pending scoped network state with the inherited attempt lifecycle.
func clear() -> void:
	fire_rates.clear()
	super.clear()
