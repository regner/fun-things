extends S04Replication
## Records actual producer output; admission and pose rules remain inherited unchanged.

var sent: Array[Dictionary] = []


## Observes outgoing intent at its public boundary without requiring a peer connection.
func send_held(envelope: Dictionary) -> void:
	sent.append(envelope.duplicate(true))
