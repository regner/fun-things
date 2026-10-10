class_name FakeHudSource
extends Node
## Supplies observable read-only HUD source contracts without gameplay ownership.

signal changed(view: Dictionary)

var snapshot: Dictionary = {}
var read_count: int = 0
var write_count: int = 0


## Returns the retained owner snapshot while recording a presentation read.
func view() -> Dictionary:
	read_count += 1
	return snapshot


## Publishes an owner-side snapshot through the same immutable-view signal contract.
func publish(next_snapshot: Dictionary) -> void:
	snapshot = next_snapshot.duplicate(true)
	changed.emit(snapshot)


## Represents a gameplay mutation API that presentation must never call.
func write_gameplay_state() -> void:
	write_count += 1
