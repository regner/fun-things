class_name S05SavedMatch
extends S05Match
## Coordinates saved cosmetic slots and injects unchanged car pose references.


## Binds authored descendants before existing live-event signals are connected.
func _ready() -> void:
	var saved_slots: Array[Node3D] = []
	var saved_bodies: Array[S05Car] = []
	for slot: Node3D in $Presentation/Slots.get_children():
		saved_slots.append(slot)

	for body: S05Car in $Cars.get_children():
		saved_bodies.append(body)

	($Presentation as S05SavedPresentation).bind(saved_slots, saved_bodies)
	super._ready()
